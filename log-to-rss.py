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


def tail(args):
    logfiles = args.logfiles
    lines = []

    for log in logfiles:
        lines_wanted = abs(args.num)
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

            lines.extend([x.decode('utf-8') for x in tmp])
    return lines


def lines_to_dict(lines):
    return [ast.literal_eval(x) for x in lines]


def items_to_xml(dict_items):
    # Sort by datetime first
    items_sorted = sorted(dict_items, reverse=False, key=lambda x: x['datetime'])
    items = [item_template.format(title=x['title'],
                                  link=x['url'],
                                  desc=x['datetime']) for x in items_sorted]
    return "".join(items)


def write_rss(items, args):
    with open(args.output, 'w') as f:
        f.write(rss_template.format(title=args.title, link=args.link,
                                    desc=args.description, items=items))


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

    args = parser.parse_args()
    lines = tail(args)
    dicts = lines_to_dict(lines)
    items = items_to_xml(dicts)
    write_rss(items, args)
