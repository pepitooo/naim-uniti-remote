import json
import logging
import sys

import requests
from celery import Celery
from celery.signals import after_setup_logger

app = Celery(
    'tirs_celery',
    broker='redis://localhost:6379/0',
    # ## add result backend here if needed.
    backend='redis://localhost:6379/0'
)


def get_current_value(url_pattern, ip_address, variable):
    r = requests.get(url_pattern.format(ip=ip_address))
    if r.status_code == 200:
        content = r.content
        if type(content) == bytes:
            content = content.decode()
        j = json.loads(content)
        if variable in j:
            return j[variable]


def volume_get_current_value(ip_address):
    return int(get_current_value('http://{ip}:15081/levels/room', ip_address, 'volume'))


def mute_get_current_value(ip_address):
    return int(get_current_value('http://{ip}:15081/levels/room', ip_address, 'mute'))


def get_power_state(ip_address):
    current_state = get_current_value('http://{ip}:15081/power', ip_address, 'system')
    return current_state == 'on'


@after_setup_logger.connect()
def logger_setup_handler(logger, **kwargs):
    custom_handler = logging.StreamHandler(sys.stdout)
    custom_handler.setLevel(logging.DEBUG)
    custom_formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(name)s:%(filename)s:%(lineno)d %(message)s')
    custom_handler.setFormatter(custom_formatter)
    logger.addHandler(custom_handler)


@app.task
def volume_change(ip_address, increment, request_confirmation):
    current_volume = volume_get_current_value(ip_address)
    if current_volume is not None:
        # volume will not go under 0, no big deal if you send negative value
        requests.put(
            'http://{ip}:15081/levels/room?volume={value}'.format(ip=ip_address, value=current_volume + increment))
        if request_confirmation:
            logging.info('Volume have been set to {value}'.format(value=volume_get_current_value(ip_address)))


@app.task
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


@app.task
def power_action(ip_address, action, request_confirmation=False):
    if action == 'toggle':
        if get_power_state(ip_address):
            action = 'lona'
        else:
            action = 'on'
    requests.put('http://{ip}:15081/power?system={action}'.format(ip=ip_address, action=action))
    if request_confirmation:
        display_power_status(ip_address)


@app.task
def play_action(ip_address, action):
    requests.get('http://{ip}:15081/nowplaying?cmd={action}'.format(ip=ip_address, action=action))


@app.task
def select_input(ip_address, input_identifier):
    requests.get('http://{ip}:15081/inputs/{input}?cmd=select'.format(ip=ip_address, input=input_identifier))
