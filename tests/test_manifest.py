# coding=utf-8
from __future__ import unicode_literals

import mock
import os
import pytest

import ship_it
from ship_it.manifest import Manifest, get_manifest_from_path


@pytest.fixture
def manifest_file():
    return """
version: 0.1.0
exclude: '*.pyc'
name: ship_it
after_install: some_script.sh
build_dependencies:
    - ruby-devel == 1.0.0
run_dependencies:
    - python
"""


def test_sanity(tmpdir, manifest_file, manifest):
    """
    Does our mock manifest contents evaluate the same as a file?
    """
    _file = tmpdir.join('manifest.yaml')
    _file.write(manifest_file)
    assert get_manifest_from_path(str(_file)).contents == manifest.contents


@mock.patch('yaml.load')
@mock.patch('ship_it.manifest.Manifest.get_manifest_fobj')
def test_open_for_yaml(mock_fobj, mock_load):
    assert not mock_fobj.called
    assert not mock_load.called
    Manifest('some path')
    mock_fobj.assert_called_once_with(os.path.abspath('some path'))
    mock_load.assert_called_once_with(mock_fobj.return_value)


@pytest.mark.parametrize('path', [
    '/home/test/manifest.yaml',
    '~/manifest.yaml',
    'manifest.yaml',
])
@mock.patch('ship_it.manifest.Manifest.get_manifest_content_from_path')
def test_manifest_normalizes_path(mock_content, path):
    """
    Test that the resulting manifest has the path it came from
    """
    assert not mock_content.called
    _man = Manifest(path)
    mock_content.assert_called_once_with(Manifest.normalize_path(path))
    assert _man.path
    assert os.path.isabs(_man.path)
    assert _man.manifest_dir
    assert os.path.isabs(_man.manifest_dir)
    assert '~' not in _man.path
    assert '~' not in _man.manifest_dir


def test_override_virtualenv_name():
    """
    Test that there's a distinction between name and virtualenv name
    """
    test_man = Manifest('manifest.yaml', manifest_contents=dict(
        name='prefix-ship_it',
        virtualenv_name='ship_it'
    ))
    assert test_man.virtualenv_name == 'ship_it'
    assert test_man.remote_virtualenv_path == '/opt/ship_it'
    assert test_man.name == 'prefix-ship_it'


class TestGettingArgsAndFlags(object):
    """
    Test the specifics of getting command line flags and args from a manifest
    """
    @pytest.mark.parametrize('test_man, expected', [
        # We just set up a bunch of flags with whatever we get
        (dict(name='test'), [('name', 'test')]),
        (dict(version='test'), [('version', 'test')]),
        (dict(iteration='test'), [('iteration', 'test')]),
        (dict(description='test'), [('description', 'test')]),
        # We do do some normalization on some of them
        (dict(before_install='test'), [('before-install', '/test_dir/test')]),
        (dict(after_install='test'), [('after-install', '/test_dir/test')]),
        (dict(before_install='/test'), [('before-install', '/test')]),
        (dict(after_install='/test'), [('after-install', '/test')]),
        # # mix and match
        (dict(after_install='/test', name='test'),
        [('after-install', '/test'), ('name', 'test')]),
    ])
    def test_single_flags(self, manifest, test_man, expected):
        # just test the subset of things we care about
        manifest.contents = test_man
        assert sorted(manifest.get_single_flags()) == sorted(expected)

    @pytest.mark.parametrize('test_cfg, expected_args, expected_flags', [
        # we don't have to return config files
        ({}, [], []),
        # some paths relative to the resulting venv
        ({'etc/settings.py': 'examples/settings.py'},
         ['/test_dir/examples/settings.py=/opt/ship_it/etc/'],
         [('config-files', 'opt/ship_it/etc/settings.py')]),
        # some absolute paths
        ({'/etc/ship_it/settings.cfg': 'packaging/rpm/settings.cfg'},
         ['/test_dir/packaging/rpm/settings.cfg=/etc/ship_it/'],
         [('config-files', 'etc/ship_it/settings.cfg')]),
        # more than one config file
        ({'/etc/ship_it/settings.cfg': 'packaging/rpm/settings.cfg',
          'etc/settings.py': 'examples/settings.py'},
         ['/test_dir/packaging/rpm/settings.cfg=/etc/ship_it/',
          '/test_dir/examples/settings.py=/opt/ship_it/etc/'],
         [('config-files', 'etc/ship_it/settings.cfg'),
          ('config-files', 'opt/ship_it/etc/settings.py')]),
    ])
    def test_config(self, manifest, test_cfg, expected_args, expected_flags):
        """
        Test getting the right arguments and flags from config files.
        """
        manifest.contents.update({'config_files': test_cfg})
        actual_args, actual_flags = manifest.get_config_args_and_flags()
        assert sorted(actual_args) == sorted(expected_args)
        assert sorted(actual_flags) == sorted(expected_flags)

    @pytest.mark.parametrize('test_contents, expected_args, expected_flags', [
        # if nothing else, we include the cfg and single args
        ({},
         ['cfg arg', '/test_dir/build/ship_it=/opt'],
         [('single', 'flag'), ('cfg', 'flag'), ('rpm-user', 'ship_it'),
          ('rpm-group', 'ship_it'), ('directories', '/opt/ship_it')]),
    ])
    @mock.patch('ship_it.manifest.Manifest.get_config_args_and_flags',
                return_value=(['cfg arg'], [('cfg', 'flag')]))
    @mock.patch('ship_it.manifest.Manifest.get_single_flags',
                return_value=[('single', 'flag')])
    def test_get_overall_args(self, mock_single, mock_cfg, manifest,
                              test_contents, expected_args, expected_flags):
        manifest.contents.update(test_contents)
        actual_args, actual_flags = manifest.get_args_and_flags()
        assert sorted(actual_args) == sorted(expected_args)
        assert sorted(actual_flags) == sorted(expected_flags)
