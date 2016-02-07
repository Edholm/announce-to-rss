#!/usr/bin/env python
# Takes an announce log and outputs an RSS feed/file

import argparse as ap
import ast

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
    items = [item_template.format(title=x['title'],
                                  link=x['url'],
                                  desc=x['datetime']) for x in items_sorted]
    return "".join(items)


def write_rss(items, args):
    with open(args.output, 'w') as f:
        f.write(rss_template.format(title=args.title, link=args.link,
                                    desc=args.description, items=items))


def process_file(log, lines_wanted):
    lines = tail(log, lines_wanted)
    return lines_to_dicts(lines)

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

    args = parser.parse_args()
    items = []
    for log in args.logfiles:
        items.extend(process_file(log, args.num))

    # Sort by datetime first
    items_sorted = sorted(items, reverse=True, key=lambda x: x['datetime'])
    write_rss(dicts_to_xml(items_sorted), args)
