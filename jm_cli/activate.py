"""

JM CLI module - ACTIVATE

    Used initially to activate ZFS pools for JM.

Every CLI module should export two functions:
    parser(p) - to add appropriate parsers to argparse subparser
    run(in_args) - to run the module with relevant parsed arguments

"""

import argparse
import os

import jm_lib.zfs as zfs
from jm_lib.config import jmConfig

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
    p.add_argument('zfspool')
    p.add_argument('mountpoint')

def validate():
    """Perform basic validation on ZFS

    Returns
    -------
    boolean
        True if we should proceed
    """

    """Check if mountpoint already exists"""
    if os.path.exists(args.mountpoint):
        print(f"Mountpoint {args.mountpoint} already exists!")
        return False

    """Check if ZFS pool already exists"""
    if args.zfspool in zfs.list():
        print(f"ZFS pool {args.zfspool} already exists!")
        return False

    """All ok - proceed"""
    return True

def run(in_args):
    """Run the ACTIVATE command

    Parameters
    ----------
    in_args
        Result of parsing commandline parameters with argparse
    """

    global args
    global config

    args = in_args
    cfg = jmConfig()

    """Config file shouldn't be present"""
    if cfg.exists:
        print (f"Config {cfg.configfile} already present!")
        return -1

    if not validate():
        return -1

    """Create ZFS mountpoints and pools"""
    zfs.create(args.zfspool, args.mountpoint)
    zfs.create(args.zfspool + '/jails', args.mountpoint + '/jails')
    zfs.create(args.zfspool + '/defaults', args.mountpoint + '/defaults')

    """Create and write basic config file"""
    cfg.params['MAIN'] = {
            'zfspool': args.zfspool,
            'mountpoint': args.mountpoint }

    cfg.save()

