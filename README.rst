sistats
=======

.. image:: https://raw.github.com/marianoguerra/sistats/master/sistats.jpg

why?
----

I need to *collect system stats and send them somewhere else*:sup:`TM`

I wanted to start extracting the stats collection from `glances`_ but the code
was riden with try/except and kind of unpythonic *so I decided to start from scratch*:sup:`TM`

what?
-----

a library (sistats) that gives you system stats and allows to calculate the
variation between two reads and some modules that allow to periodically check
for stats and send them somewhere else

an example of the sistats module:

.. code-block:: python

    import time
    from sistats import *

    cpu  = get_cpu_stats()
    mem  = get_mem_stats()
    net  = get_net_stats()
    disk = get_disk_stats()
    fst  = get_fs_stats()

    platinfo = get_platform_info()

    pretty_print("Platform", platinfo)
    pretty_print("CPU", cpu)
    pretty_print("Memory", mem)
    pretty_print("Net", net)
    pretty_print("Disk", disk)
    pretty_print("File System", fst)

    while True:
        time.sleep(5)

        new_cpu  = get_cpu_stats()
        new_mem  = get_mem_stats()
        new_net  = get_net_stats()
        new_disk = get_disk_stats()
        new_fst  = get_fs_stats()

        cpu_diff  = get_cpu_stats_delta(cpu, new_cpu)
        mem_diff  = get_mem_stats_delta(mem, new_mem)
        net_diff  = get_net_stats_delta(net, new_net)
        disk_diff = get_disk_stats_delta(disk, new_disk)
        fst_diff  = get_fs_stats_delta(fst, new_fst)

        pretty_print("CPU diff", cpu_diff)
        pretty_print("Memory diff", mem_diff)
        pretty_print("Net diff", net_diff)
        pretty_print("Disk diff", disk_diff)
        pretty_print("File System diff", fst_diff)

        cpu  = new_cpu
        mem  = new_mem
        net  = new_net
        disk = new_disk
        fst  = new_fst

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

how to run on windows?
----------------------

* install python 2.7 from python.org
* install psutil from http://www.lfd.uci.edu/~gohlke/pythonlibs/#psutil
* download requests zip and run: python setup.py install 
* download sistats https://github.com/marianoguerra/sistats/zipball/master

license?
--------

LGPL v3 + optional beer for the author
