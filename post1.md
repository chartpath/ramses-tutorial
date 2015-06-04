Create a REST API in minutes with Python and Ramses
===================================================


Intro:
------

Making an API can be a lot of work. Developers need to handle details like serialization, URL mapping, validation, authentication, authorization, versioning, testing, databases, custom code for models and views, etc. Services like Firebase and Parse exist to make this way easier. Using a Backend-as-a-Service, developers can focus more on building unique user experiences.

Some drawbacks of using third party backend providers include a lack of control over the backend code, inability to self-host, no intellectual property etc. Having control over the code _and_ leveraging the time-saving convenience of a BaaS would be ideal, but most REST API frameworks in the wild still require a lot of boilerplate. One popular example of this would be the awesomely heavy Django Rest Framework. Another great project which requires way less boilerplate and makes building APIs super easy is flask-restless, however it has a hard dependency on Postgres as the only/primary database.

Enter Ramses, a simple way to generate a powerful backend from a YAML file (actually a dialect for REST APIs called [RAML](http://raml.org/)). In this post we'll show you how to go from zero to your own production-ready backend in a few minutes.


Creating a new product API:
---------------------------

### Prerequisites

We assume you are working inside a fresh [virtual Python environment](https://virtualenv.pypa.io/en/latest/), and are running both [elasticsearch](https://www.elastic.co/downloads/elasticsearch) and [postgresql](http://www.postgresql.org/download/) with default configurations. We use [httpie](https://github.com/jakubroztocil/httpie) to interact with the API but you can also use curl or other http clients.

If at any time you get stuck or want to see the final working version of the code for this tutorial, [it can be found here]().

### Scenario: a factory to make (hopefully) delicious pizzas

<img src="https://upload.wikimedia.org/wikipedia/commons/c/c5/FatPizzaShopHumeHwyChullora.JPG" alt="Python Pizzeria" style="float:right;max-width:400px;padding:20px">

We want to create an API for our new pizzeria. Our backend should know about all the different toppings, cheeses, sauces, and crusts that can be used and the different combinations of them that go into making various pizza styles. We also want to be able to do queries to figure out which styles are currently available based on the availability of their ingredients, and to be able to create new pizza styles on the fly.

    $ pip install ramses
    $ pcreate -s ramses_starter pizza_factory

The installer will ask which database backend you want to use. Pick option 1 to use SQLAlchemy ('sqla').

Change into the newly created directory and look around.

    $ cd pizza_factory

Run the built-in server to start interacting with your new backend. All endpoints will be accessible at the URI /api/<endpoint-name>/<endpoint-id>. The server runs on port 6543 by default.

    $ pserve local.ini

Look at api.raml to get an idea of how endpoints are specified.

    #%RAML 0.8
    ---
    title: pizza_factory API
    documentation:
        - title: pizza_factory REST API
          content: |
            Welcome to the pizza_factory API.
    baseUri: http://{host}:{port}/{version}
    version: v1
    mediaType: application/json
    protocols: [HTTP]

    /items:
        displayName: Collection of items
        get:
            description: Get all item
        post:
            description: Create a new item
            body:
                application/json:
                    schema: !include items.json

        /{id}:
            displayName: Collection-item
            get:
                description: Get a particular item
            delete:
                description: Delete a particular item
            patch:
                description: Update a particular item

As you can see, we have a resource called "items" at /api/items which is defined by the schema in items.json.

    $ http :6543/api/items
    HTTP/1.1 200 OK
    Cache-Control: max-age=0, must-revalidate, no-cache, no-store
    Content-Length: 73
    Content-Type: application/json; charset=UTF-8
    Date: Tue, 02 Jun 2015 16:02:09 GMT
    Expires: Tue, 02 Jun 2015 16:02:09 GMT
    Last-Modified: Tue, 02 Jun 2015 16:02:09 GMT
    Pragma: no-cache
    Server: waitress

    {
        "count": 0,
        "data": [],
        "fields": "",
        "start": 0,
        "took": 1,
        "total": 0
    }


Data modelling
--------------

### Schemas!

Schemas describe the structure of data.

We need to create schemata for the different kinds of ingredients that we will make our pizzas from. The default schema from Ramses is a basic example in items.json.

Since we're going to have more than one schema in our project, let's create a new directory and move the default schema into it to keep things clean.

    $ mkdir schemas
    $ mv items.json schemas/
    $ cd schemas/

**Rename items.json to pizzas.json** and open it in a text editor. Then copy its contents into new additional new files in the shcemas directory named _toppings.json_, _cheeses.json_, _sauces.json_, and _crusts.json_.

In each new schema, update the value of the "title" field for the different ingredient categories that are being described (i.e. "title": "Pizza schema", etc.).

Let's edit the **pizzas.json** schema to hook up the ingredients that would go into a given pizza.

Under the "id", "name" and "description" fields, add the following relations to the ingredients:

    "toppings": {
        "required": false,
        "type": "relationship",
        "args": {
            "document": "Topping",
            "ondelete": "NULLIFY",
            "backref_name": "pizza",
            "backref_ondelete": "NULLIFY",
        }
    },
    "cheeses": {
        "required": false,
        "type": "relationship",
        "args": {
            "document": "Cheese",
            "ondelete": "NULLIFY",
            "backref_name": "pizza",
            "backref_ondelete": "NULLIFY",
        }
    },
    "sauce": {
        "required": false,
        "type": "foreign_key",
        "args": {
            "ref_document": "Pizza",
            "ref_column": "pizza.id",
            "ref_column_type": "id_field"
        }
    },
    "crust": {
        "required": true,
        "type": "foreign_key",
        "args": {
            "ref_document": "Pizza",
            "ref_column": "pizza.id",
            "ref_column_type": "id_field"
        }
    }

We also need to do the corresponding thing to each ingredient schema to link the ingredients to the pizza recipes that call for them. In **toppings.json** we need a foreign key to the individual pizza IDs that each topping would be used by (again, put this after "name" and "description"):

    "pizza_id": {
        "required": false,

    }

One thing to note here is that only a crust is _really_ required if you think about it. Maybe you would just call it bread at that point, but let's not get too philosophical.

<img src="https://upload.wikimedia.org/wikipedia/commons/7/7c/Pizza_dough_recipe.jpg" alt="Python Pizzeria" style="float:left;max-width:370px;padding:20px">

Also note the "relationship" field type which designates that the origin model (the one we're defining the relationship field on, pizzas) can have multiple different items of from the ingredient categories it is pointing to (in this case toppings and cheeses). A pizza in our universe can only have one sauce and one crust though.

At this point, our kitchen is almost ready. In order to actually start making pizzas, we need to hook up some API enpoints to access the data models we just created.

Let's open up **api.raml** and replace the old "items" endpoint for each of our real models like so:

    #%RAML 0.8
    ---
    title: pizza_factory API
    documentation:
        - title: pizza_factory REST API
          content: |
            Welcome to the pizza_factory API.
    baseUri: http://{host}:{port}/{version}
    version: v1
    mediaType: application/json
    protocols: [HTTP]

    /pizzas:
        displayName: Collection of pizza styles
        get:
            description: Get all pizza styles
        post:
            description: Create a new pizza style
            body:
                application/json:
                    schema: !include schemas/pizzas.json

        /{id}:
            displayName: A particular pizza style
            get:
                description: Get a particular pizza style
            delete:
                description: Delete a particular pizza style
            patch:
                description: Update a particular pizza style

    /toppings:
        displayName: Collection of ingredients for toppings
        get:
            description: Get all topping ingredients
        post:
            description: Create a topping ingredient
            body:
                application/json:
                    schema: !include schemas/toppings.json

        /{id}:
            displayName: A particular topping ingredient
            get:
                description: Get a particular topping ingredient
            delete:
                description: Delete a particular topping ingredient
            patch:
                description: Update a particular topping ingredient

    /cheeses:
        displayName: Collection of different cheeses
        get:
            description: Get all cheeses
        post:
            description: Create a new cheese
            body:
                application/json:
                    schema: !include schemas/cheeses.json

        /{id}:
            displayName: A particular cheese ingredient
            get:
                description: Get a particular cheese
            delete:
                description: Delete a particular cheese
            patch:
                description: Update a particular cheese

    /sauces:
        displayName: Collection of different sauces
        get:
            description: Get all sauces
        post:
            description: Create a new sauce
            body:
                application/json:
                    schema: !include schemas/sauces.json

        /{id}:
            displayName: A particular sauce
            get:
                description: Get a particular sauce
            delete:
                description: Delete a particular sauce
            patch:
                description: Update a particular sauce

    /crusts:
        displayName: Collection of different crusts
        get:
            description: Get all crusts
        post:
            description: Create a new crust
            body:
                application/json:
                    schema: !include schemas/crusts.json

        /{id}:
            displayName: A particular crust
            get:
                description: Get a particular crust
            delete:
                description: Delete a particular crust
            patch:
                description: Update a particular crust

We can easily create our own ingredients and pizza styles now!

Restart the server and get cooking:

    $ pserve local.ini

Let's start by making a Hawaiian style pizza:

    $ http POST :6543/api/toppings name=ham description="because yum"
    $ 


Initial data
------------

