# coding=utf-8
from __future__ import unicode_literals
import os

import mock
import pytest

import ship_it


@mock.patch('ship_it.virtualenv.patch_virtualenv')
@mock.patch('ship_it.virtualenv.build_virtualenv')
@mock.patch('ship_it.validate_path')
@mock.patch('ship_it.cli.invoke_fpm')
@mock.patch('ship_it.Manifest.get_args_and_flags',
            return_value=(['arg'], {'--flag': 'value'}))
@mock.patch('ship_it.cli.get_command_line', return_value='command line')
def test_manifest_calls(mock_cl, mock_get, mock_invoke, mock_val, mock_build,
                        mock_patch, manifest):
    """
    Does the fpm task do the things we expect in the order we expect?
    """
    mocked_functions = [mock_cl, mock_get, mock_invoke, mock_val, mock_build, mock_patch]
    assert all(not mocked.called for mocked in mocked_functions)

    with mock.patch('ship_it.get_manifest_from_path', return_value=manifest):
        ship_it.fpm(manifest.path)

    assert all(mocked.called for mocked in mocked_functions)
    assert mock_val.mock_calls == [mock.call('/test_dir/manifest.yaml'),
                                   mock.call('/test_dir/requirements.txt')]
    mock_cl.assert_called_once_with(['arg'], {'--flag': 'value'})
    mock_invoke.assert_called_once_with('command line')


@pytest.mark.parametrize('file_path, valid', [
    # convenient way to get an absolute path that exists
    (__file__, True),
    (os.path.dirname(__file__), False),
    (os.path.relpath(os.path.dirname(__file__)), False),
    (os.path.relpath(__file__), False),
    ('/some/fake/absolute/path/to/directory', False),
    ('/some/fake/absolute/path/to/requirements.txt', False)
])
def test_handle_odd_reqfile_paths(file_path, valid):

    if not valid:
        with pytest.raises(AssertionError):
            ship_it.validate_path(file_path)
    else:
        ship_it.validate_path(file_path)