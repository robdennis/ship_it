# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from pipes import quote

import mock
import pytest

from ship_it import virtualenv

@pytest.fixture(autouse=True)
def patch_executable(monkeypatch):
    monkeypatch.setattr('sys.executable', '/path/to/python.py')


class TestPackage(object):
    @pytest.fixture(autouse=True)
    def make_files_exist_and_be_absolute(self, monkeypatch):
        always_true = lambda *args, **kwargs: True
        monkeypatch.setattr('ship_it.virtualenv.path.isfile', always_true)
        monkeypatch.setattr('ship_it.virtualenv.path.isabs', always_true)

    @pytest.mark.parametrize('venv,req,pkg_dir,expected', [
        ('/local/venv/path', '/local/requirements.txt', '/local/pkg', [
            '/local/venv/path/bin/pip install -r /local/requirements.txt',
            'find /local/pkg -type f -name "*.py[co]" -delete;'
            'find /local/pkg -type d -name "__pycache__" -delete',
            'cp -r /local/pkg /local/venv/path',
        ]),
        # we normalize the package directory to ignore any trailing slashes
        ('/local/venv/path', '/local/requirements.txt', '/local/pkg/', [
            '/local/venv/path/bin/pip install -r /local/requirements.txt',
            'find /local/pkg/ -type f -name "*.py[co]" -delete;'
            'find /local/pkg/ -type d -name "__pycache__" -delete',
            'cp -r /local/pkg /local/venv/path',
        ]),
    ])
    def test_copying_a_packaging_into_virtualenv(self, mock_local, venv,
                                                 pkg_dir, req, expected):

        assert not mock_local.called
        with mock.patch('ship_it.virtualenv._build_virtualenv',
                        return_value=quote(venv)):
            virtualenv.copy_package_in_virtualenv(venv, req, pkg_dir)

        assert mock_local.mock_calls == [mock.call(exp) for exp in expected]

    @pytest.mark.parametrize('venv,setup,expected', [
        ('/local/venv/path', '/local/setup.py',
         '/local/venv/path/bin/python /local/setup.py install'),
    ])
    def test_installing_a_packaging_into_virtualenv(self, mock_local, venv,
                                                    setup, expected):
        assert not mock_local.called
        with mock.patch('ship_it.virtualenv._build_virtualenv',
                        return_value=quote(venv)):
            virtualenv.install_package_in_virtualenv(venv, setup)

        mock_local.assert_called_once_with(expected)


@pytest.mark.parametrize('exists', [True, False])
def test_building_the_virtualenv(exists, mock_local):
    assert not mock_local.called
    with mock.patch('ship_it.virtualenv.path.exists', return_value=exists):
        virtualenv._build_virtualenv('/my/local path/to/venv')

    if exists:
        # We expect that we're going to delete the directory
        rm_rf_call = [mock.call("rm -rf '/my/local path/to/venv'")]
    else:
        # We don't need to do that
        rm_rf_call = []

    assert mock_local.mock_calls == rm_rf_call + [
        mock.call("/path/to/python.py -m virtualenv '/my/local path/to/venv'")
    ]


class TestPatchVirtualEnv(object):
    def test_with_no_spaces(self, monkeypatch, mock_local):
        monkeypatch.setattr('sys.executable', '/some/python.py')

        local_venv = '/local/venv'
        remote_venv = '/remote/venv'
        assert not mock_local.called
        virtualenv.patch_virtualenv(local_venv, remote_venv)
        assert mock_local.mock_calls == [
            mock.call('prelink -u /local/venv/bin/python'),
            mock.call('/some/python.py -m virtualenv '
                      '--relocatable /local/venv'),
            mock.call('sed -i "s:/local/venv:/remote/venv:" '
                      '/local/venv/bin/activate'),
        ]

    def test_with_spaces(self, monkeypatch, mock_local):
        monkeypatch.setattr('sys.executable', '/some/python.py')

        local_venv = '/local path/venv'
        remote_venv = '/remote path/venv'
        assert not mock_local.called
        virtualenv.patch_virtualenv(local_venv, remote_venv)
        assert mock_local.mock_calls == [
            mock.call("prelink -u '/local path/venv/bin/python'"),
            mock.call("/some/python.py -m virtualenv --relocatable "
                      "'/local path/venv'"),
            mock.call('sed -i "s:/local path/venv:/remote path/venv:" '
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

    args = '/some/path', req_file_path, '/other/path'
    if not valid:
        with pytest.raises(AssertionError):
            virtualenv.copy_package_in_virtualenv(*args)
    else:
        virtualenv.copy_package_in_virtualenv(*args)

@pytest.mark.parametrize('setup_path, valid', [
    # convenient way to get an absolute path that exists
    (__file__, True),
    (os.path.dirname(__file__), False),
    (os.path.relpath(os.path.dirname(__file__)), False),
    (os.path.relpath(__file__), False),
    ('/some/fake/absolute/path/to/directory', False),
    ('/some/fake/absolute/path/to/setup.py', False)
])
def test_handle_odd_setup_paths(setup_path, valid):
    if not valid:
        with pytest.raises(AssertionError):
            virtualenv.install_package_in_virtualenv('/some/path', setup_path)
    else:
        virtualenv.install_package_in_virtualenv('/some/path', setup_path)
