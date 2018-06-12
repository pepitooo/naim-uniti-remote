#!/usr/bin/env python

import argparse
import ipaddress
import json
import sys

import requests

request_confirmation = True


def get_current_value(url_pattern, ip_address, variable):
    r = requests.get(url_pattern.format(ip=ip_address))
    if r.status_code == 200:
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


def volume_up(ip_address):
    current_volume = volume_get_current_value(ip_address)
    if current_volume is not None:
        requests.put('http://{ip}:15081/levels/room?volume={value}'.format(ip=ip_address, value=current_volume+1))
        if request_confirmation:
            print('Volume have been set to {value}'.format(value=volume_get_current_value(ip_address)))


def volume_down(ip_address):
    current_volume = volume_get_current_value(ip_address)
    if current_volume is not None:
        # volume will not go under 0, no big deal if you send negative value
        requests.put('http://{ip}:15081/levels/room?volume={value}'.format(ip=ip_address, value=current_volume-1))
        if request_confirmation:
            print('Volume have been set to {value}'.format(value=volume_get_current_value(ip_address)))


def mute_toggle(ip_address):
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


def power_on(ip_address):
    requests.put('http://{ip}:15081/power?system={value}'.format(ip=ip_address, value='on'))
    if request_confirmation:
        display_power_status(ip_address)


def power_off(ip_address):
    requests.put('http://{ip}:15081/power?system={value}'.format(ip=ip_address, value='lona'))
    if request_confirmation:
        display_power_status(ip_address)


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
                        choices=['volume-up', 'volume-down', 'mute-toggle', 'power-on', 'power-off',
                                 # 'play-next', 'play-previous'
                                 ],
                        help="simulate action on remote control")
    return parser.parse_args(args)


def main(args):
    args_parsed = parse_args(args)
    if 'volume-up' == args_parsed.requested_action:
        volume_up(args_parsed.ip_address)
    elif 'volume-down' == args_parsed.requested_action:
        volume_down(args_parsed.ip_address)
    elif 'mute-toggle' == args_parsed.requested_action:
        mute_toggle(args_parsed.ip_address)
    elif 'power-on'== args_parsed.requested_action:
        power_on(args_parsed.ip_address)
    elif 'power-off' == args_parsed.requested_action:
        power_off(args_parsed.ip_address)


if __name__ == '__main__':
    main(sys.argv[1:])