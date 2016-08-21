from gi.repository import Gio
import gnsdkwrap._gnsdk as c
from ctypes import *
from xml.etree import ElementTree as ET
import sqlite3


class GNSDKMatch(object):
    """docstring for GNSDKMatch"""
    def __init__(self):
        super(GNSDKMatch, self).__init__()
        self.matching = False

        # init gnsdk stream matching
        lpath = 'license.txt'.encode('ASCII')
        manager_handle = c.gnsdk_manager_handle_t()
        c.gnsdk_manager_initialize(byref(manager_handle),
                                   lpath, c.GNSDK_MANAGER_LICENSEDATA_FILENAME)
        c.gnsdk_dsp_initialize(manager_handle)
        c.gnsdk_musicidstream_initialize(manager_handle)

        # TODO: check if user registered and register if not
        conn = sqlite3.connect('hiset.db')
        ans = conn.execute("select str_val from settings where setting='userid'").fetchall()
        userid = b''
        for userid_ in ans:
            for user in userid_:
                if user and isinstance(user, str):
                    userid = user.strip().encode('ASCII')

        ans = conn.execute("select str_val from settings where setting='usertag'").fetchall()
        usertag = b''
        for usertag_ in ans:
            for user in usertag_:
                if user:
                    usertag = user.strip().encode('ASCII')

        ans = conn.execute("select str_val from settings where setting='license_path'").fetchall()
        lpath = b''
        for lpath_ in ans:
            for user in lpath_:
                if user:
                    lpath = user.strip().encode('ASCII')

        with open('user.txt') as f:
            userbuf = f.read().strip().encode('ASCII')

        self.user_handle = c.gnsdk_user_handle_t()
        print(c.gnsdk_manager_user_create(userbuf, userid, byref(self.user_handle)))
        result_callback = c.gnsdk_result_available_fn_t(self._result_callback)

    def _result_callback(self, data, channel_handle, response, pb_abort):
        count = c.gnsdk_uint32_t(0)
        c.gnsdk_manager_gdo_child_count(response, c.GNSDK_GDO_CHILD_ALBUM,
                                        byref(count))

        app = Gio.Application.get_default()
        app.m.cork()
        self.matching = False

        matches = []
        album_handle = c.gnsdk_gdo_handle_t()
        for i in range(1, count.value + 1):
            c.gnsdk_manager_gdo_child_get(response, c.GNSDK_GDO_CHILD_ALBUM, i,
                                          byref(album_handle))
            ss = c_char_p()
            c.gnsdk_manager_gdo_render(album_handle, 8195, byref(ss))
            matches.append(MatchResult.from_json(ss))
        app.process_match(matches)

    def start_match(self):
        if self.matching:
            return
        app = Gio.Application.get_default()
        app.m.uncork()
        app._matching = True
        self.matching = True

        ident_callback = c.gnsdk_identifying_status_fn_t(_ident_callback)
        result_callback = c.gnsdk_result_available_fn_t(self._result_callback)
        channel_handle = c.gnsdk_musicidstream_channel_handle_t()
        callbacks = c.gnsdk_musicidstream_callbacks_t()
        callbacks.callback_identifying_status = ident_callback
        callbacks.callback_result_available = result_callback
        c.gnsdk_musicidstream_channel_create(self.user_handle, c.gnsdk_musicidstream_preset_radio, byref(callbacks), c.GNSDK_NULL, byref(channel_handle))
        c.gnsdk_musicidstream_channel_audio_begin(channel_handle, 44100, 8, 1)
        c.gnsdk_musicidstream_channel_identify(channel_handle)

        while self.matching:
            c.gnsdk_musicidstream_channel_audio_write(channel_handle, c_ubyte(app.m.samples.get()), 1)
        # 20 secs
        c.gnsdk_musicidstream_channel_wait_for_identify(channel_handle, 20000)


def _ident_callback(data, status, pb_abort):
    pass


class MatchResult(object):
    """docstring for MatchResult"""
    def __init__(self):
        super(MatchResult, self).__init__()
        self.year = None
        self.album = None
        self.artist = None
        self.track = None

    @classmethod
    def from_json(cls, result):
        mr = MatchResult()

        tree = ET.fromstring(result.value)
        matched_track = None
        for track in tree.findall('TRACK_MATCHED'):
            matched_track = track.text
        for year in tree.findall('YEAR'):
            mr.year = year.text
        for album in tree.findall('TITLE_OFFICIAL/DISPLAY'):
            mr.album = album.text
        for artist in tree.findall('ARTIST/NAME_OFFICIAL/DISPLAY'):
            mr.artist = artist.text
        for i in [tr for tr in tree.findall('TRACK') if tr.attrib['ORD'] == matched_track]:
            for track in i.findall('TITLE_OFFICIAL/DISPLAY'):
                mr.track = track.text

        return mr
