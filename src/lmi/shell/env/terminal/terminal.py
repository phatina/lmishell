import re
from IPython.config.loader import Config
from IPython.core.prompts import PromptManager
from IPython.frontend.terminal.embed import InteractiveShellEmbed
from lmi.shell.env.terminal import completer
from lmi.shell.env.terminal.options import Options
from lmi.shell.env.execute import make_shell_local_ns


class InteractiveShell(InteractiveShellEmbed):
    '''
    LMI Interactive Shell.
    '''
    confirm_exit = False
    separate_in=''
    separate_out=''

    def __init__(self, options=None, user_ns=None):
        # Prepare initial configuration variables.
        banner = ''
        exit_msg = ''

        # Configure the interactive shell
        config = Config()
        prompt_config = config.PromptManager
        prompt_config.in_template = '> '
        prompt_config.out_template = '\r'

        super(InteractiveShell, self).__init__(
            config=config,
            banner1=banner,
            exit_msg=exit_msg,
            user_ns=make_shell_local_ns(user_ns))

        self.set_custom_completer(self.complete_lmi)

    def __call__(self, header='', local_ns=None, module=None, dummy=None,
                 stack_depth=1, global_ns=None):
        '''
        Activate the interactive interpreter. This overriden method doesn't
        print out an empty exit message.

        See :py:class:`IPython.frontend.terminal.InteractiveShellEmbed`.
        '''

        # If the user has turned it off, go away
        if not self.embedded_active:
            return

        # Normal exits from interactive mode set this flag, so the shell can't
        # re-enter (it checks this variable at the start of interactive mode).
        self.exit_now = False

        # Allow the dummy parameter to override the global __dummy_mode
        if dummy or (dummy != 0 and self.dummy_mode):
            return

        if self.has_readline:
            self.set_readline_completer()

        # self.banner is auto computed
        if header:
            self.old_banner2 = self.banner2
            self.banner2 = self.banner2 + '\n' + header + '\n'
        else:
            self.old_banner2 = ''

        # Call the embedding code with a stack depth of 1 so it can skip over
        # our call and get the original caller's namespaces.
        self.mainloop(local_ns, module, stack_depth=stack_depth, global_ns=global_ns)

        self.banner2 = self.old_banner2

        # These last lines are different. We don't want to output the exit_msg,
        # if it's empty. exit_msg can't be set to None, because it raises
        # TraitError.
        if self.exit_msg:
            print self.exit_msg

    def init_prompts(self):
        self.prompt_manager = PromptManager(shell=self, config=self.config)
        self.configurables.append(self.prompt_manager)

    def complete_lmi(self, completer_, text):
        '''
        Completes text, if it contains LMI objects.
        '''
        return completer.complete(completer_, self.user_ns, text)
