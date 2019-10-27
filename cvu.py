# Copyright (C) 2019 Valentin Vanelslande
# Licensed under GPLv2 or any later version
# Refer to the license.txt file included.

import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile

import tqdm
import urllib3

FILE_NAME_PATTERN = 'citra-valentin-windows-(.*).tar.gz'


def main():
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
            return

    http = urllib3.PoolManager()

    r = http.request('GET', 'https://api.github.com/repos/vvanelslande/citra/releases',
                     headers={'user-agent': f'Citra Valentin updater on {sys.platform}'})
    releases = json.loads(r.data.decode('utf8'))
    latest = None
    tgz_url = None

    for release in releases:
        if latest is not None:
            break

        for asset in release['assets']:
            match = re.match(pattern=FILE_NAME_PATTERN, string=asset['name'])

            if match is not None:
                latest = match.group(1)
                tgz_url = asset['browser_download_url']

                print(
                    f'Latest version: {latest} (tag name: {release["tag_name"]})')

                break

    if installed != latest:
        print(f'Installing {latest}...')

        r = http.request('GET', tgz_url, headers={
            'user-agent': f'Citra Valentin updater on {sys.platform}'}, preload_content=False)

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
            if os.path.isdir(os.path.join(disabled, 'user')):
                shutil.copytree(os.path.join(disabled, 'user'), os.path.join(
                    INSTALL_DIR, f'citra-valentin-windows-{latest}', 'user'))
                print(f'user directory from {installed} copied to {latest}')
        tar.extractall(INSTALL_DIR)
    else:
        print('You have the latest version.')

    args = [os.path.join(
        INSTALL_DIR, f'citra-valentin-windows-{latest}', 'citra-valentin-qt.exe')] + sys.argv[1:]

    subprocess.Popen(args)


if __name__ == '__main__':
    main()
