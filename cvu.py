# Copyright (C) 2019 Valentin Vanelslande
# Licensed under GPLv2 or any later version
# Refer to the license.txt file included.

"""Main file."""

import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tkinter
import traceback
import urllib
import webbrowser

import tqdm
import urllib3

FILE_NAME_PATTERN = 'citra-valentin-windows-(.*).tar.gz'
HTTP = urllib3.PoolManager()
INSTALL_DIR = os.getenv('CVU_INSTALL_DIR', os.path.join(
    os.getenv('LOCALAPPDATA'), 'citra-valentin'))


def http_get(url, **kwargs):
    """Makes a HTTP GET."""
    return HTTP.request('GET', url, headers={
        'user-agent': f'Citra Valentin updater on {sys.platform}'
    }, **kwargs)


def get_json(url, **kwargs):
    """Makes a HTTP GET then returns the parsed JSON."""
    res = http_get(url, **kwargs)
    return json.loads(res.data.decode('utf8'))


def get_releases(**kwargs):
    """Returns the releases for vvanelslande/citra."""
    return get_json(
        'https://api.github.com/repos/vvanelslande/citra/releases',
        **kwargs)


def get_installed_version():
    """Gets the installed Citra Valentin version."""
    installed = None

    if not os.path.exists(INSTALL_DIR):
        os.mkdir(INSTALL_DIR)
    else:
        enabled = list(
            filter(lambda n: n.startswith('citra-valentin-windows-')
                   and not n.endswith('-disabled'),
                   os.listdir(INSTALL_DIR)))

        if len(enabled) == 1:
            installed = re.match(pattern='citra-valentin-windows-(.*)',
                                 string=enabled[0]).group(1)

            print(f'Installed: {installed}')
        elif len(enabled) == 0:
            print('No installed and enabled version found.')
        else:
            subprocess.call(['explorer.exe', INSTALL_DIR])
            raise Exception('\n'.join([
                'Multiple enabled installed versions found.',
                'Explorer was started.',
                'To disable a version, add -disabled to it\'s directory name.'
            ]))

    return installed


def show_traceback(exception, formatted_traceback):
    """Shows a traceback and buttons to copy it or create a GitHub issue."""
    window = tkinter.Tk()
    window.title('cvu')
    window.state('zoomed')
    tkinter.Label(window, text='Something happened').pack()
    tkinter.Label(window, text='Traceback:').pack()
    text = tkinter.Text(window)
    text.insert(tkinter.END, formatted_traceback)
    text.config(state=tkinter.DISABLED)
    text.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    def copy_traceback():
        window.clipboard_clear()
        window.clipboard_append(formatted_traceback)

    def new_github_issue():
        qstr = urllib.parse.urlencode({
            'title': type(exception).__name__,
            'body': f'Issue generated by cvu.\n\n```\n{formatted_traceback}```'
        })
        webbrowser.open(
            f'https://github.com/vvanelslande/cvu/issues/new?{qstr}')
        window.quit()

    buttons = tkinter.Frame(window)
    tkinter.Button(buttons, text='Copy Traceback',
                   command=copy_traceback).pack(side=tkinter.LEFT)
    tkinter.Button(buttons,
                   text='New GitHub Issue',
                   command=new_github_issue).pack(side=tkinter.LEFT)
    buttons.pack(side=tkinter.BOTTOM)
    window.mainloop()


def delete_disabled(installed, disabled):
    """Deletes disabled directory if it already exists."""
    if os.path.exists(disabled):
        print(f'Deleting \'citra-valentin-windows-{installed}-disabled\'')
        print('Because it already exists.')
        shutil.rmtree(disabled)


def main():
    """Main function."""

    print(f'Installation directory: {INSTALL_DIR}')

    installed = None

    def excepthook(exctype, value, tbk):
        if installed is not None:
            subprocess.Popen([
                os.path.join(
                    INSTALL_DIR,
                    f'citra-valentin-windows-{installed}',
                    'citra-valentin-qt.exe'
                )
            ] + sys.argv[1:])

        show_traceback(value, traceback.format_exception(
            exctype, value, tbk))

    sys.excepthook = excepthook

    installed = get_installed_version()

    releases = get_releases()
    latest = None
    tgz_url = None

    for release in releases:
        if latest is not None:
            break

        for asset in release['assets']:
            match = re.match(pattern=FILE_NAME_PATTERN,
                             string=asset['name'])

            if match is not None:
                latest = match.group(1)
                tgz_url = asset['browser_download_url']

                print(' '.join([
                    f'Latest version: {latest}',
                    f'(tag name: {release["tag_name"]})'
                ]))

                break

    if installed != latest:
        print(f'Installing {latest}...')

        res = http_get(tgz_url, preload_content=False)
        size = int(res.headers['content-length'])
        progress = tqdm.tqdm(total=size, unit='B', unit_scale=True)
        tgz = io.BytesIO()

        for data in res:
            progress.update(len(data))
            tgz.write(data)

        progress.close()

        tgz.seek(0)
        tar = tarfile.open(fileobj=tgz, mode='r:gz')
        if installed is not None:
            disabled = os.path.join(
                INSTALL_DIR,
                f'citra-valentin-windows-{installed}-disabled')
            delete_disabled(installed, disabled)
            os.rename(os.path.join(
                INSTALL_DIR,
                f'citra-valentin-windows-{installed}'), disabled)
            print(f'{installed} was disabled (-disabled suffix added)')
            if os.path.isdir(os.path.join(disabled, 'user')):
                shutil.copytree(
                    os.path.join(disabled, 'user'),
                    os.path.join(INSTALL_DIR,
                                 f'citra-valentin-windows-{latest}',
                                 'user'))
                print(
                    f'user directory from {installed} copied to {latest}')
        tar.extractall(INSTALL_DIR)
    else:
        print('You have the latest version.')

    subprocess.Popen([
        os.path.join(INSTALL_DIR,
                     f'citra-valentin-windows-{latest}',
                     'citra-valentin-qt.exe')
    ] + sys.argv[1:])


if __name__ == '__main__':
    main()
