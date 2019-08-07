import argparse
import os
import sys
import re

#command_list = ["activate", "create", "list", "start", "console", "stop", "destroy"]

def list_commands():
    rv = []

    for filename in os.listdir(os.path.abspath(os.path.dirname(__file__))):
        if filename.endswith('.py',) and not filename.startswith('__init__'):
            rv.append(re.sub(".py$", "", filename))

    rv.sort()

    return rv

def jm_run():
    p = {}

    mainp = argparse.ArgumentParser(description = 'jm - jail manager')
    subp = mainp.add_subparsers(dest = 'command')

    for command in list_commands():
        mod = __import__(f"jm_cli.{command}", None, None, 'parser')
        p[command] = subp.add_parser(command)
        mod.parser(p[command])

    args = mainp.parse_args()

    mod = __import__(f"jm_cli.{args.command}", None, None, 'run')
    mod.run(args)

if __name__ == '__main__':
    jm_run()

