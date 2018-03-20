Ship It
=======
A dead-simple wrapper for building python applications ``fpm`` that will enforce some best practices.

Build Status
------------
Master: [![Build Status](https://travis-ci.org/robdennis/ship_it.svg?branch=master)](https://travis-ci.org/robdennis/ship_it)[![Coverage Status](https://coveralls.io/repos/robdennis/ship_it/badge.png?branch=master)](https://coveralls.io/r/robdennis/ship_it?branch=master)

Develop: [![Build Status](https://travis-ci.org/robdennis/ship_it.svg?branch=develop)](https://travis-ci.org/robdennis/ship_it)[![Coverage Status](https://coveralls.io/repos/robdennis/ship_it/badge.png?branch=develop)](https://coveralls.io/r/robdennis/ship_it?branch=develop)


How?
====

```
ship_it manifest.yaml
```

What's a Manifest?
==================

defines some additional information that we'll send to ``fpm``

Example
=======

    version: 0.13.0
    name: frufyfru
    before_install: preinstall
    user: root
    group: root
    config_files:
      /etc/frufyfru.conf: examples/frufyfru.conf
    extra_dirs:
      - source: extras/plugins
        target: plugins

Define extra directories
========================

To add directories outside of your python package, use `extra_dirs`.

`extra_dirs` is a list. Items can either be strings or dicts with
'source' and 'target' keys.

All declarations must be relative to the project directory in both
source and target contexts - i.e., you can't copy a folder to an
arbitrary system directory.

If an item is just a string, it will just copy the dir to the top
level of the project directory. If it's a dict, it will copy
"source" to "target," (again, the paths must be relative).
