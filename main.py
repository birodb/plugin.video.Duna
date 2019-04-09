# -*- coding: utf-8 -*-
# Module: default
# Author: Biro D.B.
# Created on: 28.11.2014
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""
Example video plugin that is compatible with both Python 2 and 3

Compatibility features are provided by ``script.module.future`` library addon.
"""

# Enable unicode strings by default as in Python 3
from __future__ import unicode_literals
# Monkey-patch standard libary names to enable Python 3-like behavior
from future import standard_library
standard_library.install_aliases()
from future.utils import iterkeys
# The above strings provide compatibility layer for Python 2
# so the code can work in both versions.
# In Python 3 they do nothing and can be safely removed.
# Normal imports for your addon:
import sys
from urllib.parse import urlencode, parse_qsl
import xbmcgui
import xbmcplugin

from urllib.request import Request
from http.cookiejar import CookieJar
#cookiejar = cookiejar.CookieJar()
#opener = request.build_opener(request.HTTPCookieProcessor(cookiejar))

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

# Free sample videos are provided by www.vidsplay.com
# Here we use a fixed set of properties simply for demonstrating purposes
# In a "real life" plugin you will need to get info and links to video files/streams
# from some web-site or online service.
VIDEOS = {'Animals': [{'name': 'Crab',
                       'thumb': 'http://www.vidsplay.com/wp-content/uploads/2017/04/crab-screenshot.jpg',
                       'video': 'http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4',
                       'genre': 'Animals'},
                      {'name': 'Alligator',
                       'thumb': 'http://www.vidsplay.com/wp-content/uploads/2017/04/alligator-screenshot.jpg',
                       'video': 'http://www.vidsplay.com/wp-content/uploads/2017/04/alligator.mp4',
                       'genre': 'Animals'},
                      {'name': 'Turtle',
                       'thumb': 'http://www.vidsplay.com/wp-content/uploads/2017/04/turtle-screenshot.jpg',
                       'video': 'http://www.vidsplay.com/wp-content/uploads/2017/04/turtle.mp4',
                       'genre': 'Animals'}
                      ],
            'Cars': [{'name': 'Postal Truck',
                      'thumb': 'http://www.vidsplay.com/wp-content/uploads/2017/05/us_postal-screenshot.jpg',
                      'video': 'http://www.vidsplay.com/wp-content/uploads/2017/05/us_postal.mp4',
                      'genre': 'Cars'},
                     {'name': 'Traffic',
                      'thumb': 'http://www.vidsplay.com/wp-content/uploads/2017/05/traffic1-screenshot.jpg',
                      'video': 'http://www.vidsplay.com/wp-content/uploads/2017/05/traffic1.mp4',
                      'genre': 'Cars'},
                     {'name': 'Traffic Arrows',
                      'thumb': 'http://www.vidsplay.com/wp-content/uploads/2017/05/traffic_arrows-screenshot.jpg',
                      'video': 'http://www.vidsplay.com/wp-content/uploads/2017/05/traffic_arrows.mp4',
                      'genre': 'Cars'}
                     ],
            'Food': [{'name': 'Chicken',
                      'thumb': 'http://www.vidsplay.com/wp-content/uploads/2017/05/bbq_chicken-screenshot.jpg',
                      'video': 'http://www.vidsplay.com/wp-content/uploads/2017/05/bbqchicken.mp4',
                      'genre': 'Food'},
                     {'name': 'Hamburger',
                      'thumb': 'http://www.vidsplay.com/wp-content/uploads/2017/05/hamburger-screenshot.jpg',
                      'video': 'http://www.vidsplay.com/wp-content/uploads/2017/05/hamburger.mp4',
                      'genre': 'Food'},
                     {'name': 'Pizza',
                      'thumb': 'http://www.vidsplay.com/wp-content/uploads/2017/05/pizza-screenshot.jpg',
                      'video': 'http://www.vidsplay.com/wp-content/uploads/2017/05/pizza.mp4',
                      'genre': 'Food'}
                     ]}


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def get_categories():
    """
    Get the list of video categories.

    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or server.

    .. note:: Consider using `generator functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :return: The list of video categories
    :rtype: types.GeneratorType
    """
    return iterkeys(VIDEOS)


def get_videos(category):
    """
    Get the list of videofiles/streams.

    Here you can insert some parsing code that retrieves
    the list of video streams in the given category from some site or server.

    .. note:: Consider using `generators functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :param category: Category name
    :type category: str
    :return: the list of videos in the category
    :rtype: list
    """
    return VIDEOS[category]


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, 'My Video Collection')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    categories = get_categories()
    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category)
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': VIDEOS[category][0]['thumb'],
                          'icon': VIDEOS[category][0]['thumb'],
                          'fanart': VIDEOS[category][0]['thumb']})
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        # 'mediatype' is needed for a skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': category,
                                    'genre': category,
                                    'mediatype': 'video'})
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = get_url(action='listing', category=category)
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
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
    videos = get_videos(category)
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


def play_video(path):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


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
            play_video(params['video'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
    
import os
import time
import urllib
import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui
import json
import re
import sys
import datetime
import xml.etree.ElementTree as ET


CHANNELS=[
    {'name': 'DunaTV', 'id': 'dunalive', 'num': '3' },
    {'name': 'DunaWorld', 'id': 'dunaworldlive', 'num': '4' },
    {'name': 'MTV1', 'id': 'mtv1live', 'num': '1' },
    {'name': 'MTV2', 'id': 'mtv2live', 'num': '2' },
    {'name': 'MTV4', 'id': 'mtv4live', 'num': '30' },
    {'name': 'MTV5', 'id': 'mtv5live', 'num': '33' }
]

# setup
#cs_url = "http://player.mediaklikk.hu/player/player-inside-full3.php?userid=mtva&streamid=dunalive"
#cs_url = "https://player.mediaklikk.hu/playernew/player.php?video=dunalive&noflash=yes&osfamily=OS%20X&osversion=10.13&browsername=Firefox&browserversion=60.0&title=Duna&contentid=dunalive&embedded=0"
cf_url = "https://player.mediaklikk.hu/playernew/player.php?video={0}&noflash=yes&osfamily=OS%20X&osversion=10.13&browsername=Firefox&browserversion=60.0&title=Duna&contentid={0}&embedded=0"
cs_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_3 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B329 Safari/8536.25"
cs_name = xbmcaddon.Addon().getAddonInfo("id")
cs_file = os.path.join(xbmc.translatePath("special://temp"), cs_name + ".session")
cs_delay = 5

class CsatornakURLopener(urllib.FancyURLopener):
    version = cs_agent

#print "Session: " + cs_file

# tries to limit deadlocks due to multiple runs
# fcntl for file locking may not be available on some platforms
if os.path.exists(cs_file) and time.time() - os.path.getmtime(cs_file) < cs_delay:
    print "Recently ran, exiting."
    sys.exit(0)
else:
    with open(cs_file, "a+"):
	os.utime(cs_file, None)

cs_player = xbmc.Player()

# stop playing and wait
#cs_player.stop()
#while cs_player.isPlaying():
#	xbmc.sleep(10)
	
urllib._urlopener = CsatornakURLopener()
def load_page(pg_url):
    # load and parse stream
    print "Loading: " + pg_url
    page = urllib.urlopen(pg_url)
    page_content = page.read()
    page.close()
    return page_content

def add_live_tv(c):
    cs_url = cf_url.format(c['id'])
    cs_content = load_page(cs_url)
    cs_stream = ''

    for i in re.finditer('pl\.setup\(([^;]+)\);', cs_content):
        
        pl = json.loads(i.group(1))['playlist']
        n = 0
        if len(pl) > 1:
            n = 1
        cs_stream = pl[n]['file'] 
        break

    today = datetime.date.today()
    now = datetime.datetime.now()
    prg_url = 'https://www.mediaklikk.hu/iface/broadcast/{0}/broadcast_{1}.xml'.format(str(today), c['num'])
    prg_content = load_page(prg_url)
    root = ET.fromstring(prg_content)
    cnt = 0
    for item in root.iter('Item'):
        start_date = None
        date_xml =  item.find('Date')
        if date_xml is not None and date_xml.text is not None:
            start_date = datetime.datetime(*(time.strptime(date_xml.text, '%Y-%m-%d %H:%M:%S')[0:6]))
        length_xml = item.find('Length')
        play_dt = None
        if length_xml is not None and length_xml.text is not None:
            t = time.strptime(length_xml.text, '%H:%M:%S')
            play_dt = datetime.timedelta(hours = t.tm_hour, minutes = t.tm_min, seconds = t.tm_sec)
        #if start_date > now:
        #    continue
        if now - start_date > play_dt:
            continue
        if True:
            title_xml = item.find('SeriesTitle')
            if title_xml is None or title_xml.text is None:
                title_xml = item.find('Title')
            title = str(title_xml.text.encode('utf-8'))
            descr_xml = item.find('Description')
            description = None
            if descr_xml is not None and descr_xml.text is not None:
                description = str(descr_xml.text.encode('utf-8'))
            #title += '.'
            #for child in item:
            #    if child.text:
            #        s +=  child.tag + ': ' + str(child.text.encode('utf-8')) +'; '
            #xbmcgui.Dialog().ok(cs_name, s, json.dumps(sys.argv), str(today))
            play_min, play_sec = divmod(play_dt.seconds, 60)
            if play_min:
                name = '[{0}] {1} ({2}, {3}perc)'.format(c['name'], title, start_date.strftime('%H:%M'), play_min)
            else:
                name = '[{0}] {1} ({2}, {3:02}mp)'.format(c['name'], title, start_date.strftime('%H:%M'), play_sec)
            liz = xbmcgui.ListItem(name)
            liz.setInfo('video', {'title': name, 'duration': play_dt.seconds, 'plot': description})
            liz.setProperty("IsPlayable" , "True")
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), "https:" + cs_stream, liz)
            cnt = cnt + 1
            if cnt > 2:
                break

    
    #liz = xbmcgui.ListItem(' '.join((cs_name, json.dumps(sys.argv), str(date.today())))))#'XBMC list Example Title')

# play stream
#print "Playing: " + cs_stream
#xbmcgui.Dialog().ok(cs_name, json.dumps(sys.argv), str(date.today()))
for i in CHANNELS:
    add_live_tv(i)


xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
#XBMC.Container.Update
#cs_player.play("https:" + cs_stream, listitem)
