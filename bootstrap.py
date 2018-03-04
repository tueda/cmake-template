#!/bin/sh
""":" .

exec python "$0" "$@"
"""

__doc__ = """Bootstrap script."""

import argparse
import os
import subprocess
import sys


# https://stackoverflow.com/a/26379693/9105334
def set_default_subparser(self, name, args=None):
    """Set the default subparser.

    Call after setup, just before parse_args()
    name: is the name of the subparser to call by default
    args: if set is the argument list handed to parse_args()

    , tested with 2.7, 3.2, 3.3, 3.4
    it works with 2.6 assuming argparse is installed
    """
    subparser_found = False
    existing_default = False  # check if default parser previously defined
    for arg in sys.argv[1:]:
        if arg in ['-h', '--help']:  # global help if no subparser
            break
    else:
        for x in self._subparsers._actions:
            if not isinstance(x, argparse._SubParsersAction):
                continue
            for sp_name in x._name_parser_map.keys():
                if sp_name in sys.argv[1:]:
                    subparser_found = True
                if sp_name == name:  # check existance of default parser
                    existing_default = True
        if not subparser_found:
            # If the default subparser is not among the existing ones,
            # create a new parser.
            # As this is called just before 'parse_args', the default
            # parser created here will not pollute the help output.

            if not existing_default:
                for x in self._subparsers._actions:
                    if not isinstance(x, argparse._SubParsersAction):
                        continue
                    x.add_parser(name)
                    break  # this works OK, but should I check further?

            # insert default in first position, this implies no
            # global options without a sub_parsers specified
            if args is None:
                sys.argv.insert(1, name)
            else:
                args.insert(0, name)


argparse.ArgumentParser.set_default_subparser = set_default_subparser


def run(args, verbose=False, ignore_error=False):
    """Run an external command."""
    if verbose:
        print('Running {0}'.format(' '.join(args)))
    if ignore_error:
        with open(os.devnull, 'w') as devnull:
            subprocess.call(args, stderr=devnull)
    else:
        try:
            subprocess.check_call(args)
        except subprocess.CalledProcessError:
            exit(1)


def command_init(args):
    """Initialize the build."""
    cmake_args = []

    for a in args.args:
        if not a.startswith('-'):
            if a.lower() == 'debug':
                a = '-DCMAKE_BUILD_TYPE=Debug'
            elif a.lower() == 'release':
                a = '-DCMAKE_BUILD_TYPE=Release'
            elif a.startswith('gcc'):
                a = [
                    '-DCMAKE_C_COMPILER={0}'.format(a),
                    '-DCMAKE_CXX_COMPILER=g++{0}'.format(a[3:]),
                ]
            elif a.startswith('clang'):
                a = [
                    '-DCMAKE_C_COMPILER={0}'.format(a),
                    '-DCMAKE_CXX_COMPILER=clang++{0}'.format(a[5:]),
                ]
            elif a.startswith('test-install'):
                a = '-DCMAKE_INSTALL_PREFIX={0}'.format(
                    os.path.join(os.getcwd(), '_test_install_prefix'))
            else:
                args.error('unknown keyword: {0}'.format(a))

        if isinstance(a, list):
            cmake_args.extend(a)
        else:
            cmake_args.append(a)

    cmake_src_dir = os.path.dirname(__file__)

    run(['git', '-C', cmake_src_dir, 'submodule', 'update', '--init'],
        verbose=args.verbose)

    if args.verbose:
        cmake_args.insert(0, '-L')
    run(['cmake'] + cmake_args + [cmake_src_dir], verbose=args.verbose)


def command_clean(args):
    """Clean up the working directory."""
    run(['git', 'submodule', 'deinit', '.'], verbose=args.verbose,
        ignore_error=True)
    run(['git', 'clean', '-dfX'], verbose=args.verbose)


def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_init = subparsers.add_parser(
        'init',
        help='initialize the build'
    )
    parser_init.set_defaults(handler=command_init)
    parser_init.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='verbose output',
    )
    parser_init.add_argument(
        'args',
        nargs='*',
        help=argparse.SUPPRESS,
    )

    parser_clean = subparsers.add_parser(
        'clean',
        help='clean up the working directory'
    )
    parser_clean.set_defaults(handler=command_clean)
    parser_clean.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='verbose output',
    )

    parser.set_default_subparser('init')

    def args_error(message):
        parser.exit(status=2, message='{0}: error: {1}\n'.format(
            parser.prog, message))

    args = parser.parse_args()
    args.error = args_error
    args.handler(args)


if __name__ == '__main__':
    main()
