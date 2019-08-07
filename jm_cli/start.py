"""

JM CLI module - START

    Start jail(s)

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

def start_jail(name):
    """Start jail by name

    Parameters
    ----------
    name : string
        Name of jail to start
    """

    jail = jmJail(name, cfg.params)
    jail.load(cfg.params)

    status = jail.status()

    """If jail is already running - skip it"""
    if status == 1:
        print (f"Jail {jail.name} is already running as {jail.getid_jid()}")
        return -1

    """If jail has pid file but is not actually running - stop it first"""
    if status == 2:
        jail.stop()

    """Create jail.conf and start jail"""
    jail.create_jailconf()
    jail.start()

    print("Started: %s" % jail.getid_jid())


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
        """If meta-keywork ALL is used - start all jails in boot order"""
        order = cfg.bootorder()

        for name in order:
            start_jail(name)

    else:
        """If it is specified by name - start this particular one"""
        if not validate():
            return -1

        start_jail(args.name)


