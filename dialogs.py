from gi.repository import Gtk, Gio
import sqlite3


class SettingsDialog(object):
    """docstring for SettingsDialog"""

    def __init__(self):
        super(SettingsDialog, self).__init__()

        builder = Gtk.Builder()
        builder.add_from_file('data/settings.ui')
        app = Gio.Application.get_default()

        self.__dialog = builder.get_object('SettingsDialog')
        self.__dialog.set_transient_for(app.window)

        combo = builder.get_object('combo')
        for index, (name, desc, mon) in app.m.sinks.items():
            combo.append_text(desc)
        if app.m._sink_index:
            combo.set_active(app.m._sink_index)
        else:
            combo.set_active(0)
        combo.connect('changed', self.update_monitor)

        hb = builder.get_object('titlebar')
        hb.set_title('Preferences')
        self.__dialog.set_titlebar(hb)

        self.userid = builder.get_object('userid-text')
        self.usertag = builder.get_object('usertag-text')
        self.license_path = builder.get_object('licensepath-text')
        conn = sqlite3.connect('hiset.db')
        userid = conn.execute("select str_val from settings where setting='userid'").fetchall()
        for userid_ in userid:
            for user in userid_:
                self.userid.set_text(str(user))

        ans = conn.execute("select str_val from settings where setting='usertag'").fetchall()
        for usertag_ in ans:
            for user in usertag_:
                self.usertag.set_text(str(user))

        ans = conn.execute("select str_val from settings where setting='license_path'").fetchall()
        for lpath_ in ans:
            for lpath in lpath_:
                self.license_path.set_filename(str(lpath))

        save = builder.get_object('save-button')
        save.connect('clicked', self.on_save)

    def show(self):
        self.__dialog.show()

    def update_monitor(self, combo):
        # insert new index into settings db
        ac = combo.get_active()
        conn = sqlite3.connect('hiset.db')
        conn.execute("update settings set val={} where setting='last_index'".format(ac))
        conn.commit()
        conn.close()
        app = Gio.Application.get_default()
        app.m.choose_stream()

    def on_save(self, save):
        conn = sqlite3.connect('hiset.db')
        conn.execute("update settings set str_val=? where setting='userid'", (self.userid.get_text(),))
        conn.execute("update settings set str_val=? where setting='usertag'", (self.usertag.get_text(),))
        conn.execute("update settings set str_val=? where setting='license_path'", (self.license_path.get_filename(),))
        conn.commit()
        conn.close()

        app = Gio.Application.get_default()
        if not app.match:
            app.reinit_gnsdkmatch()
        self.__dialog.close()
