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

home_dict = _expanduser("~")

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
@click.option("--send-to", multiple=True)
@click.pass_context
def run(ctx, interval, refresh_context_every, monitor, send_to):

    try:
        global _MONITORS
        global _SENDERTYPES
        global _SENDERS

        _MONITORS = {k.lower(): v for k, v in _MONITORS.items()} # keys are mixed case although they are lower case in code.
        
        monitors = monitor
        if type(monitor) != list or type(monitor) != tuple:
            monitor = (monitor,)
        
        if type(send_to) != list or type(send_to) != tuple:
            send_to = (send_to,)
            
        monitors = [_ for _ in monitors if _ in _MONITORS.keys()]
        senders = send_to

        if len(senders) == 0:
            click.echo("At least one sender is required.")
            exit

        #### CREATE AND RUN THE AGENT ####

        agent_builder = _AgentBuilder()
        sender_factory = _SenderFactory()

        for m in monitors:
            agent_builder.add_monitor(_MONITORS[m]())
        
        for s in senders:
            sender = sender_factory.build(sender_type=s)
            agent_builder.add_sender(sender)

        agent = agent_builder.build()
        agent.interval = interval
        agent.reload_context_every = refresh_context_every

        agent.start()

        with open(f"{home_dict}/.pimonitor.pid", mode="w", encoding="utf-8") as f:
            f.write(str(_os.getpid()))

    except KeyboardInterrupt:
        agent.stop_agent()
        print("Stopped by user.")
    except:
        agent.stop_agent()
        print("Unexpected error.")
        raise

@cli.command()
def kill():
    click.echo("...stopping pi_monitor.")

    with open(f"{home_dict}/.pimonitor.pid", mode="r", encoding="utf-8") as f:
        pm_pid = f.readlines()[0]
    
    _os.kill(int(pm_pid))

    click.echo("...pimonitor is now stopped.")


if __name__ == '__main__':
    cli(obj={})
