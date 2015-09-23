# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from pipes import quote

import mock
import pytest
from tempfile import mkdtemp

from ship_it.virtualenv import VirtualEnvPackager

@pytest.fixture(autouse=True)
def patch_executable(monkeypatch):
    monkeypatch.setattr('sys.executable', '/path/to/python.py')


@pytest.yield_fixture
def mock_build_venv():
    with mock.patch('ship_it.virtualenv.VirtualEnvPackager.build_virtualenv') as _m:
        yield _m


class TestPackage(object):

    @pytest.yield_fixture(autouse=True)
    def do_not_build(self, mock_build_venv):
        yield

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
    def test_copy_package(self, mock_local, venv, pkg_dir, req, expected):

        assert not mock_local.called
        VirtualEnvPackager(venv).copy_package(req, pkg_dir)

        assert mock_local.mock_calls == [mock.call(exp) for exp in expected]

    @pytest.mark.parametrize('venv,setup,expected', [
        ('/local/venv/path', '/local/setup.py',
         '/local/venv/path/bin/python /local/setup.py install'),
    ])
    def test_install_package(self, mock_local, venv, setup, expected):
        assert not mock_local.called
        VirtualEnvPackager(venv).install_package(setup)
        mock_local.assert_called_once_with(expected)

    @pytest.mark.parametrize('venv,req,expected', [
        ('/local/venv/path', '/local/reqs.txt',
         '/local/venv/path/bin/pip install -r /local/reqs.txt'),
    ])
    def test_install_requirements(self, mock_local, venv, req, expected):
        assert not mock_local.called
        VirtualEnvPackager(venv).install_requirements(req)
        mock_local.assert_called_once_with(expected)

    @pytest.mark.parametrize('venv,req,expected', [
        ('/local/venv/path', '/local/reqs.txt',
         '/local/venv/path/bin/pip install .'),
    ])
    def test_pip_install(self, mock_local, venv, req, expected):
        assert mock_local.mock_calls == []
        with mock.patch('ship_it.virtualenv.VirtualEnvPackager.'
                        'install_requirements') as mock_install_reqs:
            VirtualEnvPackager(venv).pip_install_package(req)
            mock_install_reqs.assert_called_once_with(req)
        mock_local.assert_called_once_with(expected)


class TestBuildVirtualEnv(object):

    @pytest.mark.parametrize('exists', [True, False])
    def test_exists(self, exists, mock_local):
        assert not mock_local.called
        with mock.patch('ship_it.virtualenv.path.exists', return_value=exists):
            VirtualEnvPackager('/my/local path/to/venv')

        if exists:
            # We expect that we're going to delete the directory
            rm_rf_call = [mock.call("rm -rf '/my/local path/to/venv'")]
        else:
            # We don't need to do that
            rm_rf_call = []

        assert mock_local.mock_calls == rm_rf_call + [
            mock.call("/path/to/python.py -m virtualenv '/my/local path/to/venv'")
        ]

    @pytest.mark.parametrize('upgrade_pip', [True, False])
    def test_upgrade_pip(self, upgrade_pip, mock_local):
        assert mock_local.mock_calls == []
        pkger = VirtualEnvPackager('/tmp/foo', upgrade_pip)

        if upgrade_pip:
            upgrade_pip_call = [mock.call('/tmp/foo/bin/pip install --upgrade pip')]
        else:
            upgrade_pip_call = []
        assert mock_local.mock_calls == [
            mock.call("/path/to/python.py -m virtualenv /tmp/foo")
        ] + upgrade_pip_call


class TestPatchVirtualEnv(object):

    @pytest.yield_fixture(autouse=True)
    def do_not_build(self, mock_build_venv):
        yield

    def test_with_no_spaces(self, monkeypatch, mock_local):
        monkeypatch.setattr('sys.executable', '/some/python.py')

        local_venv = '/local/venv'
        remote_venv = '/remote/venv'
        pkger = VirtualEnvPackager(local_venv)
        mock_local.reset_mock()
        assert not mock_local.called
        pkger.patch_virtualenv(remote_venv)
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
        pkger = VirtualEnvPackager(local_venv)
        mock_local.reset_mock()
        assert not mock_local.called
        pkger.patch_virtualenv(remote_venv)
        assert mock_local.mock_calls == [
            mock.call("prelink -u '/local path/venv/bin/python'"),
            mock.call("/some/python.py -m virtualenv --relocatable "
                      "'/local path/venv'"),
            mock.call('sed -i "s:/local path/venv:/remote path/venv:" '
                      "'/local path/venv/bin/activate'"),
        ]


@mock.patch('ship_it.virtualenv.logger')
def test_handle_prelink_issue(mock_logger, mock_local, mock_build_venv):
    pkger = VirtualEnvPackager('/tmp')
    mock_local.reset_mock()
    mock_logger.reset_mock()
    assert not mock_local.called
    assert not mock_logger.called
    mock_local.side_effect = Exception
    pkger.remove_prelink_if_applicable()
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
def test_handle_odd_reqfile_paths(req_file_path, valid, mock_build_venv):

    if not valid:
        with pytest.raises(AssertionError):
            VirtualEnvPackager('/tmp').copy_package(req_file_path, '/other/path')
    else:
        VirtualEnvPackager('/tmp').copy_package(req_file_path, '/other/path')

@pytest.mark.parametrize('setup_path, valid', [
    # convenient way to get an absolute path that exists
    (__file__, True),
    (os.path.dirname(__file__), False),
    (os.path.relpath(os.path.dirname(__file__)), False),
    (os.path.relpath(__file__), False),
    ('/some/fake/absolute/path/to/directory', False),
    ('/some/fake/absolute/path/to/setup.py', False)
])
def test_handle_odd_setup_paths(setup_path, valid, mock_build_venv):
    pkger = VirtualEnvPackager('/tmp')
    if not valid:
        with pytest.raises(AssertionError):
            pkger.install_package(setup_path)
    else:
        pkger.install_package(setup_path)
