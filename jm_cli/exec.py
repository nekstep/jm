import argparse
import os

import jm_lib.zfs as zfs
from jm_lib.config import jmConfig
from jm_lib.jail import jmJail

args = None
cfg = None

def parser(p):
    p.add_argument('name')
    p.add_argument('cmd', nargs = argparse.REMAINDER)

def validate():
    if not args.name in cfg.params.sections():
        print(f"Jail {args.name} does not exist!")
        return False

    return True

def exec_jail(name, cmd):
    jail = jmJail(name, cfg.params)
    jail.load(cfg.params)

    status = jail.status()

    if status == 1:
        jail.exec(cmd)

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
        order = cfg.jaillist()

        for name in order:
            exec_jail(name, args.cmd)

    else:
        if not validate():
            return -1

        exec_jail(args.name, args.cmd)

