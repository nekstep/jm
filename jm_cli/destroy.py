"""

JM CLI module - DESTROY

    Destroy an existing jail

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

    if not validate():
        return -1

    """Load jail configuration"""
    jail = jmJail(args.name, cfg.params)
    jail.load(cfg.params)

    if jail.status() == 1:
        print(f"Jail {jail.name} is running as {jail.getid_jid()}!")
        exit -1

    # TODO add -f flag to commandline to avoid this prompt
    if not input(f"Destroy jail {jail.name} [y/N]?") == "y":
        return -1

    """Destroy the jail"""
    jail.destroy()

    """Remove it from config and save"""
    cfg.params.remove_section(jail.name)
    cfg.save()

    print(f"Destroyed {jail.name}")

