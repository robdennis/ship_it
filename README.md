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
