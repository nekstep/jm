"""

JM CLI module - __TEMPLATE__

    __DESCRIPTION__

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

def validate():
    """Perform basic validation

    Returns
    -------
    boolean
        True if we should proceed
    """

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

    if not validate():
        return -1

