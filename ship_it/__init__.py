# coding=utf-8
from __future__ import unicode_literals
from os import path

from ship_it.manifest import Manifest, get_manifest_from_path
from ship_it import virtualenv, cli


def validate_path(path_to_check):
    assert path.isabs(path_to_check) and path.isfile(path_to_check)


def fpm(manifest_path, requirements_file_path=None):

    _man = get_manifest_from_path(manifest_path)
    if requirements_file_path is None:
        requirements_file_path = path.join(_man.manifest_dir,
                                           'requirements.txt')

    validate_path(_man.path)
    validate_path(requirements_file_path)

    virtualenv.build_virtualenv(_man.local_virtualenv_path, requirements_file_path)
    virtualenv.patch_virtualenv(_man.local_virtualenv_path,
                                _man.remote_virtualenv_path)

    command_line = cli.get_command_line(*_man.get_args_and_flags())
    cli.invoke_fpm(command_line)