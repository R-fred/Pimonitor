import argparse as _argparse
import sys as _sys
import json as _json
import re as _re

import click

from .monitor.agents import AgentBuilder as _AgentBuilder
from .monitor.senders import SenderFactory as _SenderFactory
from .monitor.singleMonitors import _MONITORS


@click.group()
@click.pass_context
def cli(ctx):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)


@cli.command()
@click.option("--interval", type=float, default=30, nargs=1)
@click.option("--refresh-context-every", type=float, nargs=1)
@click.option("--monitors", nargs=0)
@click.argument("monitors", nargs=-1) # trick (incl. nargs=0 on the previous line) to get multiple arguments working.
@click.option("--send-to", multiple=True)
@click.pass_context
def run(ctx, interval, refresh_context_every, monitors, send_to):

    try:
        global _MONITORS
        _MONITORS = {k.lower(): v for k, v in _MONITORS.items()} # keys are mixed case although they are lower case in code.
        
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
            sender_name = f"send_to_{s}"
            sender = sender_factory.build(sender_type=s)
            agent_builder.add_sender(sender)

        agent = agent_builder.build()
        agent.interval = interval
        agent.reload_context_every = refresh_context_every

        agent.start()
    except KeyboardInterrupt:
        agent.stop_agent()
        print("Stopped by user.")
    except:
        agent.stop_agent()
        print("Unexpected error.")
        raise

@cli.command()
def stop():
    click.echo("...stopping pi_monitor.")
    click.echo("Simply a dummy for now")

if __name__ == '__main__':
    cli(obj={})
