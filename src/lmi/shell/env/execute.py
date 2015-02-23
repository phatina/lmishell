import sys
from lmi.shell import con
from lmi.shell import obj


def make_shell_local_ns(local_ns=None):
    '''
    Returns a dictionary containing LMIShell locals (such as connect(),
    LMIInstance, etc).  If local_ns is provided, then user defined locals are
    extended with LMIShell ones.
    '''
    if local_ns is None:
        local_ns = dict()

    # TODO:  Add all missing symbols
    local_ns.update({
        'LMIClass': obj.LMIClass,
        'LMIInstance': obj.LMIInstance,
        'LMIInstanceName': obj.LMIInstanceName,
        'LMINamespace': obj.LMINamespace,
        'connect': con.connect
    })
    return local_ns


def exec_code(code, local_ns=None):
    '''
    Executes a compiled byte-code.
    '''
    local_ns = make_shell_local_ns(local_ns)
    exit_code = None

    try:
        # Execute the code
        exec(code, local_ns)
    except SystemExit as e:
        exit_code = e.args[0]
    except:
        # Catch all the exceptions. One frame is omitted, because we don't want
        # to flood the stack trace with internal calls from LMIShell.
        o = sys.excepthook
        save_tb_offset = o.tb_offset
        o.tb_offset = 1
        o(sys.exc_info())
        o.tb_offset = save_tb_offset

    return local_ns, exit_code


def exec_command(command, local_ns=None):
    '''
    Executes a script passed in as string.
    '''
    code = compile(command, 'module', 'exec')
    return exec_code(code, local_ns)


def exec_script(args, local_ns=None):
    '''
    Executes a script with filename and returns its locals.
    '''
    filename = args[0]

    # Save old CLI arguments
    save_argv = sys.argv
    sys.argv = args


    with open(filename, 'r') as fin:
        code = compile(fin.read(), filename, 'exec')
        local_ns, exit_code = exec_code(code, local_ns)

    # Restore CLI arguments
    sys.argv = save_argv

    return local_ns, exit_code
