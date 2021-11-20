import json as _json
import os as _os
from os.path import expanduser as _expanduser
import re as _re
import sys as _sys
import time as _time

import click

from .monitor.agents import AgentBuilder as _AgentBuilder
from .monitor.senders import SenderFactory as _SenderFactory
from .monitor.singleMonitors import _MONITORS
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
@click.pass_context
def run(ctx, interval, monitor, monitor_options, send_to, send_to_options, refresh_context_every):

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
            exit

        #### CREATE AND RUN THE AGENT ####
        agent = None
        agent_builder = _AgentBuilder()
        sender_factory = _SenderFactory()

        m_cnt = 0
        for m in monitors:
            agent_builder.add_monitor(_MONITORS[m]())
            m_cnt += 1
        
        s_cnt = 0
        for s in senders:
            print(senders_parameters)
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
        raise e

@cli.command()
def kill():
    click.echo("...stopping pi_monitor.")

    with open(f"{home_dict}/.pimonitor.pid", mode="r", encoding="utf-8") as f:
        pm_pid = f.readlines()[0]
    
    _os.kill(int(pm_pid))

    click.echo("...pimonitor is now stopped.")
    


if __name__ == '__main__':
    cli(obj={})
