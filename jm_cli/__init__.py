"""

Main file for parsing arguments and executing appropriate command

    list_commands() - internal routine to add modules as commands
    jm_run() - main function to run the program

"""

import argparse
import os
import sys
import re

def list_commands():
    """Generates list of CLI commands from module directory
    
    Every *.py file within jm_cli directory is a potential command

    Returns
    -------
    list
        a list of available module commands sorted alphabetically

    """

    rv = []

    """Every .py rather than __*.py is added as a command"""
    for filename in os.listdir(os.path.abspath(os.path.dirname(__file__))):
        if filename.endswith('.py',) and not filename.startswith('__'):
            rv.append(re.sub(".py$", "", filename))

    rv.sort()

    return rv

def jm_run():
    """Main function run to parse commandline and execute appropriate module
    """

    p = {}

    """Initialize main parser"""
    mainp = argparse.ArgumentParser(description = 'jm - jail manager')
    subp = mainp.add_subparsers(dest = 'command')
    subp.required = True

    """Add subparserver for commands"""
    for command in list_commands():
        mod = __import__(f"jm_cli.{command}", None, None, 'parser')
        p[command] = subp.add_parser(command)
        mod.parser(p[command])

    """Parse commandline arguments"""
    args = mainp.parse_args()

    """Execute module according to command"""
    mod = __import__(f"jm_cli.{args.command}", None, None, 'run')
    mod.run(args)

"""Run if invoked standalone
"""
if __name__ == '__main__':
    jm_run()

