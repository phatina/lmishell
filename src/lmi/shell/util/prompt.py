import sys
import getpass
import readline

from lmi.shell.logger import logger


def prompt_input(prompt, echo=True):
    '''
    Reads a string from the standard input.
    '''
    if not sys.stderr.isatty() and not sys.stdout.isatty():
        logger.warn(
            'Both stdout and stderr are detached from terminal, '
            'using stdout for prompt')
    elif not sys.stdout.isatty() and sys.stderr.isatty():
        # read the input with prompt printed to stderr
        stream = sys.stderr
    else:
        # read the input with prompt printed to stdout
        stream = sys.stdout

    # Define input function
    if echo:
        def get_input(prompt):
            return raw_input(prompt)
    else:
        def get_input(prompt):
            return getpass.getpass(prompt, stream)

    try:
        result = get_input(prompt)
    except EOFError, e:
        stream.write('\n')
        return None
    except KeyboardInterrupt, e:
        raise e

    if result and echo:
        cur_hist_len = readline.get_current_history_length()
        if cur_hist_len > 1:
            readline.remove_history_item(cur_hist_len - 1)

    return result
