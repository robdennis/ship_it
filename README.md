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

Options
-------

	name: name of the package
	version: package version
	iteration: package iteration
	epoch: package epoch, should be an integer or 'timestamp' which sets value to Unix timestamp of build
	before_install: path to pre_install script
	after_install: path to post_install script
	description: Package description
	config_files: dictionary of files to be included and their local path
	user: the user to own installed files (defaults to virtualenv_name)
	group: the group to own installed files (defaults to user)
	upgrade_pip: if pip should be upgraded after building virtualenv
	upgrade_wheel: if wheel should be upgraded after building virtualenv
	virtualenv_name: the name of the virtualenv to be built and installed (defaults to name)
	local_package_path: the local path to the package to be installed
	remote_package_path: the remote path for the package to be installed. By default, relative paths are relative to /opt
	depends: list of package dependencies
	method: copy (copy contents to venv), requirements (pip install -r requirements_file), or pip (pip install .). Defaults to setup.py (python setup_file install)


Example
=======

    version: 0.13.0
    name: frufyfru
    before_install: preinstall
    user: root
    group: root
    config_files:
      /etc/frufyfru.conf: examples/frufyfru.conf
