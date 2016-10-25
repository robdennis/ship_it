# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pipes
import re
from os import path

import yaml


def get_manifest_from_path(manifest_path):
    return Manifest(manifest_path)


class Manifest(object):
    """
    Utility class for getting command line arguments and flags out of
    configuration
    """
    def __init__(self, manifest_path=None, manifest_contents=None,
                 pkg_type='rpm', pkg_location='/opt'):
        # we don't currently support other packages, but deb is planned
        assert pkg_type in ('rpm',)
        assert path.isabs(pkg_location)
        self.path = self.normalize_path(manifest_path)
        self.pkg_type = pkg_type
        self.pkg_location = pkg_location

        if not manifest_contents:
            self.contents = self.get_manifest_content_from_path(self.path)
        else:
            self.contents = manifest_contents

    @staticmethod
    def normalize_path(original_path):
        return path.normpath(path.abspath(path.expanduser(original_path)))

    @staticmethod
    def get_manifest_fobj(manifest_path):
        return open(manifest_path, 'rb')

    @staticmethod
    def get_manifest_content_from_path(manifest_path):
        fobj = Manifest.get_manifest_fobj(manifest_path)
        return yaml.load(fobj, Loader=yaml.BaseLoader)

    def get_args_and_flags(self):
        args = [pipes.quote('{}={}'.format(self.local_virtualenv_path,
                                           self.pkg_location))]
        flags = self.get_single_flags()

        # add the package user and group
        flags.extend([('{}-{}'.format(self.pkg_type, name_type),
                       self.virtualenv_name)
                      for name_type in ('user', 'group')])
        flags.append(('directories', self.remote_virtualenv_path))

        cfg_args, cfg_flags = self.get_config_args_and_flags()
        args.extend(cfg_args)
        flags.extend(cfg_flags)
        flags.extend(self.get_dependency_flags())
        flags.extend(self.get_exclude_flags())

        return args, flags

    def get_config_args_and_flags(self):
        args = []
        flags = []
        if not self.contents.get('config_files'):
            return args, flags

        # config files need to be added to both flags and args
        for remote_path, local_path in self.contents['config_files'].items():
            remote_cfg = path.normpath(path.join(self.remote_virtualenv_path,
                                                 remote_path))
            assert path.isabs(remote_cfg)
            local_cfg = path.normpath(path.join(self.manifest_dir, local_path))
            # We'll rely on fpm to error if it's a nonexistent path.
            assert path.isabs(local_cfg)
            # The leading / needs to be omitted here
            flags.append(('config-files', remote_cfg[1:]))
            args.append('{}={}/'.format(pipes.quote(local_cfg),
                                        pipes.quote(path.dirname(remote_cfg))))

        return args, flags

    def get_single_flags(self):

        flags = {
            flag.replace('_', '-'): value
            for flag, value in self.contents.items()
            if flag in ('name', 'version', 'iteration', 'before_install',
                        'after_install', 'description')
        }

        for script_type in ('before-install', 'after-install'):
            script_path = flags.get(script_type)
            if script_path and not path.isabs(script_path):
                flags[script_type] = path.normpath(path.join(self.manifest_dir,
                                                             script_path))

        return list(flags.items())

    def get_bool_value(self, name):
        """
        Get manifest value `name` as a boolean
        """
        return bool(self.contents.get(name, '').lower() in ['true', 'yes', 'on', 'y'])

    def get_dependency_flags(self):
        """
        get all the flags related to dependencies
        """
        return [('depends', dep) for dep in self.contents.get('depends', [])]

    def get_exclude_flags(self):
        """
        Get all the excludes defined in manifest. Optionally add '*.py[co]' and
        '__pycache__' if exclude_compiled is set.
        """
        excludes = set([('exclude', excl) for excl in self.contents.get('exclude', [])])
        if self.get_bool_value('exclude_compiled'):
            excludes |= set([('exclude', excl) for excl in ['*.py[co]', '__pycache__']])
        return excludes

    @property
    def manifest_dir(self):
        return path.dirname(self.path)

    @property
    def name(self):
        return self.contents['name']

    @property
    def upgrade_pip(self):
        return self.get_bool_value('upgrade_pip')

    @property
    def virtualenv_name(self):
        return self.contents.setdefault('virtualenv_name',
                                        self.contents['name'])

    @property
    def local_package_path(self):
        self.contents.setdefault('local_package_path', self.virtualenv_name)
        if not path.isabs(self.contents['local_package_path']):
            return path.abspath(path.join(self.manifest_dir,
                                self.contents['local_package_path']))
        else:
            return self.contents['local_package_path']

    @property
    def local_virtualenv_path(self):
        return path.join(self.manifest_dir, 'build', self.virtualenv_name)


    @property
    def remote_virtualenv_path(self):
        return path.join(self.pkg_location, self.virtualenv_name)

