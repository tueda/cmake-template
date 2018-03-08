#!/bin/sh
""":" .

exec python "$0" "$@"
"""

__doc__ = """Bootstrap script."""

import argparse
import os
import re
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


def get_script_path():
    """Return the path to the this script."""
    return __file__


def get_root_dir():
    """Return the CMake/Git root directory."""
    return os.path.dirname(__file__)


def run(args, verbose=False, ignore_error=False, without_check=False,
        return_output=False):
    """Run an external command."""
    if verbose:
        print('Running {0}'.format(' '.join(args)))
        sys.stdout.flush()
    if ignore_error:
        with open(os.devnull, 'w') as devnull:
            return subprocess.call(args, stderr=devnull)
    elif without_check:
        return subprocess.call(args)
    else:
        try:
            if return_output:
                return subprocess.check_output(args)
            else:
                subprocess.check_call(args)
        except subprocess.CalledProcessError:
            exit(1)
        return 0


def cmake_has_target(target):
    """Return True if the current CMake build has the given target."""
    output = run(['cmake', '--build', '.', '--target', 'help'],
                 return_output=True)
    return any(re.search(r'\b{0}\b'.format(re.escape(target)), l)
               for l in output.splitlines())


def command_init(args):
    """Initialize the build."""
    cmake_args = []

    for a in args.args:
        if not a.startswith('-'):
            if a.lower() == 'debug':
                a = '-DCMAKE_BUILD_TYPE=Debug'
            elif a.lower() == 'release':
                a = '-DCMAKE_BUILD_TYPE=Release'
            elif a.lower() == 'native':
                a = '-DENABLE_NATIVE=ON'
            elif a.lower() == 'nonative':
                a = '-DENABLE_NATIVE=OFF'
            elif a.lower() == 'strict':
                a = '-DENABLE_STRICT=ON'
            elif a.lower() == 'nostrict':
                a = '-DENABLE_STRICT=OFF'
            elif a.lower() == 'sanitize':
                a = '-DENABLE_SANITIZER=ON'
            elif a.lower() == 'nosanitize':
                a = '-DENABLE_SANITIZER=OFF'
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

    root_dir = get_root_dir()

    run(['git', '-C', root_dir, 'submodule', 'update', '--init'],
        verbose=args.verbose)

    if args.verbose:
        cmake_args.insert(0, '-L')
    run(['cmake'] + cmake_args + [root_dir], verbose=args.verbose)


def command_clean(args):
    """Clean up the working directory."""
    run(['git', 'submodule', 'deinit', '.'], verbose=args.verbose,
        ignore_error=True)
    run(['git', 'clean', '-dfX'], verbose=args.verbose)


def command_ci_lint(args):
    """Run linters for CI."""
    subcommands = []

    for a in args.args:
        if a.lower() == 'cpp':
            if 'cpp' not in subcommands:
                subcommands.append('cpp')
        elif a.lower() == 'python':
            if 'python' not in subcommands:
                subcommands.append('python')
        else:
            args.error('unknown keyword: {0}'.format(a))

    if not subcommands:
        subcommands.append('cpp')

    script_path = get_script_path()
    verbose_opt = ['-v'] if args.verbose else []
    run(['python', script_path, 'clean'] + verbose_opt, verbose=args.verbose)

    for cmd in subcommands:
        globals()['_command_ci_lint_' + cmd](args)


def _command_ci_lint_cpp(args):
    if args.verbose:
        run(['clang-format', '--version'], verbose=args.verbose)

    # Assume the repository has no changes. Run clang-format and then check
    # git diff.
    root_dir = get_root_dir()
    target_files = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not re.match(
            r'CMakeFiles', d)]
        files = [f for f in files if re.match(
            r'.*\.(?:c|C|c\+\+|cc|cpp|cxx|h|hh|h\+\+|hpp|hxx)$', f)]
        target_files.extend([os.path.join(root, f) for f in files])
    for f in target_files:
        run(['clang-format', '-i', f], verbose=args.verbose)
    status = run(['git', '-C', root_dir, 'diff', '--exit-code'],
                 verbose=args.verbose, without_check=True)
    if status != 0:
        exit(status)


def _command_ci_lint_python(args):
    if args.verbose:
        run(['flake8', '--version'], verbose=args.verbose)

    run(['flake8'], verbose=args.verbose)


def command_ci_test(args):
    """Run tests for CI."""
    script_path = get_script_path()
    verbose_opt = ['-v'] if args.verbose else []

    run(['python', script_path, 'clean'] + verbose_opt, verbose=args.verbose)

    run(['python', script_path, 'init', 'strict', 'debug'] + args.args +
        verbose_opt, verbose=args.verbose)
    run(['cmake', '--build', '.', '--target', 'all'], verbose=args.verbose)
    if cmake_has_target('check'):
        run(['cmake', '--build', '.', '--target', 'check'],
            verbose=args.verbose)

    run(['python', script_path, 'init', 'strict', 'release'] + args.args +
        verbose_opt, verbose=args.verbose)
    run(['cmake', '--build', '.', '--target', 'all'], verbose=args.verbose)
    if cmake_has_target('check'):
        run(['cmake', '--build', '.', '--target', 'check'],
            verbose=args.verbose)
    if cmake_has_target('bench'):
        # We don't perform benchmarks on CI, but ensure they can be built.
        run(['cmake', '--build', 'benchmarks'],
            verbose=args.verbose)

    if cmake_has_target('install'):
        run(['python', script_path, 'init', 'strict', 'release',
            'test-install'] + args.args + verbose_opt, verbose=args.verbose)
        run(['cmake', '--build', '.', '--target', 'install'],
            verbose=args.verbose)


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

    parser_ci_lint = subparsers.add_parser(
        'ci-lint',
        help='run liners for CI'
    )
    parser_ci_lint.set_defaults(handler=command_ci_lint)
    parser_ci_lint.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='verbose output',
    )
    parser_ci_lint.add_argument(
        'args',
        nargs='*',
        help=argparse.SUPPRESS,
    )

    parser_ci_test = subparsers.add_parser(
        'ci-test',
        help='run tests for CI'
    )
    parser_ci_test.set_defaults(handler=command_ci_test)
    parser_ci_test.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='verbose output',
    )
    parser_ci_test.add_argument(
        'args',
        nargs='*',
        help=argparse.SUPPRESS,
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
