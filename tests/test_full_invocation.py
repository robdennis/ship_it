# coding=utf-8
from __future__ import unicode_literals
import os

import mock
import pytest

import ship_it


@mock.patch('ship_it.virtualenv.patch_virtualenv')
@mock.patch('ship_it._package_virtualenv_with_manifest')
@mock.patch('ship_it.validate_path')
@mock.patch('ship_it.cli.invoke_fpm')
@mock.patch('ship_it.Manifest.get_args_and_flags',
            return_value=(['arg'], [('--flag', 'value')]))
@mock.patch('ship_it.cli.get_command_line', return_value='command line')
def test_manifest_calls(mock_cl, mock_get, mock_invoke, mock_val,
                        mock_pack, mock_patch, manifest):
    """
    Does the fpm task do the things we expect in the order we expect?
    """
    mocked_functions = [mock_cl, mock_get, mock_invoke, mock_val,
                        mock_pack, mock_patch]
    assert all(not mocked.called for mocked in mocked_functions)

    with mock.patch('ship_it.get_manifest_from_path', return_value=manifest):
        ship_it.fpm(manifest.path, overridden='flag')

    assert all(mocked.called for mocked in mocked_functions)
    assert mock_val.mock_calls == [mock.call('/test_dir/manifest.yaml')]
    mock_cl.assert_called_once_with(['arg'], [('--flag', 'value'),
                                              ('overridden', 'flag')])
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


class TestCallingTheRightPackaging(object):
    """
    Based on the setup of the manifest, want to call the correct virtualenv
    function.
    """
    @pytest.mark.parametrize('man_fixture', ['manifest', 'install_manifest'])
    @mock.patch('ship_it.virtualenv.install_package_in_virtualenv')
    def test_installing(self, mock_install, request, man_fixture):
        the_manifest = request.getfuncargvalue(man_fixture)
        assert not mock_install.called
        ship_it._package_virtualenv_with_manifest(the_manifest, 'req', 'set')
        mock_install.assert_called_once_with(
            the_manifest.local_virtualenv_path, 'set')

    @mock.patch('ship_it.virtualenv.copy_package_in_virtualenv')
    def test_copying(self, mock_copy, copy_manifest):
        assert not mock_copy.called
        ship_it._package_virtualenv_with_manifest(copy_manifest, 'req', 'set')
        mock_copy.assert_called_once_with(copy_manifest.local_virtualenv_path,
                                          'req',
                                          copy_manifest.local_package_path)
