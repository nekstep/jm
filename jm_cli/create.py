"""

JM CLI module - CREATE

    Create new instance of jail

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
        Subparser to add paratemers to
    """

    p.add_argument('name')
    p.add_argument('-a', '--addr')
    p.add_argument('-i', '--interface')
    p.add_argument('-n', '--hostname')
    p.add_argument('-b', '--boot', default="no")

def validate():
    """Perform basic validation

    Returns
    -------
    boolean
        True if we should proceed
    """

    if args.name in cfg.params.sections():
        print(f"Jail {args.name} already exists!")
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

    """Create jail from parameters"""
    jail = jmJail(args.name, cfg.params)
    jail.create(args)

    """Add new section to config and save"""
    cfg.params[jail.name] = jail.config
    cfg.save()

    print(f"Created {jail.name}")

