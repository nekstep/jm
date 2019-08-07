"""

JM CLI module - LIST

    Print out a list of jails

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

    p.add_argument('-b', '--boot', action='store_true')
    p.add_argument('-r', '--running', action='store_true')
    p.add_argument('-s', '--shutdown', action='store_true')

def validate():
    """Perform basic validation

    Returns
    -------
    boolean
        True if we should proceed
    """

    return True

def run_str(value):
    """Get string status for boolean status

    Parameters
    ----------
    value : boolean
        True if jail is running

    Returns
    -------
    string
        String representation of current jail status
    """

    if value:
        return "running"
    else:
        return "stopped"

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

    """Print table header"""
    print("R %-15s %-15s %4s %4s %s" %
            ('NAME', 'IP', 'JID', 'BOOT', 'HOSTNAME'))

    """Prepare array of jails to output depending on options"""
    jlist = []

    if args.boot:
        jlist = cfg.bootorder()
    elif args.shutdown:
        jlist = cfg.shutorder()
    else:
        jlist = cfg.jaillist()

    """Print out list of jails one-by-one"""
    for name in jlist:
        jail = jmJail(name, cfg.params)
        jail.load(cfg.params)

        """Skip if we are only listing running jails and it is not"""
        # TODO use status()
        if args.running and not jail.jid_exists():
            continue

        """Print out jail information"""
        print("%s %-15s %-15s %4s %4s %s" % (
            (' ', '*')[jail.jid_exists()],
            name,
            jail.get_config('addr'),
            jail.getid_jid(),
            jail.get_config('boot').replace('no','-'),
            jail.get_config('hostname')
            ));

