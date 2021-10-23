#!/usr/bin/python3

import argparse as _argparse
import sys as _sys
import json as _json
import re as _re

from pi_monitor.monitor.agents import AgentBuilder as _AgentBuilder
from pi_monitor.monitor.senders import SenderFactory as _SenderFactory
from pi_monitor.monitor.singleMonitors import _MONITORS

# define function to run
def main():
    global used_args
    try:
        global _MONITORS
        _MONITORS = {k.lower(): v for k, v in _MONITORS.items()} # keys are mixed case although they are lower case in code.

        monitors = [_ for _ in used_args if _ in _MONITORS.keys()]
        senders = [_.replace("send_to_", "") for _ in used_args if bool(_re.match("send_to_", _))]

        #### CREATE AND RUN THE AGENT ####

        print("building agent...")
        agent_builder = _AgentBuilder()
        sender_factory = _SenderFactory()

        for m in monitors:
            agent_builder.add_monitor(_MONITORS[m]())
        
        for s in senders:
            print(senders)
            print(f"---> {s} <----")
            sender_name = f"send_to_{s}"
            sender = sender_factory.build(sender_type=s)
            agent_builder.add_sender(sender)

        agent = agent_builder.build()

        print("start monitor...")

        agent.start()
    except:
        print(agent.list_parts())

# CLI portion
parser = _argparse.ArgumentParser()

parser.add_argument('--interval', nargs=1, default=5, type=float, help="Time interval in seconds between data capture (defaults to 5).")
parser.add_argument('--refresh-context-every', nargs=1, type=int, help="Time interval in seconds between refreshes of the context data. E.g. --refresh-context-every 1200 (data refresehd every 20 min)")

parser.add_argument('--cpu', nargs="*", help="Run the CPU monitor. Option to monitor each cpu (defaults to False). E.g. --cpu True")
parser.add_argument('--disk', nargs="*", help="Run the Disk monitor. Option to set the mount point to monitor (defaults to '/'). E.g. --disk '/'")
parser.add_argument('--memory', nargs="*", help="Run the memory monitor. Both virtual and swap memories are monitored")
parser.add_argument('--processes', nargs="*", help="Run the process monitor.")
parser.add_argument('--uptime', nargs="*", help="Run the uptime monitor.")

parser.add_argument('--send-to-file', nargs='*', help="Send the monitoring data to a file. If the file exists, the data will be automatically appended. If the file does not exist, it will be created. Parameter expects the filepath as argument. E.g. --send_to_file /home/user/monitoring.txt")
parser.add_argument('--send-to-sqlite', nargs='*', help="Send the monitoring data to a sqlite database. If the database does not exist, it will be automatically created. Parameter expects the database_name and table_name as argument. Database_name is the path to the database. Table_name is optional (defaults to None). E.g. --send_to_sqlite /home/user/monitoring.sqlite")

args = vars(parser.parse_args())

used_args = {k: v for k, v in args.items() if v != None}

# Start execution
if __name__ == "__main__":

    main()
# args = vars(parser.parse_args())
# print(args.get('username'))