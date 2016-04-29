![GSI Logo](http://www.gsi.dit.upm.es/images/stories/logos/gsi.png)
[DoCon](http://demos.gsi.dit.upm.es/docon) 
==================================

Introduction
---------------------
This tool will take several input formats and translates them to semantic formats. It focuses on translating corpora to the NIF+[Marl](http://gsi.dit.upm.es/ontologies/marl) format, using json-ld.

DoCon is under heavy development. As of this writing, it supports:

* Creating and administrating translation templates (admin level)
* Editing templates to convert traditional formats (csv, tsv, xls, xml) formats to NIF+Marl+Onyx.
* Using the available templates to translate known formats through this portal or via POST requests
* Saving or outputting the result
* HTTP API
* Logging translation requests
* Auto selection of the best template based on the input format

In the future, we might include the following features:
* Conversion of semantic formats
* Automatic translation between semantic formats (e.g. [RDF](http://www.w3.org/RDF/) to [JSON-LD](http://json-ld.org/))

Translating a document
----------------------
Documents can be translated via the Web Interface, through the REST interface, or via Command-Line.

DoCon's endpoint takes these parameters:

 * input (i): The original file to be translated
 * informat (f): The format of the original file
 * intype (t) [Optional]:
    * direct (default)
    * url
    * file
 * outformat (o):
    * json-ld
    * rdfxml
    * turtle (default, to comply with NIF)
    * ntriples
    * trix
 * base URI (u) [Optional]: base URI to use for the corpus
 * prefix (p) [Optional]: prefix to replace the base URI
 * language (l) [Optional]: language code (see dc:terms and [ISO 639](http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) )
 * template (t) [Optional]: ID of the template to use. If it is omitted, a template to convert from informat to outformat will be used, or a template from informat to another format (e.g. json-ld), with automatic conversion (*to be done*).
 * toFile [Optional]: Whether the result should be sent in the response (default) or written to a file. For convenience, this value defaults to False when using the Web Form.

Using the command line tool *curl*, a request can be made like this:

    curl -F"template=Example_to_Marl" -F"input=@input-file.csv" -F"intype=FILE"
        http://demos.gsi.dit.upm.es/docon/process
        > result.jsonld

Templates
---------
DoCon templates are custom jinja2 templates with syntactic sugar, custom preferences and functions to deal with different document types.

For instance, this is a template that prints each cell in a csv file in a separate line, adding a dashed line between rows:

    {% set file = open_file(informat="csv", delimiter=',') %}
    {% for row in file %}
    {% for item in row %}
    {{ item.strip() }}
    {% endfor %}
    {{ "------" if not loop.last }}
    {% endfor %}

This is the alternative and cleaner form of the same template using jinja's line expressions:

    % set file = open_file(informat="csv", delimiter=',') 
    % for row in file 
    % for item in row 
    {{ item.strip() }}
    % endfor 
    {{ "------" if not loop.last }}
    % endfor 

Command-line tool
-----------------
In addition to providing an endpoint, this tool can be used directly in the command line.
Just install the package and run:

    docon -i <file to be converted> --template <conversion template> -o <output>

If you don't want to install the package, you can also run it like a normal python module:

    python -m docon.cli -i <file to be converted> --template <conversion template> -o <output>

Installation instructions
------------------------------
The easy way:

    pip install docon

That will allow you to use the CLI tool right away.
So far, if you want to run the server, you will need to run your own wsgi script or copy wsgi.py from this repository.

To install it from source, follow these steps:

* Copy the docon/settings-private.py.template to docon/settings-private.py
* Add your database information to settings.py
* Create a virtualenv (preferably, in the project root)
* Install the required packages:
```
    pip install -r requirements.txt
```
* Test the environment with:
```
    python manage.py runserver localhost:<PORT>
```

If the standalone server works, you can try serving the portal via apache/nginx and WSGI. It has been tested with apache2 and uwsgi. In that case you will also need to serve the static files from your web server. An example configuration for Apache2 would be:

```
<VirtualHost *:80>

    [ ... ]

    WSGIScriptAlias /docon /path_to_docon/wsgi.py
    WSGIDaemonProcess docon user=www-data group=www-data processes=nprocesses threads=nthreads python-path=/path_to_docon:/path_to_docon/venv/lib/python2.7/site-packages
    WSGIProcessGroup docon
    <Directory /path_to_docon>
    Order allow,deny
    Allow from all
    </Directory>

    Alias /docon/robots.txt /path_to_docon/static/robots.txt
    Alias /docon/favicon.ico /path_to_docon/static/favicon.ico

    AliasMatch ^docon/([^/]*\.css) /path_to_docon/static/styles/$1

    Alias /docon/media/ /path_to_docon/media/
    Alias /docon/static/ /path_to_docon/static/

    <Directory /path_to_docon/static>
    Order deny,allow
    Allow from all
    Options -Indexes
    </Directory>

    <Directory /path_to_docon/media>
    Order deny,allow
    Allow from all
    Options -Indexes
    </Directory>

</VirtualHost>
```

Acknowledgement
---------------
EUROSENTIMENT PROJECT
Grant Agreement no: 296277
Starting date: 01/09/2012
Project duration: 24 months

![Eurosentiment Logo](logo_grande.png)
![FP7 logo](logo_fp7.gif)
