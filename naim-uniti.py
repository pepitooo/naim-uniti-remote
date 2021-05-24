#!/usr/bin/env python

import argparse
import sys
import json

import requests


def get_current_value(url_pattern, ip_address, variable):
    r = requests.get(url_pattern.format(ip=ip_address))
    if r.status_code == 200:
        content = r.content
        if type(content) == bytes:
            content = content.decode()
        j = json.loads(r.content)
        if variable in j:
            return j[variable]


def volume_get_current_value(ip_address):
    return int(get_current_value('http://{ip}:15081/levels/room', ip_address, 'volume'))


def mute_get_current_value(ip_address):
    return int(get_current_value('http://{ip}:15081/levels/room', ip_address, 'mute'))


def get_power_state(ip_address):
    current_state = get_current_value('http://{ip}:15081/power', ip_address, 'system')
    return current_state == 'on'


def volume_change(ip_address, increment, request_confirmation=False):
    current_volume = volume_get_current_value(ip_address)
    if current_volume is not None:
        # volume will not go under 0, no big deal if you send negative value
        requests.put('http://{ip}:15081/levels/room?volume={value}'.format(ip=ip_address, value=current_volume+increment))
        if request_confirmation:
            print('Volume have been set to {value}'.format(value=volume_get_current_value(ip_address)))


def mute_toggle(ip_address, request_confirmation=False):
    mute = mute_get_current_value(ip_address)
    if mute is not None:
        requests.put('http://{ip}:15081/levels/room?mute={value}'.format(ip=ip_address, value=int(not(mute > 0))))
        if request_confirmation:
            print('Mute have been set to {value}'.format(value=bool(mute_get_current_value(ip_address))))


def display_power_status(ip_address):
    current_state = get_power_state(ip_address)
    if current_state:
        print('Your Naim Uniti device is Power On')
    else:
        print('Your Naim Uniti device is Power Off')


def power_action(ip_address, action, request_confirmation=False):
    if action == 'toggle':
        if get_power_state(ip_address):
            action = 'lona'
        else:
            action = 'on'
    requests.put('http://{ip}:15081/power?system={action}'.format(ip=ip_address, action=action))
    if request_confirmation:
        display_power_status(ip_address)


def play_action(ip_address, action):
    requests.get('http://{ip}:15081/nowplaying?cmd={action}'.format(ip=ip_address, action=action))


def select_input(ip_address, input_identifier):
    requests.get('http://{ip}:15081/inputs/{input}?cmd=select'.format(ip=ip_address, input=input_identifier))


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
        volume_change(args_parsed.ip_address, increment, args_parsed.request_confirmation)
    elif 'volume-down' == args_parsed.requested_action:
        increment = args_parsed.volume_increment or 1
        volume_change(args_parsed.ip_address, -increment, args_parsed.request_confirmation)
    elif 'mute-toggle' == args_parsed.requested_action:
        mute_toggle(args_parsed.ip_address, args_parsed.request_confirmation)
    elif 'power-on'== args_parsed.requested_action:
        power_action(args_parsed.ip_address, 'on', args_parsed.request_confirmation)
    elif 'power-off' == args_parsed.requested_action:
        power_action(args_parsed.ip_address, 'lona', args_parsed.request_confirmation)
    elif 'power-toggle' == args_parsed.requested_action:
        power_action(args_parsed.ip_address, 'toggle', args_parsed.request_confirmation)
    elif 'play-next' == args_parsed.requested_action:
        play_action(args_parsed.ip_address, 'next')
    elif 'play-previous' == args_parsed.requested_action:
        play_action(args_parsed.ip_address, 'prev')
    elif 'play-pause' == args_parsed.requested_action:
        play_action(args_parsed.ip_address, 'playpause')
    elif 'input-analog-1' == args_parsed.requested_action:
        select_input(args_parsed.ip_address, 'ana1')
    elif 'input-digital-1' == args_parsed.requested_action:
        select_input(args_parsed.ip_address, 'dig1')
    elif 'input-digital-2' == args_parsed.requested_action:
        select_input(args_parsed.ip_address, 'dig2')
    elif 'input-digital-3' == args_parsed.requested_action:
        select_input(args_parsed.ip_address, 'dig3')
    elif 'input-bluetooth' == args_parsed.requested_action:
        select_input(args_parsed.ip_address, 'bluetooth')
    elif 'input-webradio' == args_parsed.requested_action:
        select_input(args_parsed.ip_address, 'radio')


if __name__ == '__main__':
    main(sys.argv[1:])
