#!/usr/bin/env python3
"""Fire TV Remote -> PS3 (webMAN MOD virtual pad) - optimized"""

from evdev import InputDevice, ecodes
import threading
import requests
import subprocess
import time
import os

PS3_IP = 'your ps3 ip address'
PAD_URL = f'http://{PS3_IP}/pad.ps3'

DEVICES = [
    '/dev/input/event0',
    '/dev/input/event1',
]

KEY_TO_PS3 = {
    103: 'up',
    108: 'down',
    105: 'left',
    106: 'right',
    96:  'cross',
    158: 'circle',
    172: 'psbtn',
    139: 'triangle',
    164: 'square',
    168: 'select',
    208: 'start',
}

# One shared session = one persistent TCP connection
session = requests.Session()

def send_pad(btn):
    try:
        session.get(f'{PAD_URL}/{btn}', timeout=1)
    except Exception:
        pass

def handle_key(code, value):
    if value != 1:
        return

    if code == 116:
        try:
            session.get(f'http://{PS3_IP}/shutdown.ps3', timeout=3)
        except requests.exceptions.ConnectionError:
            subprocess.Popen(['/home/pi/wakeps3.sh']) #this is where you can put in your own wake script, it boils down to a wakeonlan with the mac address of the ps3, thats it.
        return

    if code not in KEY_TO_PS3:
        return

    send_pad(KEY_TO_PS3[code])

def listen(path):
    dev = InputDevice(path)
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            handle_key(event.code, event.value)

def main():
    while True:
        if all(os.path.exists(p) for p in DEVICES):
            break
        time.sleep(2)

    # Pre-warm the connection
    try:
        session.get(f'http://{PS3_IP}/', timeout=3)
    except Exception:
        pass

    threads = []
    for path in DEVICES:
        t = threading.Thread(target=listen, args=(path,), daemon=True)
        t.start()
        threads.append(t)

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()   
