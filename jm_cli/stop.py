import argparse
import os

import jm_lib.zfs as zfs
from jm_lib.config import jmConfig
from jm_lib.jail import jmJail

args = None
cfg = None

def parser(p):
    p.add_argument('name')

def validate():
    if not args.name in cfg.params.sections():
        print(f"Jail {args.name} does not exist!")
        return False

    return True

def stop_jail(name):
    jail = jmJail(name, cfg.params)
    jail.load(cfg.params)

    if not jail.jid_exists():
        print (f"Jail {jail.name} is not running!")
        return -1

    jail.stop()


def run(in_args):
    global args
    global cfg

    args = in_args
    cfg = jmConfig()

    if not cfg.exists:
        print (f"Config {cfg.configfile} absent!")
        return -1

    cfg.load()

    if args.name == "ALL":
        order = cfg.shutorder()

        for name in order:
            stop_jail(name)

    else:
        if not validate():
            return -1
        
        stop_jail(args.name)


