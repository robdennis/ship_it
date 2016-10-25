# coding=utf-8
from __future__ import unicode_literals
import collections
import pytest
from ship_it import cli


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
