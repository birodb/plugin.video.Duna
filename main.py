# -*- coding: utf-8 -*-
# Module: default
# Author: B.D.B.
# Credit: romanvm - author of original video plugin sample
# Created on: 28.04.2019
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""
Example video plugin for online streams
"""

# Enable unicode strings by default as in Python 3
#from __future__ import unicode_literals
# Monkey-patch standard libary names to enable Python 3-like behavior
#from future import standard_library
#standard_library.install_aliases()
#from future.utils import iterkeys
# The above strings provide compatibility layer for Python 2
# so the code can work in both versions.
# In Python 3 they do nothing and can be safely removed.
# Normal imports for your addon:

import sys
import json
import re
import os
import xml.etree.ElementTree as ET

from html.parser import HTMLParser
from http.cookiejar import CookieJar

import urllib.request
import urllib.parse
import urllib.error
from urllib.request import build_opener, HTTPCookieProcessor, Request
from urllib.parse import urlencode, parse_qsl

from pathlib import Path
from datetime import date, time, datetime, timedelta

import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui


# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

cs_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_3 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B329 Safari/8536.25"

def get_url(**kwargs):
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
	#opener.addheaders = {'User-agent':'Custom user agent'}
	#opener.version = cs_agent
    p = MyHTMLParser()
    try:
        request = Request(url)
        response = opener.open(request)
        p.feed(response.read().decode('utf-8'))
        response.close()
        d = p.player_data[0]
        token_id = d.get('streamId')
        if not token_id:
            token_id = d.get('token')
			#contentid={0}
        url = '{}/player.php?video={}&noflash=yes&osfamily=OS%20X&osversion=10.13&browsername=Firefox&browserversion=60.0&title=Duna&embedded=0'.format(p.player_js.split('/js')[0], token_id)
        #print(url)
        request = Request(url)
        response = opener.open(request)
        p.feed(response.read().decode('utf-8'))
        response.close()
    except (OSError, IOError, RuntimeError) as e:
        dlg = xbmcgui.Dialog()
        dlg.ok('Error', str(e))
        raise e
    return p.stream_url
#[1,2,30,34,33,3,4]
CHANNELS = [
        {'name': 'DunaTV', 'id': 'dunalive', 'id2': 'duna-elo', 'num': '3'},
        {'name': 'DunaWorld', 'id': 'dunaworldlive', 'id2': 'duna-world-elo', 'num': '4'},
        {'name': 'MTV1', 'id': 'mtv1live', 'id2': 'm1-elo', 'num': '1'},
        {'name': 'MTV2', 'id': 'mtv2live', 'id2': 'm2-elo', 'num': '2'},
        {'name': 'MTV4', 'id': 'mtv4live', 'id2': 'm4-elo', 'num': '30'},
        {'name': 'MTV4+', 'id': 'mtv4live', 'id2': 'm4-sport-plusz-elo', 'num': '34'},
        {'name': 'MTV5', 'id': 'mtv5live', 'id2': 'm5-elo', 'num': '33'}
        ]


# Free sample videos are provided by www.vidsplay.com
# Here we use a fixed set of properties simply for demonstrating purposes
# In a "real life" plugin you will need to get info and links to video files/streams
# from some web-site or online service.


def list_categories():
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
    xbmcplugin.addDirectoryItem(_handle, get_url(action='search'), list_item, is_folder)
    xbmcplugin.endOfDirectory(_handle)


def list_videos(category):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: Category name
    :type category: str
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, category)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get the list of videos in the category.
    videos = {} # get_videos(category)
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['name'])
        # Set additional info for the list item.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': video['name'],
                                    'genre': video['genre'],
                                    'mediatype': 'video'})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
        url = get_url(action='play', video=video['video'])
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def play_video(path, video_info):
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

def search_items():
    kb = xbmc.Keyboard()
    kb.doModal()
    if kb.isConfirmed():
        '''Host: mediaklikk.hu
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
'''

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
        #opener.addheaders = {'User-agent':'Custom user agent'}
        #opener.version = cs_agent
        resp = '[]'
        try:
            request = Request(url)#, urlencode(p))
            response = opener.open(request)
            resp = response.read().decode('utf-8')
            response.close()
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
                xbmcplugin.addDirectoryItem(_handle, get_url(action='play', video='https:' + src['URL']), list_item, is_folder)
        xbmcplugin.endOfDirectory(_handle)


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
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            list_videos(params['category'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(get_stream_url(params['video']), params.get('video_info', {}))
        elif params['action'] == 'search':
            # Play a video from a provided URL.
            #play_video(get_stream_url(params['video']))
            search_items()
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()

# setup
this_addon = xbmcaddon.Addon()
cs_name = this_addon.getAddonInfo("id")
cs_profile = this_addon.getAddonInfo("profile")
cs_file = os.path.join(xbmc.translatePath("special://temp"), cs_name + ".session")
cs_delay = 5

class CsatornakURLopener(urllib.request.FancyURLopener):
    version = cs_agent

urllib.request._urlopener = CsatornakURLopener()
def load_page(pg_url):
    # load and parse stream
    # print("Loading: " + pg_url)
    page = urllib.request.urlopen(pg_url)
    page_content = page.read()
    page.close()
    return page_content

def add_live_tv(c):
    today = date.today()
    now = datetime.now()
    prg_content = None
    profile_path = Path(xbmc.translatePath( cs_profile ).decode("utf-8"))
    local_prg_fname = profile_path / 'broadcast_{0}.xml'.format(c['num'])
    if local_prg_fname.exists() and date.fromtimestamp(local_prg_fname.fstat().st_mtime) == today:
        with local_prg_fname.open('rt') as f:
            prg_content = f.read()
    else: #if not prg_content:
        prg_url = 'https://www.mediaklikk.hu/iface/broadcast/{0}/broadcast_{1}.xml'.format(str(today), c['num'])
        prg_content = load_page(prg_url)
        with local_prg_fname.open('wt') as f:
            f.write(prg_content)
    root = ET.fromstring(prg_content)
    cnt = 0
    for item in root.iter('Item'):
        start_date = None
        date_xml = item.find('Date')
        if date_xml is not None and date_xml.text is not None:
            start_date = datetime(*(time.strptime(date_xml.text, '%Y-%m-%d %H:%M:%S')[0:6]))
        length_xml = item.find('Length')
        play_dt = None
        if length_xml is not None and length_xml.text is not None:
            t = time.strptime(length_xml.text, '%H:%M:%S')
            play_dt = timedelta(hours=t.tm_hour, minutes=t.tm_min, seconds=t.tm_sec)
        #if start_date > now:
        #    continue
        if now - start_date > play_dt:
            continue
        title_xml = item.find('SeriesTitle')
        if title_xml is None or title_xml.text is None:
            title_xml = item.find('Title')
        title = str(title_xml.text)
        descr_xml = item.find('Description')
        description = None
        if descr_xml is not None and descr_xml.text is not None:
            description = str(descr_xml.text)
        #title += '.'
        #for child in item:
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
        url = get_url(action='play', video='https://www.mediaklikk.hu/{}/'.format(c['id2']), video_info=video_info)
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

        cnt = cnt + 1
        if cnt > 2:
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


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
    #print "Session: " + cs_file

    # tries to limit deadlocks due to multiple runs
    # fcntl for file locking may not be available on some platforms
    #if os.path.exists(cs_file) and time.time() - os.path.getmtime(cs_file) < cs_delay:
    #	print "Recently ran, exiting."
    #	sys.exit(0)
    #else:
    #	with open(cs_file, "a+"):
    #	os.utime(cs_file, None)

    #cs_player = xbmc.Player()

    # stop playing and wait
    #cs_player.stop()
    #while cs_player.isPlaying():
    #	xbmc.sleep(10)
