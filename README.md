# What is dude?

**THIS PROJECT IS CURRENTLY A WORK IN PROGRESS**

**dude** (**Dynamic and Uniform Databank Engine**) is a microservice middleware for taking HTTP/JSON requests and renders them in to database queries.

It then can **transform** the returned data and give it back to the caller.

Each **HTTP Endpoint** can have a **POST**, **GET**, **PATCH** and **DELETE** method associated with it.

<img src="./docs/Dude%20-%20Top%20Level.png?raw=true" width="500">

## Dynamic?

The **endpoints** are **data driven**.

In theory these **endpoints** could be **hot reloaded** without having to rebuild and redeploy the code.

## Uniform?

Each **endpoint** is defined in the exact same way.

All follow the same pattern and in theory can all use the same code/classes.

This has the side-effect of making the microservice compact.

## Databank Engine?

Each **dude** in theory could sit in front of **many banks**. These could be different database types such as **MySQL**, **MongoDB** or even something like **Solr** or **Elasticsearch**.

By adding **Database Drivers (drivers)** to **dude** these resources could be changed **transparently** without the application using **dude** knowing the nitty gritty details.

# CRUD

The HTTP/dude methods are:

* POST
* GET
* PATCH
* DELETE

## POST

Posted JSON either be an **object** or **list of objects**.

They query will be executed on the server for every **object**.

The caller should be notified on the success of each object being created. (This should be expanded)

## GET

No JSON.

Query will be executed once.

**List of objects** returned.

**Transforms** are run on the **list of objects**.

## PATCH

Posted JSON either be an **object** or **list of objects**.

They query will be executed on the server for every **object**.

The caller should be notified on the success of each object being updated.

## DELETE

No JSON.

The caller should be notified on the success of DELETE.

# Databanks

# Endpoint

Every **endpoint** implements a **pipeline**.

Each **endpoint** can be thought of as a **HTTP URI**, that runs a query for each object in the **HTTP Request**.

# Domain

A **domain** is a collection of **endpoints** and **databank credentials**.

It hands the primitives of the **pipeline** over to the app.

# The Pipeline

The **pipeline** is made up of three parts (and the methods which use them):

* Imports (POST, GET, PATCH, DELETE)
* Driver (POST, GET, PATCH, DELETE)
* Transforms (GET)

<img src="./docs/Dude%20-%20Pipeline%20Components.png?raw=true" width="500">

# Importers

The **Importers** are classes that ensure the HTTP Requests to the Endpoint are in the right format. If they aren't the process should return an error code.

Only values that are imported are can be used by the **Drivers** and **Transformers**.

## Sources

The following sources are derived from the HTTP Request.

* args (POST, GET, PATCH, DELETE)
* cookies (POST, GET, PATCH, DELETE)
* headers (POST, GET, PATCH, DELETE)
* data (POST, PATCH)

The import should look and feel sorta like this:

```yaml
Imports:
  args:
    # components
  headers:
    # that
  data:
    # specify
  cookies:
    # data format
  form:
    # and values to import
  vars:
    # and some to render
```

## vars

**vars** are similar to **Importers** but they are used to generate data at runtime.

They differ from **Importers** in three key ways:

* They have a **template** member in the component. This is a **Jinja2** template. This is used instead of a value from an above **source**.
* They are always executed after the other imports, this is so that you can use them in your **template** member.
* Their components can either be a **dict** or a **list of dicts**. The keys in a **dict** may be computed in any order. Using a **list of dicts** you can specify the order the vars get generated in.

**Through development I've discovered that templating can be rather slow, I think a faster alternative would be to use the Python 'format' command. Templates should only be used in rare occurences, I reckon with 'format' being the defacto.**

```yaml
  vars:
  - formal:
      template: 'Mr {{ args.first_name }}'
      type: string
  - unlucky_number:
      template: '{{ args.lucky_number / 13 }}'
      type: float
          
```

## Types

The following types will be supported in the first build of the app:

* str
* int
* float
* boolean


In the interest of keeping this first build simple these types will have no further validation. Once the bare bones are in these classes can be refactored to add the validation as desired.

In the future I'd want to add primitives for **date**, **datetime** and **time**.

## boolean

Imports a **boolean** value.

```yaml
Imports:
  args:
    enabled:
      as_false:
      - list
      - of
      - values
      reject:
      - 'this == False'
      type: boolean
```

### as\_false

Takes a **list of values**. If the **value** is the same as one of the **list**, it is treat as False.

This is because **args** and such-like are always passed to dude as **str**'s, and so are always **true** unless they're blank.

This allows the developer to explicitly set what they want to represent **false**.

# Drivers

**Drivers** are the classes that interact with the database on behalf of the **endpoint**. They should implement the **CRUD** (**POST**, **GET**, **PATCH** and **DELETE**) methods.

The endpoint should just be able to handover the **query/parameters** to the **driver** when calling the appropriate method.

* mysql
* mongodb

A Driver represents a **connection** to a **databank**.

It knows how to take the **imported data** and how to **render** (using jinja2) that in to **queries** for the **databank**.

It then uses the **connection** and the **queries** to **exchange** with the **databank**.

<img src="docs/Dude%20-%20Inside%20a%20Driver.png?raw=true" height="300">

# Transformers

**Transformers** transform the output data in to the desired format.

## data

**data** can be an **array** or **object**. If it's an **object** it will be treat an **array** with one element.

**data** iterates over the **driver's** output and transforms each object in to the desired format. Each **object** in the **array** is one pass of transformations.

```yaml
Transforms:
  data:
  - formal: "Sir {{ this.name }}"
    lucky:
      publish: false
      reject:
      - value == 13
      render: "{{ this.age - 13 }}"
      type: int
    name:
      inherit: 'name'
      type: str
    alive:
      type: bool
```

### key: value

If the **type** of **value** is a **str**, it is just rendered using **jinja2**.

If the **type** is a **boolean** set to **true** it **inherits** the **value** from the same **key**.

### inherit

The **key** of the **value** to lift from the previous version of the object.

### publish

**boolean**; Assumed to be **true**, if explicitly set to **false** the key/value pair won't be passed to the HTTP response.

### reject

Is a **list** of **Python expressions**, that are executed sequentially.

If any of the expressions are **true**, then the **data transform** skips for this object and skips to the next one.

The variables passed to reject are:

* `this` - a dict of the object currently being transformed
* `key` - the current key of the value being rendered
* `value` - the value after it has been rendered and its type coerced to the right one.

This will be an **eval** under the covers, which doesn't feel very safe. In future iterations of the program **Importer** methods will be used to check the data is in the right shape.

This is currently as such to simplify the proof of concept version.

### render:

A **jinja2** string to render the value.

### type:

The **type** the value should be.

This is currently locked to the simple types that are representable in JSON (i.e. not lists or objects) - but down the line in further iterations more complex types should be definable - including **date**, **datetime**, **time** or anything else that takes our fancy.

## group

**group** takes a list of **keys** and groups the **objects** them.

**group**'s has a **data** component that is identical to the **data transformer** apart from there are some special purpose **group object** instead of **this** which exposes some methods for getting data from the group.


```yaml
Transforms:
  group:
    keys:
    - name
    data:
    - name: "{{ group.max('created', name) }}"
      man years:
        render: "{{ group.sum('age') }}"
        type: int
      average:
        render: "{{ group.mean('age') }}"
        type: float
```

### group.count()

Returns the number of instances in the **group**.

### group.distinct(key)

Returns the number of **distinct** instances of **object[key]** in the **group**.

### group.max(src, value)
### group.mean(src, value)
### group.min(src, value)
### group.mode(src, value)
### group.median(src, value)

These functions all behave in the same way. It checks all instances of **object[src]** in the **group**.

Returns the **object** whose **src** is the **max**|**mean**|**min**|**mode**|**median**.

If **value** is not set it returns **object[src]**.

If **value** is set it returns the corresponding **object[value]**.

### group.sum(key)

Returns the **total** of all instances in the **group** of **object[key]** added together.

## order

**order** arranges the instances by **key** by the **asc|desc** in **order**.

```yaml
  order:
  - { key: 'name', order: 'asc' }
  - { key: 'age' order: 'desc' }
```

## paginate

**paginate** can limit the output.

```yaml
  paginate:
    limit: "{{ args.limit }}"
    page: "{{ args.page }}"
```

### limit

**jinja2** rendered value that's coerced to an **int**.

Limits the instances returned to this int.

### page

**jinja2** rendered value that's coerced to an **int**.

# Vagrant

**deprecated**

A version of the test environment should run in Vagrant.

# Docker Compose

The test environment should be orchestrated with Docker Compose.

# Unit Tests

To ensure the environment for the unittest is set-up correctly and to run them use the following command from repo root:

```sh
. tests/entrypoint
```

It assumes that the virtualenc `venv` is setup in the project root.

If it isn't this can be created with `requirements.txt`.

```sh
virtualenv -p python3 venv
. venv/bin/activate
pip install -r requirements.txt
``` 

At the very minimum every **Importer**, **Driver** and **Transformer** should be a class and have a unit test around it.

# License

```
Copyright (c) 2019, Myke Atkinson
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of the dude project.
```

