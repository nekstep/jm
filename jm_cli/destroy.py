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


def run(in_args):
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

    jail = jmJail(args.name, cfg.params)
    jail.load(cfg.params)

    if jail.jid_exists():
        print(f"Jail {jail.name} is running as {jail.jid()}!")
        exit -1

    if not input(f"Destroy jail {jail.name} [y/N]?") == "y":
        return -1

    jail.destroy()

    cfg.params.remove_section(jail.name)
    cfg.save()

    print(f"Destroyed {jail.name}")

