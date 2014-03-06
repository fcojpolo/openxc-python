from __future__ import absolute_import

import argparse
import sys
import time
import threading

from openxc.formats.json import JsonFormatter
from .common import device_options, configure_logging, select_device


class ResponseHandler(object):

    def __init__(self):
        self.response_lock = threading.Condition()

    def receive(message, **kwargs):
        self.response_lock.acquire()

        # TODO may want to move this logic into controllers.base so it can be
        # used programatically instead of from the command line only
        if (message.get('bus') == self.request.bus and
                message.get('id') == self.request.id and
                message.get('mode') == self.request.mode):
            print(response)
            # TODO currently this is going to exit after the first response.
            # what about broadcast requests? we may just need to stay alive for
            # 1 second
            self.response_lock.notify()

        self.response_lock.release()

    def request(self, arguments, controller):
        self.response_lock.acquire()

        request = {
                'command': "diagnostic_request",
                'request': {
                    'bus': int(arguments.bus_id, 0),
                    'id': int(arguments.message_id, 0)
                }
        }

        if arguments.diagnostic_mode is not None:
            request['request']['mode'] = int(arguments.diagnostic_mode, 0)
        if arguments.payload is not None:
            # TODO what format is the payload going to be? hex?
            request['request']['payload'] = arguments.payload
        if arguments.pid is not None:
            request['request']['pid'] = int(arguments.pid, 0)
        if arguments.frequency is not None:
            request['request']['frequency'] = int(arguments.frequency, 0)

        controller.complex_request(request)

        self.response_lock.wait(1)


def parse_options():
    parser = argparse.ArgumentParser(description="Send diagnostic message requests to an attached VI",
            parents=[device_options()])
    parser.add_argument("bus_id")
    parser.add_argument("message_id")
    parser.add_argument("diagnostic_mode")
    parser.add_argument("--pid")
    parser.add_argument("--payload")
    parser.add_argument("--frequency")

    return parser.parse_args()


def main():
    configure_logging()
    arguments = parse_options()

    controller_class, controller_kwargs = select_device(arguments)
    controller = controller_class(**controller_kwargs)
    controller.start()

    import time
    time.sleep(.1)
    response_handler = ResponseHandler()
    response_handler.request(arguments, controller)
