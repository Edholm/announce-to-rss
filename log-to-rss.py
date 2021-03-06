#!/usr/bin/env python
# Takes an announce log and outputs an RSS feed/file

import argparse as ap
import ast
import pyinotify as pyi
import subprocess
from datetime import datetime

rss_template = """<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
<channel>
    <title>{title}</title>
    <link>{link}</link>
    <description>{desc}</description>
{items}
</channel>
</rss>
"""

item_template = """<item>
    <title>{title}</title>
    <link>{link}</link>
    <description>{desc}</description>
    <pubDate>{desc}</pubDate>
</item>
"""


def tail(log, lines_wanted):
    lines_wanted = abs(lines_wanted)
    buffer = 400  # Probable size of each line
    i = -1 * lines_wanted
    tmp = []
    with open(log, 'rb') as f:
        filesize = f.seek(0, 2)
        while len(tmp)+1 <= lines_wanted:
            offset = buffer*i
            if abs(offset) > filesize:
                f.seek(0, 0)  # Beginning of file
                tmp = f.readlines()
                break
            else:
                f.seek(offset, 2)
                # The first line is probably "incomplete"
                tmp = f.readlines()[1:]
            i -= 1
    return [x.decode('utf-8') for x in tmp[len(tmp)-lines_wanted:]]


def lines_to_dicts(lines):
    return [ast.literal_eval(x) for x in lines]


def dicts_to_xml(dict_items):
    # Sort by datetime first
    items_sorted = sorted(dict_items, reverse=True, key=lambda x: x['datetime'])
    items = [item_template.format(title=x['title'],
                                  link=x['url'],
                                  desc=x['datetime']) for x in items_sorted]
    return "".join(items)


def write_rss(items, args):
    vprint('Writing to ' + args.output, args)
    with open(args.output, 'w') as f:
        f.write(rss_template.format(title=args.title, link=args.link,
                                    desc=args.description, items=items))


def process_file(log, lines_wanted):
    lines = tail(log, lines_wanted)
    return lines_to_dicts(lines)


def process_update(args):
    vprint('Processing file update', args)
    items = []
    for log in args.logfiles:
        items.extend(process_file(log, args.num))
    write_rss(dicts_to_xml(items), args)

    if args.cmd:
        vprint('Executing post-command', args)
        subprocess.call(args.cmd, shell=True)


def vprint(msg, args):
    if args.verbose:
        print("{} - {}".format(datetime.now(), msg))


class EventHandler(pyi.ProcessEvent):
    def __init__(self, args):
        self.args = args

    def process_IN_CLOSE_WRITE(self, event):
        vprint(event.path + ' has been updated...', self.args)
        process_update(self.args)


if __name__ == '__main__':
    parser = ap.ArgumentParser(description='Parse announce logs and output RSS file.')
    parser.add_argument('logfiles', metavar='LOG', type=str, nargs='+',
                        help='Input logfiles to parse')
    parser.add_argument('-o', '--output', dest='output', metavar='PATH', default='announce.xml',
                        help='where to store the finished RSS XML')
    parser.add_argument('-t', '--title', dest='title', metavar='STR', default='RSS Feed',
                        help='The RSS title attribute')
    parser.add_argument('-l', '--link', dest='link', metavar='URL', default='localhost',
                        help='Specify the RSS link attribute')
    parser.add_argument('-d', '--desc', dest='description', metavar='STR', default='RSS Feed',
                        help='Description attribute')
    parser.add_argument('-n', '--num', dest='num', metavar='INT', type=int, default='50',
                        help='Number of items to fetch')
    parser.add_argument('-w', '--watch', dest='watch', action='store_true',
                        default=False, help='Watch the input files for changes using inotify')
    parser.add_argument('-c', '--cmd', dest='cmd',
                        help='Command to execute after successful RSS write')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()
    process_update(args)

    if args.watch:
        wm = pyi.WatchManager()
        handler = EventHandler(args)

        notifier = pyi.Notifier(wm, handler)
        for log in args.logfiles:
            vprint('Starting watch on ' + log, args)
            wm.add_watch(log, pyi.IN_CLOSE_WRITE)
        notifier.loop()
