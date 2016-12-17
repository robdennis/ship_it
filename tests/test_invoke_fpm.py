# coding=utf-8
from __future__ import unicode_literals
import collections
import os.path

import mock
import pytest

from ship_it import fpm, cli, get_version_from_setup_py
from ship_it.manifest import Manifest

# not a fixture to make sure this is never passed down a module level
__here__ = os.path.dirname(__file__)


def test_invoke_with_command_line(mock_local):
    assert not mock_local.called
    cli.invoke_fpm('test')
    mock_local.assert_called_once_with('fpm -f -s dir -t rpm test')


class TestGettingTheCommandLine(object):
    # Using ordered dictionaries for an expected order in tests.
    @pytest.mark.parametrize('flag_list, expected', [
        ([('-f', 1)], ['-f 1']),
        ([('--flag', 1)], ['--flag 1']),
        # We shortcut some flag rules for you and do some normalization.
        ([('--f', 1)], ['-f 1']),
        ([('f', 1)], ['-f 1']),
        ([('flag', 1)], ['--flag 1']),
        ([('-flag', 1)], ['--flag 1']),
        # Multiple flags are fine
        ([('--f1', 'a'), ('--f2', 'b')], ['--f1 a', '--f2 b']),
        # Values can be blank and we don't have a trailing space.
        ([('-f', '')], ['-f']),
        # Values are quoted using normal cli rules
        ([('-f', 'some string')], ["-f 'some string'"]),
        # We raise errors too.
        ([('--', 'a')], ValueError),
        ([('-', 'a')], ValueError),
        ([('', 'a')], ValueError),
    ])
    def test_flags_from_dict(self, flag_list, expected):
        if isinstance(expected, collections.Sequence):
            flag_list = list(cli.format_flags(flag_list))
            assert flag_list == expected
        else:
            with pytest.raises(expected):
                list(cli.format_flags(flag_list))

    @pytest.mark.parametrize('args,flags,expected', [
        (['arg1', 'arg2'], [('--flag', 'value')], '--flag value arg1 arg2')
    ])
    def test_flags_then_args_in_command_line(self, args, flags, expected):
        assert cli.get_command_line(args, flags) == expected


@pytest.fixture
def manifest_path():
    return os.path.join(__here__, 'manifest.yaml')


@pytest.fixture()
def setup_path():
    return os.path.join(__here__, 'setup.py')


@pytest.yield_fixture
def get_manifest_with_no_version(manifest_path):

    no_version = Manifest(manifest_path, manifest_contents=dict(name='ship_it'))

    with mock.patch('ship_it.validate_path'),\
         mock.patch('ship_it.get_manifest_from_path',
                    return_value=no_version) as mocked:
        yield mocked



class TestHandleNoVersionSpecified(object):
    @pytest.fixture
    def manifest_with_no_version(self, manifest_path):
        return Manifest(manifest_path, manifest_contents=dict(name='ship_it'))


    def _run_test(self, manifest_path, manifest):
        with mock.patch('ship_it.validate_path'), \
             mock.patch('ship_it.cli'), \
             mock.patch('ship_it._package_virtualenv_with_manifest'), \
             mock.patch('ship_it.get_version_from_setup_py') as mocked_get, \
                mock.patch('ship_it.get_manifest_from_path',
                           return_value=manifest) as mocked:
            assert not mocked_get.called
            fpm(manifest_path)
            return mocked_get


    def test_no_version_in_the_manifest_will_cause_us_to_check(self, manifest_path, setup_path,
                                                               manifest_with_no_version):
        mocked_get = self._run_test(manifest_path, manifest_with_no_version)
        mocked_get.assert_called_once_with(setup_path)

    def test_version_in_the_manifest_will_not_cause_us_to_check(self, manifest_path, setup_path,
                                                                manifest):
        mocked_get = self._run_test(manifest_path, manifest)
        assert not mocked_get.called



def test_getting_a_version_number_from_the_manifest(setup_path):
    assert get_version_from_setup_py(setup_path) == '0.0.1'
