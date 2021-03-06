#!/usr/bin/python
# Log PRIVMSG from announcers to file in a JSON-like syntax
#

import weechat as w
import re
from datetime import datetime

name = "log-announcers"
author = "Emil Edholm"
version = "1.1"
license = "GPL3"
desc = "Log PRIVMSG from announcers to file in a JSON-like format"
debug = False

tl_regex = re.compile(".+<(.+)>  Name:'(.+)' uploaded by .+ -  https?://.+/torrent/(.+)")
scc_regex = re.compile('.* (.+?): -> (.+?) \(.+?\).*\?id=(.+)\)')
tl_url_template = 'http://www.torrentleech.org/rss/download/{id}/{access}/{name}.torrent'
scc_url_template = 'https://sceneaccess.eu/download/{id}/{access}/{name}.torrent'

def_settings = {
    'tl_access_key': 'key-goes-here',        # RSS access key
    'scc_access_key': 'key-goes-here',       #
    'tl_log_path': '/tmp/scc-announce.log',  # Where to store the log file of TL announces
    'scc_log_path': '/tmp/tl-announce.log',  # Where to store the log file of SCC announces
    'cat_filter': '',                        # comma sep list of cats to filter.
    'channel_filter': '',                    # comma sep list of channels to watch
    } # FIXME: user-filter and parser who the uploader were...


def is_accepted_buffer(buffer):
    chan_filter = w.config_get_plugin('channel_filter')
    chans = list(filter(None, chan_filter.split(',')))
    if len(chans) == 0:
        # If user hasn't specified any filters, allow everything
        return True

    buff_name = w.buffer_get_string(buffer, "short_name")
    return buff_name in chans


def read_privmsg(data, buffer, date, tags, displayed, highlight, sender, message):
    if not is_accepted_buffer(buffer):
        debug_prnt('Ignoring filtered channel/buffer')
        return w.WEECHAT_RC_ERROR
    debug_prnt('Trying to match...')
    tl_msg = match_msg(sender, message, tl_regex)
    scc_msg = match_msg(sender, message, scc_regex)

    if tl_msg:
        acc_key = w.config_get_plugin('tl_access_key')
        path = w.config_get_plugin('tl_log_path')
        tl_msg['url'] = make_url(tl_msg, tl_url_template, acc_key)
        log(tl_msg, path)
    if scc_msg:
        acc_key = w.config_get_plugin('scc_access_key')
        path = w.config_get_plugin('scc_log_path')
        scc_msg['url'] = make_url(scc_msg, scc_url_template, acc_key)
        log(scc_msg, path)

    return w.WEECHAT_RC_OK


def match_msg(sender, message, regx):
    match = regx.match(message)
    if not match:
        return None

    groups = match.groups()
    return {
        'sender': sender,
        'category': groups[0],
        'id': groups[2],
        'title': groups[1].replace(' ', '.'),
        'datetime': str(datetime.now()),
        } if groups else None


def make_url(msg, template, key):
    return template.format(id=msg['id'], access=key, name=msg['title'])


def log(msg, path):
    filters = w.config_get_plugin('cat_filter')
    if len(filters) > 0:
        if msg['category'] not in filters.split(','):
            debug_prnt('Ignoring category "' + msg['category'] + '"')
            return

    debug_prnt('Logging new msg: ' + str(msg))
    with open(path, 'a') as log:
        log.write(str(msg) + '\n')


def debug_prnt(msg):
    if debug:
        w.prnt("", msg)


if __name__ == '__main__':
    if w.register(name, author, version, license, desc, '', ''):
        # w.hook_config("plugins.var.python." + name + ".*", "config_cb", "")
        w.hook_print("", "irc_privmsg", "", True, "read_privmsg", "")

        # Set the default settings
        for k, v in def_settings.items():
            if not w.config_is_set_plugin(k):
                w.config_set_plugin(k, v)
