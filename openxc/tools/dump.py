import logging
import argparse
import time

from openxc.formats.json import JsonFormatter
from .common import device_options, configure_logging, select_device

def receive(message):
    message['timestamp'] = time.time()
    # TODO update docs on trace file format
    print(JsonFormatter.serialize(message))

def parse_options():
    parser = argparse.ArgumentParser(description="Receive and print OpenXC "
        "messages over USB", parents=[device_options()])
    parser.add_argument("--corrupted",
            action="store_true",
            dest="show_corrupted",
            default=False)

    arguments = parser.parse_args()
    return arguments


def main():
    configure_logging()
    arguments = parse_options()

    source_class, source_kwargs = select_device(arguments)
    source = source_class(receive, **source_kwargs)
    source.start()
