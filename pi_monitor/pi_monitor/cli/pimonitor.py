import argparse
import sys
import json

from pi_monitor.monitor.agents import AgentBuilder as _AgentBuilder
from pi_monitor.monitor.senders import SenderFactory as _SenderFactory
from pi_monitor.monitor.singleMonitors import _MONITORS


class MonitoringAgentCLI(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='cli tool to start the Monitoring agent.',
            usage='''git <command> [<args>]

The most commonly used git commands are:
   commit     Record changes to the repository
   fetch      Download objects and refs from another repository
''')
        parser.add_argument('command', help='Subcommand to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def run(self):
        #### Get arguments ####
        parser = argparse.ArgumentParser(
            description='Record changes to the repository')
        # prefixing the argument with -- means it's optional
        parser.add_argument('--interval', nargs=1, default=5, type=float, help="Time interval in seconds between data capture (defaults to 5).")
        parser.add_argument('--refresh-context-every', nargs=1, type=int, help="Time interval in seconds between refreshes of the context data. E.g. --refresh-context-every 1200 (data refresehd every 20 min)")

        parser.add_argument('--cpu', nargs="*", help="Run the CPU monitor. Option to monitor each cpu (defaults to False). E.g. --cpu True")
        parser.add_argument('--disk', nargs="*", help="Run the Disk monitor. Option to set the mount point to monitor (defaults to '/'). E.g. --disk '/'")
        parser.add_argument('--memory', nargs="*", help="Run the memory monitor. Both virtual and swap memories are monitored")
        parser.add_argument('--processes', nargs="*", help="Run the process monitor.")
        parser.add_argument('--uptime', nargs="*", help="Run the uptime monitor.")

        parser.add_argument('--send-to-file', nargs=1, help="Send the monitoring data to a file. If the file exists, the data will be automatically appended. If the file does not exist, it will be created. Parameter expects the filepath as argument. E.g. --send_to_file /home/user/monitoring.txt")
        parser.add_argument('--send-to-sqlite', nargs=2, help="Send the monitoring data to a sqlite database. If the database does not exist, it will be automatically created. Parameter expects the database_name and table_name as argument. Database_name is the path to the database. Table_name is optional (defaults to None). E.g. --send_to_sqlite /home/user/monitoring.sqlite")

        self.args = vars(parser.parse_args(sys.argv[2:]))

        print(f'\nRunning with {self.args}\n')

        #### CREATE AND RUN THE AGENT ####

        agent_builder = _AgentBuilder()
        sender_factory = _SenderFactory()

        agent = agent_builder.build()

        agent.start()


if __name__ == '__main__':
    MonitoringAgentCLI()