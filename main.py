#!/usr/bin/env python

import argparse
import errno
import os
import os.path
from deluge_client import DelugeRPCClient


def is_valid_host(parser, host_str):
    """
    Check the validity of the host string arguments
    """
    params = host_str.split(':')
    if len(params) == 4:
        params[1] = int(params[1])
        return params
    parser.error("The host string %s is not valid!" % host_str)


def is_valid_directory(parser, location):
    """
    Check the validity of the directory argument
    """
    if not os.path.isdir(location):
        parser.error("Directory %s is not valid!" % location)
    return location


def listdir_fullpath(loc):
    """
    Helper to get the list directories with full paths
    """
    return [os.path.join(loc, f) for f in os.listdir(loc)]


def recursive_rm_dir(path):
    """
    Remove a directory that contains symlink in it
    """
    if not os.path.isdir(path):
        return
    for entry in listdir_fullpath(path):
        if os.path.islink(entry):
            os.unlink(entry)
    if not os.listdir(path):
        os.rmdir(path)



def main():
    """
    Entry function
    """
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument(
        '-d', '--dir', type=lambda x: is_valid_directory(parser, x),
        help='the directory to hold the file structure', required=True
    )
    parser.add_argument(
        'hosts', metavar='H', type=lambda x: is_valid_host(parser, x),
        nargs='+', help='the Deluge hosts'
    )
    args = parser.parse_args()

    tracker_map = {}
    clients = []

    for entry in listdir_fullpath(args.dir):
        recursive_rm_dir(entry)

    for host in args.hosts:
        client = DelugeRPCClient(*host)
        client.connect()

        clients.append(client)

        torrents = client.call(
            'core.get_torrents_status',
            {},
            ['name', 'save_path', 'tracker_host']
        )

        for _, torrent in torrents.items():
            if torrent[b'tracker_host'] not in tracker_map:
                tracker_map[torrent[b'tracker_host'].decode('utf-8')] = []
            tracker_map[torrent[b'tracker_host'].decode('utf-8')].append(torrent)

        for tracker, torrents in tracker_map.items():
            loc = os.path.join(args.dir, tracker)
            if not os.path.exists(loc):
                os.makedirs(loc)
            for torrent in torrents:
                link_from = os.path.join(loc, torrent[b'name'].decode('utf-8'))
                link_to = os.path.join(
                    torrent[b'save_path'].decode('utf-8'),
                    torrent[b'name'].decode('utf-8')
                )
                if not os.path.exists(link_from):
                    try:
                        os.symlink(link_to, link_from)
                    except OSError as error:
                        if error.errno == errno.EEXIST:
                            os.remove(link_from)
                            os.symlink(link_to, link_from)
                        else:
                            raise error


if __name__ == '__main__':
    main()
