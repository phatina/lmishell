import argparse
import itertools
import sys
from lmi.shell import __version__


class HelpFormatter(argparse.HelpFormatter):
    '''
    Help formatter.
    '''
    def _format_usage(self, usage, actions, groups, prefix):
        '''
        Returns a string with pre-formatted LMIShell usage.
        '''
        return argparse.HelpFormatter._format_usage(
            self, usage, actions, groups, 'LMIShell v%s\n\n' % __version__)


class OptionsParser(argparse.ArgumentParser):
    '''
    Command line options parser.
    '''

    def get_action(self, option_string):
        '''
        Return an Action object for option_string.
        '''
        for action in self._actions:
            if option_string in action.option_strings:
                return action

    def option_strings(self):
        '''
        Returns a list of all knows option strings.
        '''
        la = [a.option_strings for a in self._actions]
        return list(itertools.chain(*la))

    @staticmethod
    def make_parser():
        '''
        Creates a OptionsParser for LMIShell valid CLI options.
        '''
        parser = OptionsParser(
            usage='%(prog)s [options] script [script-options]',
            formatter_class=HelpFormatter)
        parser.add_argument(
            '-c', '--command', type=unicode, dest='command',
            help='program passed in as string')
        parser.add_argument(
            '-i', '--interact', action='store_true', default=False,
            dest='interact', help='inspect interactively after running a script')
        parser.add_argument(
            '-v', '--verbose', action='store_true', default=False,
            dest='verbose', help='print log messages to stderr')
        parser.add_argument(
            '-m', '--more-verbose', action='store_true', default=False,
            dest='more_verbose', help='print all log messages to stderr')
        parser.add_argument(
            '-q', '--quiet', action='store_true', default=False,
            dest='quiet', help='do not print any log messages to stderr')
        parser.add_argument(
            '-n', '--noverify', action='store_false', default=True,
            dest='verifycert', help='do not verify CIMOM SSL certificate')
        parser.add_argument(
            '--cwd-first-in-path', action='store_true', default=False,
            dest='cwd_first_in_path',
            help='prepend CWD in sys.path instead of appending it')
        return parser


class Options(object):
    '''
    LMIShell options class. Objects of this class are created with one
    parameter; list of CLI arguments. To get their value, use `getattr()`.

    Options
    -------
    command : str
        Program passwd in a string.
    interact : bool
        Inspects interactively after running a script.
    verbose : bool
        Prints log messages to stderr.
    more_verbose : bool
        Print all log messages to stderr.
    quiet : bool
        Do not print any log messages to stderr.
    no_verify : bool
        Do **not** verify CIMOM SSL certificate.
    '''

    def __init__(self, args=sys.argv):
        self.parser = OptionsParser.make_parser()
        self.args, self.script_args = self.split_args(self.parser, args)
        self.options = self.parser.parse_args(self.args[1:])

    def __getattr__(self, name):
        '''
        Returns a parsed attribute.
        '''
        if hasattr(self.options, name):
            return getattr(self.options, name)
        raise AttributeError('Options doesn\'t contain: %s' % name)

    @staticmethod
    def split_args(parser, args):
        '''
        Returns 2 lists of args, where the first one contains LMIShell options
        and the second one is related to *.lmi script.
        '''
        option_strings = parser.option_strings()

        skip = 0
        for i, arg in enumerate(args[1:], 1):
            if skip:
                skip -= 1
                continue

            if arg in option_strings:
                action = parser.get_action(arg)

                if action.nargs is None:
                    skip = 1
                else:
                    # XXX: no implementation for ?, *, +, REMAINDER
                    skip = int(action.nargs)

            if not arg.startswith('-'):
                return args[0:i], args[i:]

        return args, []
