import json as _json
import os as _os
from os.path import expanduser as _expanduser
import os as _os
import pprint as _pprint
import re as _re
import sys as _sys
import time as _time
from typing import Dict as _Dict, Any as _Any, Optional as _Optional, List as _List

import click
import toml as _toml

from .monitor.agents import AgentBuilder as _AgentBuilder
from .monitor.senders import SenderFactory as _SenderFactory
from .monitor.singleMonitors import _MONITORS, MonitorFactory as _MonitorFactory
from .monitor.senders import _SENDERTYPES, _SENDERS

# TODO: implement that --send-to-options can be read from environment variables and/or files instead of being given as string.

home_dict = _expanduser("~")

senders = []
senders_parameters = []
monitors = []
monitors_parameters = []

@click.group()
@click.pass_context
def cli(ctx):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)


@cli.command()
@click.option("--interval", type=float, default=30, nargs=1)
@click.option("--refresh-context-every", type=float, nargs=1)
@click.option("--monitor", multiple=True)
@click.option("--monitor-options", multiple=True)
@click.option("--send-to", multiple=True)
@click.option("--send-to-options", multiple=True)
@click.option("--from-config-file", multiple=False, default=".pimonitor-config.toml")
@click.pass_context
# TODO:
# 1. Change the behavior so that without arguments, the tool runs from a config with a predefined name.
# default name .pimonitor-config.toml. Config files are toml and name should end in toml (?).
# 2. sqlite sender by default
# 3. always keep a buffer (sqlite db) with the last 2 weeks.
# 4. by default, sqlite db only keeps 3 months worth of data.
def run(ctx, interval, monitor, monitor_options, send_to, send_to_options, refresh_context_every, from_config_file):

    try:
        global senders
        global senders_parameters
        global monitors
        global monitors_parameters
        global _MONITORS
        global _SENDERTYPES
        global _SENDERS
        
        _MONITORS = {k.lower(): v for k, v in _MONITORS.items()}
        
        monitors = monitor
        monitors_parameters = monitor_options
        
        monitors = [_ for _ in monitors if _ in _MONITORS.keys()]
        
        senders = send_to
        senders_parameters = send_to_options

        if len(senders) == 0:
            click.echo("At least one sender is required.")
            raise SystemExit
        # import os
        # os._exit(0)

        #### CREATE AND RUN THE AGENT ####
        agent = None
        agent_builder = _AgentBuilder()
        sender_factory = _SenderFactory()
        monitor_factory = _MonitorFactory()

        m_cnt = 0
        for m in monitors:
            if len(monitors_parameters) > 0:
                params = _json.loads(monitors_parameters[m_cnt])
            else:
                params = {}
            
            monitor = monitor_factory.build(monitor_type=m, **params)
            agent_builder.add_monitor(monitor)
            m_cnt += 1
        
        s_cnt = 0
        for s in senders:
            params = _json.loads(senders_parameters[s_cnt])
            
            sender = sender_factory.build(sender_type=s, **params)
            agent_builder.add_sender(sender)
            s_cnt += 1

        agent = agent_builder.build()
        agent.interval = interval
        agent.reload_context_every = refresh_context_every

        agent.start()

        with open(f"{home_dict}/.pimonitor.pid", mode="w", encoding="utf-8") as f:
            f.write(str(_os.getpid()))

    except KeyboardInterrupt:
        if agent:
            agent.stop_agent()
        print("Stopped by user.")
    except BaseException as e:
        if agent:
            agent.stop_agent()
        print("Unexpected error.")
        print("Debugging data:")
        print(f"m_cnt: {m_cnt}; len(monitors): {len(monitors)}; len(monitors_parameters): {len(monitors_parameters)}")
        raise e

@cli.command()
def kill():
    click.echo("...stopping pi_monitor.")

    with open(f"{home_dict}/.pimonitor.pid", mode="r", encoding="utf-8") as f:
        pm_pid = f.readlines()[0]
    
    _os.kill(int(pm_pid))

    click.echo("...pimonitor is now stopped.")

@cli.command()
@click.option("--username-password", nargs=1, help="Enter credentials as a string of the following format: 'username, password', e.g. 'testuser, testpassword'.")
def set_rabbitmq_credentials(username_password: _Optional[str] = None):
    
    if username_password != None:
        _os.environ["PIMONITOR_RABBITMQ_PLAIN_CREDENTIALS"] = username_password
    

def read_toml(filepath: str) -> _Dict[str, _Any]:
    # TODO: write a configuration handler class.
    
    try:
        with open("Hello_xxx/settings.toml", encoding="utf-8") as f:
            file = f.readlines()

        file = "".join(file)

        output = _toml.loads(file)
        
        # handle the rabbitmq credentials
        senders_names = [_.lower() for _ in output["senders"].keys]
        if 'rabbitmq' in senders_names:
            ...
        
    except BaseException as e:
        _pprint("Could not load the toml configuration file. Please check your config file.")
        raise e
        exit()



if __name__ == '__main__':
    cli(obj={})
