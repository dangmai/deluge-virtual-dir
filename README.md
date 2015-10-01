deluge-virtual-dir
==================

This program is used to set up a virtual directory structure that points to my [Deluge](http://deluge-torrent.org/) download directory,
grouped by the trackers.

Example
-------

Deluge downloads the torrent `Test Torrent` from `what.cd` to `/home/user/Downloads`,
then we can use the command `python main.py host:port:username:password --dir /home/user/Links`
to symlink `/home/user/Links/what.cd/Test Torrent` to `home/user/Downloads/Test Torrent`

Usage
-----

The script has the following required arguments:

- One or more host strings in the form of `host:port:username:password`.
If more than 1 host strings are used, separate them by a `space` character.

- `--dir`: The directory to hold the directory structure