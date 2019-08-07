"""

JM CLI module - STOP

    Stop jail(s)

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

def stop_jail(name):
    """Stop running jail

    Parameters
    ----------
    name : string
        Name of jail to stop
    """

    jail = jmJail(name, cfg.params)
    jail.load(cfg.params)

    if jail.status() == 1:
        print (f"Jail {jail.name} is not running!")
        return -1

    jail.stop()


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
        """If ALL is used - stop all in shutdown order"""
        order = cfg.shutorder()

        for name in order:
            stop_jail(name)

    else:
        """If it is specified by name - stop this one"""
        if not validate():
            return -1
        
        stop_jail(args.name)


