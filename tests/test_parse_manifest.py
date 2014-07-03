# coding=utf-8
from __future__ import unicode_literals

import pytest
import six
import yaml

@pytest.fixture
def base_manifest_contents():
    return {
        'version': '0.1.0',
        'build_dependencies': ['ruby-gems'],
        'run_dependencies': ['postgresql93-libs'],
    }


@pytest.fixture
def base_manifest():
    return """version: 0.1.0
build_dependencies:
    - ruby-gems
run_dependencies:
    - postgresql93-libs
"""


def test_sanity(base_manifest_contents, base_manifest):
    assert yaml.load(six.StringIO(base_manifest)) == base_manifest_contents