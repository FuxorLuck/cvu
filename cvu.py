# Copyright (C) 2019 Valentin Vanelslande
# Licensed under GPLv2 or any later version
# Refer to the license.txt file included.

import json
import io
import os
import re
import shutil
import subprocess
import sys
import tarfile
import urllib3

import tqdm

if sys.platform != 'win32':
    raise NotImplementedError('Only Windows is supported')

INSTALL_DIR = os.getenv('CVU_INSTALL_DIR', os.path.join(
    os.getenv('LOCALAPPDATA'), 'citra-valentin'))

print(f'Installation directory: {INSTALL_DIR}')

installed = None

if not os.path.exists(INSTALL_DIR):
    os.mkdir(INSTALL_DIR)
else:
    enabled = list(
        filter(lambda n: n.startswith('citra-valentin-windows-') and not n.endswith('-disabled'), os.listdir(INSTALL_DIR)))

    if len(enabled) == 1:
        installed = re.match(pattern='citra-valentin-windows-(.*)',
                             string=enabled[0]).group(1)

        print(f'Installed: {installed}')
    elif len(enabled) == 0:
        print('No installed and enabled version found.')
    else:
        subprocess.Popen(['explorer.exe', INSTALL_DIR])
        print('Multiple enabled versions found. add -disabled to the other versions.')
        sys.exit(0)

http = urllib3.PoolManager()

r = http.request('GET', 'https://api.github.com/repos/vvanelslande/citra/releases/latest',
                 headers={'user-agent': f'Citra Valentin Updater on {sys.platform}'})
latest = json.loads(r.data.decode('utf8'))['tag_name']

if True:  # installed != latest:
    print(f'Installing {latest}...')

    r = http.request('GET', f'https://github.com/vvanelslande/citra/releases/download/{latest}/citra-valentin-windows-{latest}.tar.gz', headers={
        'user-agent': f'Citra Valentin Updater on {sys.platform}'}, preload_content=False)

    size = int(r.headers['content-length'])
    t = tqdm.tqdm(total=size, unit='B', unit_scale=True)
    tgz = io.BytesIO()

    for data in r:
        t.update(len(data))
        tgz.write(data)

    t.close()

    tgz.seek(0)
    tar = tarfile.open(fileobj=tgz, mode='r:gz')
    if installed != None:
        disabled = os.path.join(
            INSTALL_DIR, f'citra-valentin-windows-{installed}-disabled')
        if os.path.exists(disabled):
            print(
                f'Directory \'citra-valentin-windows-{installed}-disabled\' already exists, deleting it.')
            shutil.rmtree(disabled)
        os.rename(os.path.join(
            INSTALL_DIR, f'citra-valentin-windows-{installed}'), disabled)
        print(f'{installed} was disabled (-disabled suffix added)')
    tar.extractall(INSTALL_DIR)
else:
    print('You have the latest version.')

args = [os.path.join(
    INSTALL_DIR, f'citra-valentin-windows-{latest}', 'citra-valentin-qt.exe')] + sys.argv[1:]
print(f'Starting {" ".join(args)}...')
subprocess.Popen(args)
