# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pipes
from os import path

# imported this way to more easily mock
import invoke

def invoke_fpm(command_line):
    # TODO: this should one be able to support deb
    cmd = 'fpm -f -s dir -t rpm {}'.format(command_line)
    invoke.run(cmd)


def format_flags(flags):
    for flag, value in flags:

        if value not in ('', None):
            # We only want an extra space if was actually something there.
            quoted_value = pipes.quote(str(value))
            quoted_value = ' ' + quoted_value
        else:
            quoted_value = ''

        if not flag or flag.count('-') == len(flag):
            # Is this empty or the whole thing dashes?
            raise ValueError('illegal flag: {!r} in {!r}'.format(flag, flags))

        if flag.startswith('--'):
            if len(flag) == 3:  # --f
                yield '{}{}'.format(flag[1:], quoted_value)
            else:
                yield '{}{}'.format(flag, quoted_value)
        elif flag.startswith('-'):
            if len(flag) == 2:  # -f
                yield '{}{}'.format(flag, quoted_value)
            else:
                # add a dash
                yield '-{}{}'.format(flag, quoted_value)
        else:
            if len(flag) == 1:  # f
                # add a dash
                yield '-{}{}'.format(flag, quoted_value)
            else:  # flag
                # add two dashes
                yield '--{}{}'.format(flag, quoted_value)


def get_command_line(args, flags):
    return '{} {}'.format(' '.join(format_flags(flags)),
                          ' '.join(pipes.quote(arg) for arg in args))
