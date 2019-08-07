"""

JM CLI module - EXEC

    Execute command in specified jail or all running jails

Every CLI module should export two functions:
    parser(p) - to add appropriate parsers to argparse subparser
    run(in_args) - to run the module with relevant parsed arguments

"""

import argparse
import os

import jm_lib.zfs as zfs
from jm_lib.config import jmConfig
from jm_lib.jail import jmJail

args = None
cfg = None

def parser(p):
    """Add options to parser

    Parameters
    ----------
    p : argparse
        Subparser to add paratemers to
    """

    p.add_argument('name')
    p.add_argument('cmd', nargs = argparse.REMAINDER)

def validate():
    """Perform basic validation

    Returns
    -------
    boolean
        True if we should proceed
    """

    if not args.name in cfg.params.sections():
        print(f"Jail {args.name} does not exist!")
        return False

    return True

def exec_jail(name, cmd):
    """Execute command in jail

    Parameters
    ----------
    name : string
        Name of jail
    cmd : list of string
        Command to execute
    """

    """Load selected jail"""
    jail = jmJail(name, cfg.params)
    jail.load(cfg.params)

    """Execute command if jail is running"""
    if jail.status() == 1:
        jail.exec(cmd)

def run(in_args):
    """Main job

    Parameters
    ----------
    in_args
        Result of parsing commandline parameters with argparse
    """

    global args
    global cfg

    args = in_args
    cfg = jmConfig()

    if not cfg.exists:
        print (f"Config {cfg.configfile} absent!")
        return -1

    cfg.load()

    if args.name == "ALL":
        """If meta keyword ALL is used - execute in all running jails"""
        order = cfg.jaillist()

        for name in order:
            exec_jail(name, args.cmd)

    else:
        """If it is a name of the jail - validate and execute"""
        if not validate():
            return -1

        exec_jail(args.name, args.cmd)

