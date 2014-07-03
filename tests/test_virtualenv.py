# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

import mock
import pytest

from ship_it import virtualenv


@pytest.mark.parametrize('exists', [True, False])
def test_building_virtualenv(monkeypatch, mock_local, exists):
    monkeypatch.setattr('sys.executable', '/path/to/python.py')

    assert not mock_local.called

    with mock.patch('ship_it.virtualenv.path.exists', return_value=exists),\
            mock.patch('ship_it.virtualenv.path.isfile', return_value=True):
        virtualenv.build_virtualenv('/my/local/venv/path',
                                    '/my/local/requirements.txt')

    build_and_install_calls = [
        mock.call('/path/to/python.py -m virtualenv /my/local/venv/path'),
        mock.call('/my/local/venv/path/bin/pip install '
                  '-r /my/local/requirements.txt'),
    ]

    if exists:
        # We expect that we're going to delete the directory
        rm_rf_call = [mock.call('rm -rf /my/local/venv/path')]
    else:
        # We don't need to do that
        rm_rf_call = []

    calls = rm_rf_call + build_and_install_calls

    assert mock_local.mock_calls == calls


@pytest.mark.parametrize('req_file_path, valid', [
    # convenient way to get an absolute path that exists
    (__file__, True),
    (os.path.dirname(__file__), False),
    (os.path.relpath(os.path.dirname(__file__)), False),
    (os.path.relpath(__file__), False),
    ('/some/fake/absolute/path/to/directory', False),
    ('/some/fake/absolute/path/to/requirements.txt', False)
])
def test_handle_odd_reqfile_paths(req_file_path, valid):

    if not valid:
        with pytest.raises(AssertionError):
            virtualenv.build_virtualenv('/some/path', req_file_path)
    else:
        virtualenv.build_virtualenv('/some/path', req_file_path)


def test_patch_virtual_env_with_no_spaces(monkeypatch, mock_local):
    monkeypatch.setattr('sys.executable', '/some/python.py')

    local_venv = '/local/venv'
    remote_venv = '/remote/venv'
    assert not mock_local.called
    virtualenv.patch_virtualenv(local_venv, remote_venv)
    assert mock_local.mock_calls == [
        mock.call('prelink -u /local/venv/bin/python'),
        mock.call('/some/python.py -m virtualenv --relocatable /local/venv'),
        mock.call("sed -i 's:/local/venv:/remote/venv:' "
                  "/local/venv/bin/activate"),
    ]


def test_patch_virtual_env_with_spaces(monkeypatch, mock_local):
    monkeypatch.setattr('sys.executable', '/some/python.py')

    local_venv = '/local path/venv'
    remote_venv = '/remote path/venv'
    assert not mock_local.called
    virtualenv.patch_virtualenv(local_venv, remote_venv)
    assert mock_local.mock_calls == [
        mock.call("prelink -u '/local path/venv/bin/python'"),
        mock.call("/some/python.py -m virtualenv --relocatable "
                  "'/local path/venv'"),
        mock.call("sed -i 's:/local path/venv:/remote path/venv:' "
                  "'/local path/venv/bin/activate'"),
    ]


@mock.patch('ship_it.virtualenv.logger')
def test_handle_prelink_issue(mock_logger, mock_local):
    assert not mock_local.called
    assert not mock_logger.called
    mock_local.side_effect = Exception
    virtualenv.remove_prelink_if_applicable('some path')
    mock_logger.debug.assert_called_once_with(
        'prelink not undone due to error', exc_info=True)
