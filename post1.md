Create a REST API in minutes with Pyramid and Ramses
====================================================

#### Contents

* [Intro](#Intro)
* [Bootstrap a new API](#Bootstrap a new API)
* [Data modeling](#Data modeling)
* [Creating endpoints](#Creating endpoints)
* [Initial data](#Initial data)

Foreword
--------

This tutorial is meant for beginners. If you get stuck along the way, try to power through and it will probably click. If there's anything you just don't get or want some help with, email [info@brandicted.com](mailto:info@brandicted.com).


Intro
-----

Making an API can be a lot of work. Developers need to handle details like serialization, URL mapping, validation, authentication, authorization, versioning, testing, databases, custom code for models and views, etc. Services like Firebase and Parse exist to make this way easier. Using a Backend-as-a-Service, developers can focus more on building unique user experiences.

Some drawbacks of using third party backend providers include a lack of control over the backend code, inability to self-host, no intellectual property etc. Having control over the code _and_ leveraging the time-saving convenience of a BaaS would be ideal, but most REST API frameworks in the wild still require a lot of boilerplate. One popular example of this would be the awesomely heavy Django Rest Framework. Another great project which requires way less boilerplate and makes building APIs super easy is flask-restless, however it has a hard dependency on Postgres as the only/primary database.

Enter Ramses, a simple way to generate a powerful backend from a YAML file (actually a dialect for REST APIs called [RAML](http://raml.org/)). In this post we'll show you how to go from zero to your own production-ready backend in a few minutes.


Bootstrap a new product API
---------------------------

### Prerequisites

We assume you are working inside a fresh [virtual Python environment](https://virtualenv.pypa.io/en/latest/), and are running both [elasticsearch](https://www.elastic.co/downloads/elasticsearch) and [postgresql](http://www.postgresql.org/download/) with default configurations. We use [httpie](https://github.com/jakubroztocil/httpie) to interact with the API but you can also use curl or other http clients.

If at any time you get stuck or want to see the final working version of the code for this tutorial, [it can be found here](https://github.com/chrstphrhrt/ramses-tutorial/tree/master/pizza_factory).

### Scenario: a factory to make (hopefully) delicious pizzas

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/FatPizzaShopHumeHwyChullora.JPG/440px-FatPizzaShopHumeHwyChullora.JPG" alt="Python Pizzeria" style="float:right;padding-left:20px">

We want to create an API for our new pizzeria. Our backend should know about all the different toppings, cheeses, sauces, and crusts that can be used and the different combinations of them that go into making various pizza styles.

    $ pip install ramses
    $ pcreate -s ramses_starter pizza_factory

The installer will ask which database backend you want to use. Pick option "1" to use SQLAlchemy.

Change into the newly created directory and look around.

    $ cd pizza_factory

All endpoints will be accessible at the URI /api/endpoint-name/item-id. The built-in server runs on port 6543 by default. Have a read through **local.ini** and see if it makes any sense. Then run the server to start interacting with your new backend.

    $ pserve local.ini

Look at **api.raml** to get an idea of how endpoints are specified.

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

As you can see, we have a resource at /api/items which is defined by the schema in **items.json**.

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


Data modeling
-------------

### Schemas!

Schemas describe the structure of data.

We need to create them for each of the different kinds of ingredients that we will make our pizzas with. The default schema from Ramses is a basic example in **items.json**.

Since we're going to have more than one schema in our project, let's create a new directory and move the default schema into it to keep things clean.

    $ mkdir schemas
    $ mv items.json schemas/
    $ cd schemas/

**Rename items.json to pizzas.json** and open it in a text editor. Then copy its contents into new files in the same directory with the names **toppings.json**, **cheeses.json**, **sauces.json**, and **crusts.json**.

    $ tree
    .
    ├── cheeses.json
    ├── crusts.json
    ├── pizzas.json
    ├── sauces.json
    └── toppings.json

In each new schema, update the value of the `"title"` field for the different kinds of things that are being described (e.g. `"title": "Pizza schema"`, `"title": "Topping schema"` etc.).

Let's edit the **pizzas.json** schema to hook up the ingredients that would go into a given style of pizza.

After the `"description"` field, add the following relations with the ingredients:

    ...
    "toppings": {
        "required": false,
        "type": "relationship",
        "args": {
            "document": "Topping",
            "ondelete": "NULLIFY",
            "backref_name": "pizza",
            "backref_ondelete": "NULLIFY"
        }
    },
    "cheeses": {
        "required": false,
        "type": "relationship",
        "args": {
            "document": "Cheese",
            "ondelete": "NULLIFY",
            "backref_name": "pizza",
            "backref_ondelete": "NULLIFY"
        }
    },
    "sauce_id": {
        "required": false,
        "type": "foreign_key",
        "args": {
            "ref_document": "Sauce",
            "ref_column": "sauce.id",
            "ref_column_type": "id_field"
        }
    },
    "crust_id": {
        "required": true,
        "type": "foreign_key",
        "args": {
            "ref_document": "Crust",
            "ref_column": "crust.id",
            "ref_column_type": "id_field"
        }
    }
    ...

### Relations

We need to do the same for each of the ingredients to link them to the pizza style recipes that call for them. In **toppings.json** and **cheeses.json** we need a `"foreign_key"` field pointing to the specific pizza style that each topping would be used for (again, put this after the `"description"` field):

    ...
    "pizza_id": {
        "required": false,
        "type": "foreign_key",
        "args": {
            "ref_document": "Pizza",
            "ref_column": "pizza.id",
            "ref_column_type": "id_field"
        }
    }
    ...

Then in both **sauces.json** and **crusts.json** we do the _reverse_ (by specifying `"relationship"` fields instead of `"foreign_key"` fields) because these two ingredients are being referenced by the particular instances of the pizza styles that call for them:

    ...
    "pizzas": {
        "required": false,
        "type": "relationship",
        "args": {
            "document": "Pizza",
            "ondelete": "NULLIFY",
            "backref_name": "sauce",
            "backref_ondelete": "NULLIFY"
        }
    }
    ...

For **crusts.json** just make sure to set the value of `"backref_name"` to `"crust"`.

One thing to note here is that only a crust is _really_ required to make a pizza if you think long and hard about it. Maybe we'd have to call it bread at that point, but let's not get too philosophical.

Also note the `"relationship"` field type which designates that the "parent/referenced" model (the one we're defining the relationship field on, i.e. pizzas) can have multiple different items from the kinds of ingredients it is related to (i.e. the "child/referencing" models in this case being toppings and cheeses). A pizza in our universe can only have one sauce and one crust though.

### Backref & ondelete arguments

**To learn about using relational database concepts in detail, refer to the [SQLAlchemy documentation](http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html).** _Very_ briefly:

A `backref` argument tells the database that when one model is referenced by another, the "referencing" model (which has a `foreign_key` field) will also provide access "backwards" to the "referenced" model.

An `ondelete` argument is telling the database that when the instance of a referenced model is deleted, to change the value of the referencing field accordingly. `NULLIFY` means that the value will be set to `null`.


Creating endpoints
------------------

At this point, our kitchen is almost ready. In order to actually start making pizzas, we need to hook up some API endpoints to access the data models we just created.

Let's edit **api.raml** by replacing the default "items" endpoint for each of our resources like so:

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

**Notice the order of endpoint definitions**. `/pizzas` is placed after `/toppings` and `/cheeses` because it relates to them. `/sauces` and `/crusts` are placed after `/pizzas` because they relate to it. If you get any kind of errors about things missing or not being defined when starting the server, check the order of definition.

Now we can create our own ingredients and pizza styles!

Restart the server and get cooking.

    $ pserve local.ini

Let's start by making a Hawaiian style pizza:

    $ http POST :6543/api/toppings name=ham description="extra filthy"
    HTTP/1.1 201 Created...

    $ http POST :6543/api/toppings name=pineapple description="thanks Hawai'i"
    HTTP/1.1 201 Created...

    $ http POST :6543/api/cheeses name=mozzarella description="soft and boring"
    HTTP/1.1 201 Created...

    $ http POST :6543/api/sauces name=tomato description="the usual"

    $ http POST :6543/api/crusts name=plain description="just normal white dough"
    HTTP/1.1 201 Created...

    $ http POST :6543/api/pizzas name=hawaiian description="old school ham and pineapple ftw" toppings=[1,2] cheeses=1 sauce=1 crust=1

#### Voila!

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Hawaiian_pizza.jpg/660px-Hawaiian_pizza.jpg" alt="Hawaiian Pizza">

Here it is in all its greasy glory:

    $ 


Initial data
------------

The last step for bonus points is to import a bunch of existing ingredient records to make building more fun.

