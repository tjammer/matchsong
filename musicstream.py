from pulseaudio import lib_pulseaudio as c
from ctypes import POINTER, c_ubyte, c_void_p, c_ulong, cast
from queue import Queue
import sqlite3


class MusicStream(object):
    """docstring for MusicStream"""

    def __init__(self):
        super(MusicStream, self).__init__()
        self.sink_name = None
        self.rate = 44100
        self.samples = Queue()
        self.check_db_settings()

        self.context_notify_cb = c.pa_context_notify_cb_t(self._context_notify_cb)
        self.init_stream = c.pa_sink_info_cb_t(self._init_stream)
        self.stream_read_cb = c.pa_stream_request_cb_t(self._stream_read_cb)
        self.stream_success_cb = c.pa_stream_success_cb_t(self._stream_success)

        self._sink_index = None
        self._stream = None
        self.sinks = {}

        mainloop = c.pa_threaded_mainloop_new()
        mainloop_api = c.pa_threaded_mainloop_get_api(mainloop)
        context = c.pa_context_new(mainloop_api, 'MusicStream'.encode('ascii'))
        self._context = context
        c.pa_context_set_state_callback(context, self.context_notify_cb, None)
        c.pa_context_connect(context, None, 0, None)
        c.pa_threaded_mainloop_start(mainloop)

    def __iter__(self):
        while True:
            yield self.samples.get()

    def _context_notify_cb(self, context, _):
        state = c.pa_context_get_state(context)

        if state == c.PA_CONTEXT_READY:
            o = c.pa_context_get_sink_info_list(context, self.init_stream,
                                                None)
            c.pa_operation_unref(o)

        elif state == c.PA_CONTEXT_FAILED:
            raise Exception

    def _stream_read_cb(self, stream, len, _):
        data = c_void_p()
        c.pa_stream_peek(stream, data, c_ulong(len))
        data = cast(data, POINTER(c_ubyte))
        for i in range(len):
            self.samples.put(data[i])
        c.pa_stream_drop(stream)

    def _init_stream(self, context, sink_info_p, _, __):
        if not sink_info_p:
            return

        sink_info = sink_info_p.contents
        self.sinks[sink_info.index] = (sink_info.name,
                                       sink_info.description.decode('utf-8'),
                                       sink_info.monitor_source_name)
        self.choose_stream()

    def choose_stream(self):
        index, name, desc, monitor = [None] * 4
        if len(self.sinks) == 1:
            index, (name, desc, monitor) = 0, self.sinks.get(0)
        else:
            # get index from db
            conn = sqlite3.connect('hiset.db')
            ans = conn.execute("select val from settings where setting='last_index'").fetchall()
            conn.close()
            if ans:
                for tup in ans:
                    for i in tup:
                        try:
                            index, (name, desc, monitor) = i, self.sinks.get(i)
                        except:
                            pass

        if not monitor:
            return

        self._sink_index = index
        samplespec = c.pa_sample_spec()
        samplespec.channels = 1
        samplespec.format = c.PA_SAMPLE_U8
        samplespec.rate = self.rate

        pa_stream = c.pa_stream_new(self._context,
                                    "MusicStream".encode('ascii'),
                                    samplespec, None)
        c.pa_stream_set_read_callback(pa_stream, self.stream_read_cb,
                                      index)
        c.pa_stream_connect_record(pa_stream, monitor,
                                   None, c.PA_STREAM_START_CORKED)
        self._stream = pa_stream

    def _stream_success(self, stream, _, __):
        pass

    def uncork(self):
        self.samples = Queue()
        c.pa_stream_cork(self._stream, 0, self.stream_success_cb, None)

    def cork(self):
        c.pa_stream_cork(self._stream, 1, self.stream_success_cb, None)

    def check_db_settings(self):
        conn = sqlite3.connect('hiset.db')
        tables = conn.execute("select name from sqlite_master where type='table'").fetchall()
        is_in = False
        for table in tables:
            if 'settings' in table:
                is_in = True
        if not is_in:
            print("settings not in, creating table")
            conn.execute('create table settings (setting TEXT PRIMARY KEY, val INT, str_val TEXT)')
            conn.execute("insert into settings (setting, val) values ('last_index', 0)")
            conn.execute("insert into settings (setting, str_val) values ('userid', '')")
            conn.execute("insert into settings (setting, str_val) values ('usertag', '')")
            conn.execute("insert into settings (setting, str_val) values ('license_path', '')")
            conn.commit()
        conn.close()
