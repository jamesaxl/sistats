sistats
=======

.. image:: https://raw.github.com/marianoguerra/sistats/master/sistats.jpg

why?
----

I need to *collect system stats and send them somewhere else*:sup:`TM`

I wanted to start extracting the stats collection from `glances`_ but the code
was riden with try/except and kind of unpythonic *so I decided to start from scratch*:sup:`TM`

who?
----

marianoguerra

how?
----

to use it you have to decide where are you sending it, you can send it to
the console using the dummy sample ConsoleChecker (in transport.py), to try it::

    python transport.py

you can send it to `mosquitto`_::    

    # python mqtt_transport.py -c <client id here>
    # check python mqtt_transport.py -h for options
    python mqtt_transport.py -c ganesha

you can listen to those events using mqtt_listener::

    # python mqtt_listener.py <client id here>
    # for example
    python mqtt_listener.py ganesha 

to use `mosquitto`_ you should have it running on your system, it sends
the payload as `BSON`_

you can send it to a REST API::

    # check python rest_transport.py -h for options
    python rest_transport.py -c ganesha -u god -p secret -v

you can implement any other transport just subclassing transport.Checker
and implementing the missing methods.

.. _`mosquitto`: http://mosquitto.org/
.. _`BSON`: http://bsonspec.org/
.. _`glances`: https://github.com/nicolargo/glances/

license?
--------

LGPL v3 + optional beer for the author
