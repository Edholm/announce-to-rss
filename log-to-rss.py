#!/usr/bin/env python
# Takes an announce log and outputs an RSS feed/file

import argparse as ap

rss_template = """<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
<channel>
    <title>{title}</title>
    <link>{link}</link>
    <description>{desc}</description>
{items}
</channel>
"""


def read_items(args):
    pass


def items_to_xml(items):
    pass


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

    args = parser.parse_args()
    items = items_to_xml(read_items(args))
    write_rss(items, args)
