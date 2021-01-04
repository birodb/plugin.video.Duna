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
import xml.etree.ElementTree as ET

from html.parser import HTMLParser
from http.cookiejar import CookieJar

from urllib.request import build_opener, HTTPCookieProcessor, Request
from urllib.parse import urlencode, parse_qsl

from pathlib import Path
from datetime import date, datetime, timedelta

import xbmc
import xbmcvfs
import xbmcaddon
import xbmcplugin
import xbmcgui


CS_AGENT = ' '.join(["Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_3 like Mac OS X)",
                     "AppleWebKit/536.26 (KHTML, like Gecko)",
                     "Version/6.0 Mobile/10B329 Safari/8536.25"])

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

class MyHTMLParser(HTMLParser):
    """scrape the program and web player pages"""
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
#https://player.mediaklikk.hu/playernew/player.php?video=mtv1live&noflash=yes&osfamily=OS X&osversion=10.14&browsername=Firefox&browserversion=66.0&title=M1&contentid=mtv1live&embedded=0
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


class PluginDunaTV:
    """the scraper and xbmc list provider video plugin"""
    def __init__(self, argv):
        self.base_url = argv[0]
        self.addon = xbmcaddon.Addon(self.base_url.split('/')[-2])
        self.profile_path = Path( xbmcvfs.translatePath(self.addon.getAddonInfo("profile")))
        self.handle = int(argv[1])
        # We use string slicing to trim the leading '?' from the plugin call paramstring
        paramstr = argv[2][1:]
        # Parse a URL-encoded paramstring to the dictionary of
        # {<parameter>: <value>} elements
        self.params = dict(parse_qsl(paramstr))
        self.cj = CookieJar()
        self.opener = build_opener(HTTPCookieProcessor(self.cj))


    def build_url(self, **kwargs):
        """
        Create a URL for calling the plugin recursively from the given set of keyword arguments.

        :param kwargs: "argument=value" pairs
        :return: plugin call URL
        :rtype: str
        """
        return '{0}?{1}'.format(self.base_url, urlencode(kwargs))


    @staticmethod
    def read_response_decoded(response):
        buff = response.read()
        encoding = response.headers.get_content_charset(failobj='utf-8')
        return buff.decode(encoding)


    def load_page_decoded(self, url):
        """load page data"""
        request = Request(url, headers=REQ_HEADERS)
        with self.opener.open(request) as response:
            return PluginDunaTV.read_response_decoded(response)


    def route(self):
        """
        Router function that calls other functions
        depending on the provided paramstring
        """
        # Check the parameters passed to the plugin
        if not self.params:
            # If the plugin is called from Kodi UI without any parameters,
            # display fill the list of video entries
            self.action_initial_fill()
        elif self.params['action'] == 'play':
            # Play a video from a provided URL.
            self.action_play_video()
        elif self.params['action'] == 'search':
            # Play a video from a provided URL.
            self.action_search_items()
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid params: {0}!'.format(self.params))


    def action_play_video(self):
        """
        Play program video with url extracted from the web-player.
        """
        stream_url = self.retrieve_stream_url(self.params['video'])
        video_info = self.params.get('video_info', {})
        # Create a playable item with a path to play.
        play_item = xbmcgui.ListItem(path=stream_url)
        play_item.setInfo('video', video_info)
        # Pass the item to the Kodi player.
        xbmcplugin.setResolvedUrl(self.handle, True, listitem=play_item)


    def retrieve_stream_url(self, web_url):
        """retrieve the stream url from the webplayer for the program """
        html_parser = MyHTMLParser()
        try:
            program_site = self.load_page_decoded(web_url)
            html_parser.feed(program_site)
            d = html_parser.player_data[0]
            token_id = d.get('streamId')
            if not token_id:
                token_id = d.get('token')
            webplayer_url = '{}/player.php?video={}&noflash=yes&osfamily=OS%20X&osversion=10.13&browsername=Firefox&browserversion=60.0&title=Duna&embedded=0'.format(p.player_js.split('/js')[0], token_id)
            webplayer_site = self.load_page_decoded(webplayer_url)
            html_parser.feed(webplayer_site)
        except (OSError, IOError, RuntimeError) as e:
            dlg = xbmcgui.Dialog()
            dlg.ok('Error', str(e))
            raise e
        return html_parser.stream_url

    def action_search_items(self):
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
            search_resp = '[]'
            try:
                search_url='https://www.mediaklikk.hu/wp-content/plugins/hms-mediaklikk/interfaces//get_results.php?{}'.format(urlencode(p))
                search_resp = self.load_page_decoded(search_url)
            except (OSError, IOError, RuntimeError) as e:
                dlg = xbmcgui.Dialog()
                dlg.ok('Error', str(e))
                raise e
            try:
                r = json.loads(search_resp)
            except ValueError as e:
                dlg = xbmcgui.Dialog()
                dlg.ok('Error', str(e))
                raise e
            # is_folder = False means that this item won't open any sub-list.
            is_folder = False
            if isinstance(r, list) and len(r) == 1:
                r = r[0]
            else:
                raise RuntimeError(search_url +'\n'+resp)
            if isinstance(r, dict) and 'data' in r:
                r = r['data']
            else:
                raise RuntimeError(search_url +'\n'+resp)
            if isinstance(r, dict) and 'items' in r:
                r = r['items']
            else:
                raise RuntimeError(search_url +'\n'+resp)
            if isinstance(r, list):# and len(r) == 1:
                #r = r[0]
                pass
            else:
                raise RuntimeError(search_url +'\n'+resp)
            for i in r:
                src = i.get('source', {})
                title = i.get('post_title','')
                if 'URL' in src:
                    list_item = xbmcgui.ListItem(label=title)
                    list_item.setInfo('video', {'title': title})
                    list_item.setProperty('IsPlayable', 'true')
                    # Create a URL for a plugin recursive call.
                    # Add our item to the Kodi virtual folder listing.
                    xbmcplugin.addDirectoryItem(self.handle, self.build_url(action='play', video='https:' + src['URL']), list_item, is_folder)
            xbmcplugin.endOfDirectory(self.handle)

    # In a "real life" plugin you will need to get info and links to video files/streams
    # from some web-site or online service.
    def action_initial_fill(self):
        """
        Create the list of video categories in the Kodi interface.
        """
        # Set plugin category. It is displayed in some skins as the name
        # of the current section.
        xbmcplugin.setPluginCategory(self.handle, 'Mediaklikk Video Collection')
        # Set plugin content. It allows Kodi to select appropriate views
        # for this type of content.
        xbmcplugin.setContent(self.handle, 'videos')
        # Iterate through categories
        for channel in CHANNELS:
            self.add_live_tv(channel)
        # Add a sort method for the virtual folder items (alphabetically, ignore articles)
        # xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        # Finish creating a virtual folder.

        list_item = xbmcgui.ListItem(label='Search')
        list_item.setInfo('video', {'title': 'Search'})
        # Create a URL for a plugin recursive call.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(self.handle, self.build_url(action='search'), list_item, is_folder)
        xbmcplugin.endOfDirectory(self.handle)


    def add_live_tv(self, c):
        """ add current and upcoming entries for live tv channel """
        today = date.today()
        now = datetime.now()
        prg_content = None
        local_prg_fname = self.profile_path / 'broadcast_{0}.xml'.format(c['num'])

        if local_prg_fname.exists() and date.fromtimestamp(local_prg_fname.stat().st_mtime) == today:
            with local_prg_fname.open('rb') as f:
                buff = f.read()
                if buff:
                    prg_content = buff.decode('utf-8')
        else:
            prg_url = 'https://www.mediaklikk.hu/iface/broadcast/{0}/broadcast_{1}.xml'.format(str(today), c['num'])
            try:
                prg_content = self.load_page_decoded(prg_url)
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
            if not start_date or not play_dt or now - start_date > play_dt:
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
            url = self.build_url(action='play', video='https://www.mediaklikk.hu/{}/'.format(c['id2']), video_info=video_info)
            # Add the list item to a virtual Kodi folder.
            # is_folder = False means that this item won't open any sub-list.
            is_folder = False
            # Add our item to the Kodi virtual folder listing.
            xbmcplugin.addDirectoryItem(self.handle, url, list_item, is_folder)

            cnt = cnt + 1
            if cnt > 4:
                break




if __name__ == '__main__':
    xbmc.log('__main__ reached: ' + str(sys.argv), level=xbmc.LOGINFO)
    #Create a plugin with the parameters passed to it.
    this_plugin = PluginDunaTV(sys.argv)
    #Call the router function.
    this_plugin.route()
