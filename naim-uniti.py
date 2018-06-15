#!/usr/bin/env python

import argparse
import sys
from tasks import volume_change, mute_toggle, power_action, play_action, select_input


def check_ip_address(value):
    if sys.version_info >= (3, 3):
        import ipaddress
        try:
            ipaddress.ip_address(value)
            return value
        except ValueError:
            raise argparse.ArgumentTypeError("{ip} does not appear to be an IPv4 or IPv6 address".format(ip=value))
    else:
        import socket
        try:
            socket.inet_aton(value)
            return value
        except socket.error:
            raise argparse.ArgumentTypeError("{ip} does not appear to be an IPv4 or IPv6 address".format(ip=value))


def parse_args(args):
    """
    Parse command line parameters

    :param args: command line parameters as list of strings
    :return: command line parameters as :obj:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser(description="For controlling NAIM Uniti device via command line")
    required_named = parser.add_argument_group('required arguments')
    required_named.add_argument('--ip', dest='ip_address', help='ip address of your Naim Unity device', required=True,
                                type=check_ip_address)

    parser.add_argument('requested_action', action="store",
                        choices=['volume-up', 'volume-down', 'mute-toggle', 'power-on', 'power-off', 'power-toggle',
                                 'play-next', 'play-previous', 'play-pause', 'input-analog-1', 'input-digital-1',
                                 'input-digital-2', 'input-digital-3', 'input-bluetooth', 'input-webradio'
                                 ],
                        help="simulate action on remote control")
    parser.add_argument('-d', dest='request_confirmation', action="store_true",
                        help='request a confirmation of the change, for volume, mute, and power change')
    parser.add_argument('-v', dest='volume_increment', action="count",
                        help='volume increment (default is 1) -vvv is increment by 3')
    return parser.parse_args(args)


def main(args):
    args_parsed = parse_args(args)
    if 'volume-up' == args_parsed.requested_action:
        increment = args_parsed.volume_increment or 1
        volume_change.delay(args_parsed.ip_address, increment, args_parsed.request_confirmation)
    elif 'volume-down' == args_parsed.requested_action:
        increment = args_parsed.volume_increment or 1
        volume_change.delay(args_parsed.ip_address, -increment, args_parsed.request_confirmation)
    elif 'mute-toggle' == args_parsed.requested_action:
        mute_toggle(args_parsed.ip_address, args_parsed.request_confirmation)
    elif 'power-on'== args_parsed.requested_action:
        power_action.delay(args_parsed.ip_address, 'on', args_parsed.request_confirmation)
    elif 'power-off' == args_parsed.requested_action:
        power_action.delay(args_parsed.ip_address, 'lona', args_parsed.request_confirmation)
    elif 'power-toggle' == args_parsed.requested_action:
        power_action.delay(args_parsed.ip_address, 'toggle', args_parsed.request_confirmation)
    elif 'play-next' == args_parsed.requested_action:
        play_action.delay(args_parsed.ip_address, 'next')
    elif 'play-previous' == args_parsed.requested_action:
        play_action.delay(args_parsed.ip_address, 'prev')
    elif 'play-pause' == args_parsed.requested_action:
        play_action.delay(args_parsed.ip_address, 'playpause')
    elif 'input-analog-1' == args_parsed.requested_action:
        select_input.delay(args_parsed.ip_address, 'ana1')
    elif 'input-digital-1' == args_parsed.requested_action:
        select_input.delay(args_parsed.ip_address, 'dig1')
    elif 'input-digital-2' == args_parsed.requested_action:
        select_input.delay(args_parsed.ip_address, 'dig2')
    elif 'input-digital-3' == args_parsed.requested_action:
        select_input.delay(args_parsed.ip_address, 'dig3')
    elif 'input-bluetooth' == args_parsed.requested_action:
        select_input.delay(args_parsed.ip_address, 'bluetooth')
    elif 'input-webradio' == args_parsed.requested_action:
        select_input.delay(args_parsed.ip_address, 'radio')


if __name__ == '__main__':
    main(sys.argv[1:])
