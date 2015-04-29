# coding=utf-8
from __future__ import unicode_literals
from os import path

from ship_it.manifest import Manifest, get_manifest_from_path
from ship_it import virtualenv, cli


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

    _package_virtualenv_with_manifest(manifest, requirements_file_path,
                                      setup_py_path)
    virtualenv.patch_virtualenv(manifest.local_virtualenv_path,
                                manifest.remote_virtualenv_path)

    man_args, man_flags = manifest.get_args_and_flags()
    man_flags.extend(overrides.items())
    command_line = cli.get_command_line(man_args, man_flags)

    cli.invoke_fpm(command_line)


def _package_virtualenv_with_manifest(manifest, requirements_file_path,
                                      setup_py_path):
    """
    Given a manifest, package up the virtualenv, either by copying in the
    top-level directory, or by installing it into the virtualenv with:
    ``python setup.py install``. This is determined using the manifest's
    "method" key, with the value "copy." Anything else will be considered an
    install.
    """

    venv = manifest.local_virtualenv_path
    if manifest.contents.get('method') == 'copy':
        virtualenv.copy_package_in_virtualenv(venv, requirements_file_path,
                                              manifest.local_package_path)
    else:
        virtualenv.install_package_in_virtualenv(venv, setup_py_path)


