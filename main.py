# -*- coding: utf-8 -*-
# Module: default
# Author: B.D.B.
# Credit: romanvm - author of original video plugin sample
# Created on: 28.04.2019
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""
Example video plugin for online streams
"""

import sys
import json
import re
import os
import xml.etree.ElementTree as ET

from html.parser import HTMLParser
from http.cookiejar import CookieJar

from urllib.request import build_opener, HTTPCookieProcessor, urlopen, Request
from urllib.parse import urlencode, parse_qsl

from pathlib import Path
from datetime import date, time, datetime, timedelta

import xbmc
import xbmcvfs
import xbmcaddon
import xbmcplugin
import xbmcgui


CS_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_3 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B329 Safari/8536.25"
REQ_HEADERS = {'User-Agent': CS_AGENT}

#[1,2,30,34,33,3,4]
CHANNELS = [
        {'name': 'Duna', 'id': 'dunalive', 'id2': 'duna-elo', 'num': '3'},
        {'name': 'DunaWorld', 'id': 'dunaworldlive', 'id2': 'duna-world-elo', 'num': '4'},
        {'name': 'M1', 'id': 'mtv1live', 'id2': 'm1-elo', 'num': '1'},
        {'name': 'M2', 'id': 'mtv2live', 'id2': 'm2-elo', 'num': '2'},
        {'name': 'M4', 'id': 'mtv4live', 'id2': 'm4-elo', 'num': '30'},
        {'name': 'M4+', 'id': 'mtv4live', 'id2': 'm4-sport-plusz-elo', 'num': '34'},
        {'name': 'M5', 'id': 'mtv5live', 'id2': 'm5-elo', 'num': '33'}
        ]


def mk_request(url):
    return Request(url, headers=REQ_HEADERS)

def read_response_text(response):
    return response.read().decode(response.headers.get_content_charset(failobj='utf-8'))

def load_page(pg_url):
    """load page data"""
    with urlopen(mk_request(pg_url)) as response:
        return read_response_text(response)

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])
# setup
this_addon = xbmcaddon.Addon()
#cs_name = this_addon.getAddonInfo("id")
PROFILE_PATH = Path(xbmcvfs.translatePath( this_addon.getAddonInfo("profile") ))

#cs_file = os.path.join(xbmcvfs.translatePath("special://temp"), cs_name + ".session")


def mk_plugin_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))


class MyHTMLParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.curr_tag = None
        self.player_data = []
        self.player_js = None
        self.stream_url = ""

    def handle_starttag(self, tag, attrs):
        self.curr_tag = tag
        if tag == "script":
            if attrs:
                src = dict(attrs).get("src", "")
                if "player.js" in src:
                    #print("Encountered a start tag:", tag, attrs)
                    self.player_js = src

    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        pass

    def handle_data(self, data):
        if self.curr_tag == "script":
            if "mtva_player_" in data:
                for i in re.finditer('[^\\{]*(\\{[^;]+)\\);', data):
                    pl = json.loads(i.group(1))
                    self.player_data.append(pl)
                    #print("Encountered some data  :", json.dumps(pl))
            elif "pl.setup" in data:
                for i in re.finditer('pl.setup\\(\\s*(\\{[^;]+)\\);', data):
                    setup_data = json.loads(i.group(1))
                    pl = setup_data.get('playlist', [])
                    self.stream_url = 'https:' + pl[1 if len(pl) > 1 else 0]['file']
                    #self.player_data.append(pl)
                    #print("Encountered some data  :", json.dumps(setup_data))

def get_stream_url(url):
    #print(url)
    cj = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cj))
    p = MyHTMLParser()
    try:
        request = mk_request(url)
        with opener.open(request) as response:
            p.feed(read_response_text(response))
        d = p.player_data[0]
        token_id = d.get('streamId')
        if not token_id:
            token_id = d.get('token')
			#contentid={0}
        url = '{}/player.php?video={}&noflash=yes&osfamily=OS%20X&osversion=10.13&browsername=Firefox&browserversion=60.0&title=Duna&embedded=0'.format(p.player_js.split('/js')[0], token_id)
        #print(url)
        request = mk_request(url)
        with opener.open(request) as response:
            p.feed(read_response_text(response))
    except (OSError, IOError, RuntimeError) as e:
        dlg = xbmcgui.Dialog()
        dlg.ok('Error', str(e))
        raise e
    return p.stream_url

# In a "real life" plugin you will need to get info and links to video files/streams
# from some web-site or online service.
def action_initial_fill():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, 'Mediaklikk Video Collection')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Iterate through categories
    for channel in CHANNELS:
        add_live_tv(channel)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    # xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.

    list_item = xbmcgui.ListItem(label='Search')
    list_item.setInfo('video', {'title': 'Search'})
    # Create a URL for a plugin recursive call.
    # is_folder = False means that this item won't open any sub-list.
    is_folder = True
    # Add our item to the Kodi virtual folder listing.
    xbmcplugin.addDirectoryItem(_handle, mk_plugin_url(action='search'), list_item, is_folder)
    xbmcplugin.endOfDirectory(_handle)


def action_play_video(path, video_info):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    play_item.setInfo('video', video_info)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def action_search_items():
    """
    Host: mediaklikk.hu
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:70.0) Gecko/20100101 Firefox/70.0
    Accept: application/json, text/javascript, */*; q=0.01
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate, br
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    X-Requested-With: XMLHttpRequest
    Content-Length: 132
    Origin: https://mediaklikk.hu
    DNT: 1
    Connection: keep-alive
    Referer: https://mediaklikk.hu/talalati-lista
    Cookie: __gfp_64b=xxxx.m7; _ga=GA1.; SERVERID=mtvacookieA
    Pragma: no-cache
    Cache-Control: no-cache

    action=search&s_type=all&keyword=matrica&fromDate=2013-01-01&toDate=2019-11-24&skippedPageElements=undefined&pageSize=5&pageNumber=1
    """
    kb = xbmc.Keyboard()
    kb.doModal()
    if kb.isConfirmed():
        p = {
            'action': 'search',
            #'s_type': 'all',
            's_type': 'video',
            'keyword':  kb.getText(),
            'fromDate': '2013-01-01',
            'toDate': str( date.today() ),
            'skippedPageElements': 'undefined',
            'pageSize': 95,
            'pageNumber': 1
        }
        url='https://www.mediaklikk.hu/wp-content/plugins/hms-mediaklikk/interfaces//get_results.php?{}'.format(urlencode(p))
        cj = CookieJar()
        opener = build_opener(HTTPCookieProcessor(cj))
        resp = '[]'
        try:
            request = mk_request(url)#, urlencode(p))
            with opener.open(request) as response:
                resp = read_response_text(response)
        except (OSError, IOError, RuntimeError) as e:
            dlg = xbmcgui.Dialog()
            dlg.ok('Error', str(e))
            raise e
        try:
            r = json.loads(resp)
        except ValueError as e:
            dlg = xbmcgui.Dialog()
            dlg.ok('Error', str(e))
            raise e
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        if isinstance(r, list) and len(r) == 1:
            r = r[0]
        else:
            raise RuntimeError(url +'\n'+resp)
        if isinstance(r, dict) and 'data' in r:
            r = r['data']
        else:
            raise RuntimeError(url +'\n'+resp)
        if isinstance(r, dict) and 'items' in r:
            r = r['items']
        else:
            raise RuntimeError(url +'\n'+resp)
        if isinstance(r, list):# and len(r) == 1:
            #r = r[0]
            pass
        else:
            raise RuntimeError(url +'\n'+resp)
        for i in r:
            src = i.get('source', {})
            title = i.get('post_title','')
            if 'URL' in src:
                list_item = xbmcgui.ListItem(label=title)
                list_item.setInfo('video', {'title': title})
                list_item.setProperty('IsPlayable', 'true')
                # Create a URL for a plugin recursive call.
                # Add our item to the Kodi virtual folder listing.
                xbmcplugin.addDirectoryItem(_handle, mk_plugin_url(action='play', video='https:' + src['URL']), list_item, is_folder)
        xbmcplugin.endOfDirectory(_handle)


def add_live_tv(c):
    """ add current and upcoming entries for live tv channel """
    today = date.today()
    now = datetime.now()
    prg_content = None
    local_prg_fname = PROFILE_PATH / 'broadcast_{0}.xml'.format(c['num'])

    if local_prg_fname.exists() and date.fromtimestamp(local_prg_fname.stat().st_mtime) == today:
        with local_prg_fname.open('rb') as f:
            buff = f.read()
            if buff:
                prg_content = buff.decode('utf-8')
    else:
        prg_url = 'https://www.mediaklikk.hu/iface/broadcast/{0}/broadcast_{1}.xml'.format(str(today), c['num'])
        try:
            prg_content = load_page(prg_url)
        except (OSError, IOError, RuntimeError) as e:
            xbmc.log('Failed to load "' + prg_url + '" ' + str(e), level=xbmc.LOGINFO)
            pass
        profile_path.mkdir(parents=True, exist_ok=True)
        with local_prg_fname.open('wb') as f:
            if prg_content:
                f.write(prg_content.encode("utf-8"))
    if not prg_content:
         return
    root_xml = ET.fromstring(prg_content)
    cnt = 0
    for item_xml in root_xml.iter('Item'):
        start_date = None
        date_xml = item_xml.find('Date')
        if date_xml is not None and date_xml.text is not None:
            xbmc.log(date_xml.text, level=xbmc.LOGINFO)
            start_date = datetime.strptime(date_xml.text, '%Y-%m-%d %H:%M:%S')
        play_dt = None
        length_xml = item_xml.find('Length')
        if length_xml is not None and length_xml.text is not None:
            t = datetime.strptime(length_xml.text, '%H:%M:%S')
            play_dt = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        if now - start_date > play_dt:
            continue
        title_xml = item_xml.find('SeriesTitle')
        if title_xml is None or title_xml.text is None:
            title_xml = item_xml.find('Title')
        title = str(title_xml.text)
        descr_xml = item_xml.find('Description')
        description = None
        if descr_xml is not None and descr_xml.text is not None:
            description = str(descr_xml.text)
        #title += '.'
        #for child in item_xml:
        #    if child.text:
        #        s +=  child.tag + ': ' + str(child.text) +'; '
        #xbmcgui.Dialog().ok(cs_name, s, json.dumps(sys.argv), str(today))
        play_min, play_sec = divmod(play_dt.seconds, 60)
        if play_min:
            name = '[{0}] {1} ({2}, {3}perc)'.format(c['name'], title, start_date.strftime('%H:%M'), play_min)
        else:
            name = '[{0}] {1} ({2}, {3:02}mp)'.format(c['name'], title, start_date.strftime('%H:%M'), play_sec)

        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=name)
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        #list_item.setArt({'thumb': VIDEOS[category][0]['thumb'],
        #				  'icon': VIDEOS[category][0]['thumb'],
        #				  'fanart': VIDEOS[category][0]['thumb']})
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        # 'mediatype' is needed for a skin to display info for this ListItem correctly.
        video_info = {'title': name, 'duration': play_dt.seconds, 'plot': description, 'mediatype': 'video'}
        list_item.setInfo('video', video_info)
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=https://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
        url = mk_plugin_url(action='play', video='https://www.mediaklikk.hu/{}/'.format(c['id2']), video_info=video_info)
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

        cnt = cnt + 1
        if cnt > 4:
            break


#liz = xbmcgui.ListItem(' '.join((cs_name, json.dumps(sys.argv), str(date.today())))))#'XBMC list Example Title')

# play stream
#xbmcgui.Dialog().ok(cs_name, json.dumps(sys.argv), str(date.today()))
#for i in CHANNELS:
#    add_live_tv(i)
#bmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
#BMC.Container.Update
#"""
#ttps://www.mediaklikk.hu/m1-elo
#tml/head/<script type='text/javascript' src='https://player.mediaklikk.hu/playernew/js/mtva-player.js?ver=3.6.1'></script>
# @param typeParam 'live', vagy 'vod'
#* @param streamIdParam Élőnél a stream identifier, vodnál a cdn path
#* @param baseUrlParam Oldal megtekintést gyűjtő interfész url-je
#
#""
#""
#ttps://player.mediaklikk.hu/playernew/js/mtva-player.js?ver=3.6.1
#       var defaultSetup = {
# ...
#             playerLoader: "player.php",
#           liveClass: ["mtva-player", "mtva-player-live"],
#           vodClass: ["mtva-player", "mtva-player-vod"]
#       };
#       var currentSetup = clone_object(defaultSetup);
#""
#""
#ttps://player.mediaklikk.hu/playernew/player.php?video=mtv1live&noflash=yes&osfamily=OS X&osversion=10.14&browsername=Firefox&browserversion=66.0&title=M1&contentid=mtv1live&embedded=0
#       <script>jwplayer.key="G1TfeXueehbr/n/4/MCAEQq/kWlgDr1vbiAgbbRu5HCfpFmI";</script>
#div id="player"></div>
#script>
#   var pl = jwplayer('player');
#   var _contentId = null;
##   pl.setup( {
#   "autostart": "true",
#   "width": "100%",
#   "aspectratio": "16:9",
#   "primary": "html5",
#   "advertising": {
#       "client": "vast"
#   },
#   "cast": {},
#   "playlist": [
#       {
#           "file": "\/\/c201-node61-cdn.connectmedia.hu\/1100\/294ac424d9e378e1723d021c4889bbbe\/5cac0a95\/index.m3u8?v=5i",
#           "type": "hls"
#       }
#   ]
# );
##""
#""
#ttps://www.mediaklikk.hu/cikk/2019/04/02/ide-kattintva-visszanezhetik-az-egynyari-kaland-elso-evadat/
#p><strong>1. rész: Beköltözés</strong></p>
#div class='hmsVideoPlayerWrapper'>
#div class='hmsArticleViewerVideo'>
#div id="player_81925_1" class="live-player-container"></div>
#<p><script defer type="text/javascript">
#				mtva_player_manager.player(document.getElementById("player_81925_1"), {"token":"U2FsdGVkX1%2B%2F635p7jQljbzG6a9v6vrE0mnSBqna0wIuavyQ73V5ah9DKXTf1LSFdevSodT%2B%2F9qmMQoXAHV5PqUXZ1xdf2OLKdbsAyNjIrn4KREoKvCOwPlKK1tn9sCXJPwH9YHi36O6qQ3zm3DQQKB7TownSWp7pp8RNX7KVFQ%3D","autostart":false,"debug":false,"bgImage":"\/\/mediaklikk.cms.mtv.hu\/wp-content\/uploads\/sites\/4\/2015\/04\/Egynyári-kaland-1.epizód-fotókredit-MTVA-Megafilm-Bara-Szilvia-6-e1554212213668-1024x576.jpg","adVastPreroll":"https:\/\/gemhu.adocean.pl\/ad.xml?id=VAAxe3zcXKSHojvBEJMZNkSV4cWy78e2KTpdrMG.iPP.r7\/aocodetype=1","title":"Egynyári kaland (1. széria, 1. rész), Beköltözés ","series":"Egyéb","contentId":838544,"embedded":true});
#</script></div>
#"""


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if not params:
        # If the plugin is called from Kodi UI without any parameters,
        # display fill the list of video entries
        action_initial_fill()
    elif params['action'] == 'play':
        # Play a video from a provided URL.
        action_play_video(get_stream_url(params['video']), params.get('video_info', {}))
    elif params['action'] == 'search':
        # Play a video from a provided URL.
        action_search_items()
    else:
        # If the provided paramstring does not contain a supported action
        # we raise an exception. This helps to catch coding errors,
        # e.g. typos in action names.
        raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
        

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    xbmc.log('Loaded: ' + str(sys.argv), level=xbmc.LOGINFO)

    router(sys.argv[2][1:])
