"""

JM CLI module - CONSOLE

    Run shell on specific jail

Every CLI module should export two functions:
    parser(p) - to add appropriate parsers to argparse subparser
    run(in_args) - to run the module with relevant parsed arguments

"""

import argparse
import os

import jm_lib.zfs as zfs
from jm_lib.config import jmConfig
from jm_lib.jail import jmJail

"""Global variables"""
args = None
cfg = None

def parser(p):
    """Add options to parser

    Parameters
    ----------
    p : argparse
        Subparser to add parameters to
    """
    p.add_argument('name')

def validate():
    """Perform basic validation

    Returns
    -------
    boolean
        True if we should proceed
    """

    """Check if jail exists in config file"""
    if not args.name in cfg.params.sections():
        print(f"Jail {args.name} does not exist!")
        return False

    """All ok - proceed"""
    return True


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

    """Load and validate configuration"""
    if not cfg.exists:
        print (f"Config {cfg.configfile} absent!")
        return -1

    cfg.load()

    if not validate():
        return -1

    """Create jmJail object"""
    jail = jmJail(args.name, cfg.params)
    jail.load(cfg.params)

    """Check if jail is running"""
    if not jail.status() == 1:
        print (f"Jail {jail.name} is not running!")
        return -1

    """Start console"""
    jail.console()

