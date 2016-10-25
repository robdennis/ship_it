# coding=utf-8
from __future__ import unicode_literals
from os import path

from ship_it.manifest import Manifest, get_manifest_from_path
from ship_it import cli
from ship_it.virtualenv import VirtualEnvPackager


def validate_path(path_to_check):
    assert path.isabs(path_to_check) and path.isfile(path_to_check)


def fpm(manifest_path, requirements_file_path=None, setup_py_path=None,
        **overrides):
    manifest = get_manifest_from_path(manifest_path)
    if requirements_file_path is None:
        requirements_file_path = path.join(manifest.manifest_dir,
                                           'requirements.txt')
    if setup_py_path is None:
        setup_py_path = path.join(manifest.manifest_dir, 'setup.py')

    validate_path(manifest.path)

    packager = _package_virtualenv_with_manifest(manifest,
                                                  requirements_file_path,
                                                  setup_py_path)

    packager.patch_virtualenv(manifest.remote_virtualenv_path)

    man_args, man_flags = manifest.get_args_and_flags()
    man_flags.extend(overrides.items())
    command_line = cli.get_command_line(man_args, man_flags)

    cli.invoke_fpm(command_line)


def _package_virtualenv_with_manifest(manifest, requirements_file_path,
                                      setup_py_path):
    """
    Given a manifest, package up the virtualenv. The following methods are
    supported via the manifest's `method` setting:

    * copy: copy in the top-level directory
    * requirements: run ``pip install -r requirements_file``
        - useful if requirements_file contains '.' 
    * pip: run ``pip install .``
    * install (default): run ``python setup.py install``
    """

    venv = manifest.local_virtualenv_path
    install_method = manifest.contents.get('method')

    # Buld virtualenv and optionally upgrade pip
    packager = VirtualEnvPackager(venv, manifest.upgrade_pip)

    if install_method == 'copy':
        packager.copy_package(requirements_file_path,
                                manifest.local_package_path)

    elif install_method == 'requirements':
        packager.install_requirements(requirements_file_path)

    elif install_method == 'pip':    
        packager.pip_install_package(requirements_file_path)

    else:
        packager.install_package(setup_py_path)

    return packager

