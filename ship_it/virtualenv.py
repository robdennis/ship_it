# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import sys
from os import path
from pipes import quote

# this is to more easily mock for unittest
import fabric.api as fapi


logger = logging.getLogger(__name__)


def validate_paths(virtualenv_path, requirements_file):
    assert path.isabs(virtualenv_path)
    assert path.isabs(requirements_file) and path.isfile(requirements_file)


def get_virtualenv():
    assert sys.executable, "can't infer python executable path"
    return '{} -m virtualenv'.format(quote(sys.executable))


def build_virtualenv(virtualenv_path, requirements_file):
    validate_paths(virtualenv_path, requirements_file)
    # in case there's relevant escape characters
    venv_path = quote(virtualenv_path)
    req_file = quote(requirements_file)

    if path.exists(virtualenv_path):
        fapi.local('rm -rf {}'.format(venv_path))

    fapi.local('{virtualenv} {location}'.format(virtualenv=get_virtualenv(),
                                                location=venv_path))

    # this should ensure everything is installed, and respect any environment
    # variables that fabric was invoked with (notably custom paths)
    fapi.local('{location}/bin/pip install -r {req}'.format(location=venv_path,
                                                            req=req_file))


def patch_virtualenv(virtualenv_path, destination_path):
    """
    Patch the virtualenv we built to be relocatable and

    :param virtualenv_path: the local path to you virtualenv
    :param destination_path: the path you expect it to be in the resulting
        system
    """
    remove_prelink_if_applicable(virtualenv_path)

    fapi.local('{virtualenv} --relocatable {local_path}'.format(
        virtualenv=get_virtualenv(), local_path=quote(virtualenv_path)
    ))

    # the activate script isn't handled by doing --relocatable
    fapi.local("sed -i 's:{local}:{dest}:' {local_activate}".format(
        local=virtualenv_path, dest=destination_path,
        local_activate=quote(path.join(virtualenv_path, 'bin', 'activate'))))


def remove_prelink_if_applicable(virtualenv_path):
    """
    Packaging a virtualenv has issues if you prelink the executables. Ideally,
    Prelink would be uninstalled on the system, but if it is, we need to undo
    it for our python.
    """
    try:
        fapi.local('prelink -u {}'.format(quote(path.join(virtualenv_path,
                                                          'bin', 'python'))))
    except:
        # We're assuming that if it didn't work, then prelink must not be
        # installed, or at least not relevant for us.
        logger.debug('prelink not undone due to error', exc_info=True)
