#!/usr/bin/python3
import argparse
import logging

import pika
from .PiMonitor import PiMonitor

# Set up logging
logging.basicConfig(filename="log.log",
                    level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%m.%d.%Y %I:%M:%S %p'
                    )

# define function to run
def main(uname, pwd, server, port, monitor_iface, publish_interval, send_interface, naming, basic):
    try:
        broker_credentials = pika.PlainCredentials(uname, pwd)
        broker_parameters = pika.ConnectionParameters(host = server, port = port, virtual_host= "/", credentials = broker_credentials)
        
        monitor = PiMonitor(publish_interval=publish_interval,
                        send_iface=send_interface,
                        naming=naming,
                        monitor_iface=monitor_iface,
                        basic=basic
                        )
        monitor.send(broker_parameters=broker_parameters)
        #logging.info(f"System data sent. Send interval: {monitor.config['send_every']} s")
    except:
        logging.warning("System data could not be sent.")

# CLI portion
parser = argparse.ArgumentParser()

parser.add_argument("--serverurl", help="server url", default="localhost")
parser.add_argument("--username", help="user name for connecting to server")
parser.add_argument("--password", help= "password to connect to server")
parser.add_argument("--publishinterval", type=float, help="value in seconds to wait before sending next data package", default=1)
parser.add_argument("--sendinterface", help="network interface to use to send data.", default="eth0")
parser.add_argument("--naming", help="Prefix for the name of the monitor queue to send to. Either 'MAC' or 'IP'.", default="MAC")
parser.add_argument("--monitoriface", help="monitored network interface", default="eth0")
parser.add_argument("--basic", help="include more detailed data", default="True")
parser.add_argument("--port", help="port to connect to on the server", default="5672")

args = parser.parse_args()

if args.basic == "True":
    args.basic = True
else:
    args.basic = False

#print(f"sendevery: type == {type(args.sendevery)}, value == {args.sendevery}")

# Start execution
if __name__ == "__main__":

    main(uname=args.username,
         pwd=args.password,
         server=args.serverurl,
         port=int(args.port),
         publish_interval=float(args.publishinterval),
         send_interface=args.sendinterface,
         naming=args.naming,
         monitor_iface=args.monitoriface,
         basic=args.basic
         )
# args = vars(parser.parse_args())
# print(args.get('username'))