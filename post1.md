Title: Create a REST API in seconds with Python and Ramses

Intro:

Making an API can be a lot of work. Developers need to handle details like serialization, URL mapping, validation, authentication, authorization, versioning, testing, databases, custom code for models and views, etc. Services like Firebase and Parse exist to make this way easier. Using a Backend-as-a-Service, developers can focus more on building unique user experiences.

Some drawbacks of using third party BaaS providers include a lack of control over the backend code, inability to self-host, no intellectual property etc. Having control over the code _and_ leveraging the time-saving convenience of a BaaS would be ideal, but most REST API frameworks in the wild still require a lot of boilerplate. One popular example of this would be the awesomely heavy Django Rest Framework. Another great project which requires way less boilerplate and makes building APIs super easy is flask-restless, however it has a hard dependency on PostgreSQL.

Thankfully the open source ecosystem has been catching up and the ability to avoid thinking about backend details without sacrificing power or flexibility is now possible. Enter Ramses, a simple way to generate a powerful backend from a YAML file.

In this post we'll show you how to go from zero to your own production-ready backend in seconds.

Creating a new product API:

Prerequisites: we assume you are working inside a fresh virtual Python environment, and are running both elasticsearch and postgresql with default configurations. We use httpie to interact with the API but you may also use curl or other http clients.

Scenario: We want to create an API for our new pizzeria. Our backend should know about all the different toppings, cheeses, sauces, and crusts that can be used and the different combinations of them that go into making various pizza styles. We also want to be able to do queries to figure out which styles are currently available based on the availability of their ingredients, and to be able to create new pizza styles on the fly.

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

Now we need to create schemata for the different kinds of ingredients. The default schema is a simple example in items.json. _Rename it to pizzas.json_ and open it in a text editor.



