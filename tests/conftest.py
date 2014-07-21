# coding=utf-8
from __future__ import unicode_literals

import mock
import pytest

import fabric.api
from ship_it.manifest import Manifest


@pytest.fixture
def mock_local():
    return mock.MagicMock()


@pytest.fixture(autouse=True)
def patch_local(monkeypatch, mock_local):
    monkeypatch.setattr(fabric.api, 'local', mock_local)


@pytest.fixture
def manifest():
    return Manifest('/test_dir/manifest.yaml', manifest_contents=dict(
        version='0.1.0',
        name='ship_it',
    ))


@pytest.fixture
def copy_manifest():
    return Manifest('/test_dir/manifest.yaml', manifest_contents=dict(
        version='0.1.0',
        name='ship_it',
        method='copy',
    ))


@pytest.fixture
def install_manifest():
    return Manifest('/test_dir/manifest.yaml', manifest_contents=dict(
        version='0.1.0',
        name='ship_it',
        method='install',
    ))