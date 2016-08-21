import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
import threading
import sqlite3
import datetime


class MainWindow(Gtk.ApplicationWindow):
    """docstring for MainWindow"""

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.set_default_size(700, 400)
        self.set_icon_name('media-record')

        self.hb = Gtk.HeaderBar()
        self.hb.set_show_close_button(True)

        self.custom_title = Gtk.Label()
        self.custom_title.set_text('press record to start matching')

        self.hb.props.title = "matchsong"
        self.hb.props.custom_title = self.custom_title
        self.set_titlebar(self.hb)

        self.settings_button = Gtk.MenuButton()
        image = Gtk.Image.new_from_icon_name('open-menu-symbolic',
                                             Gtk.IconSize.BUTTON)
        self.settings_button.add(image)
        self.hb.pack_end(self.settings_button)

        self.match_button = Gtk.Button()
        image = Gtk.Image.new_from_icon_name('media-record',
                                             Gtk.IconSize.BUTTON)
        self.match_button.add(image)
        app = Gio.Application.get_default()
        self.match_button.connect('clicked', self.start_match)
        self.hb.pack_start(self.match_button)

        self.add_db()
        self.show_all()

    def setup_menu(self, menu):
        self.settings_button.set_menu_model(menu)

    def add_db(self):
        self.check_db_history()
        conn = sqlite3.connect('hiset.db')
        c = conn.cursor()
        data = c.execute("select * from (select * from matches order by rowid DESC limit 10)").fetchall()
        conn.close()

        self.table = Gtk.ListStore(str, str, str, str, str)
        for d in data:
            self.table.append(d)

        treeview = Gtk.TreeView(model=self.table)
        renderer = Gtk.CellRendererText()

        treeview.append_column(Gtk.TreeViewColumn('date', renderer, text=0))
        treeview.append_column(Gtk.TreeViewColumn('artist', renderer, text=1))
        treeview.append_column(Gtk.TreeViewColumn('track', renderer, text=2))
        treeview.append_column(Gtk.TreeViewColumn('album', renderer, text=3))
        treeview.append_column(Gtk.TreeViewColumn('year', renderer, text=4))

        scrolltree = Gtk.ScrolledWindow()
        scrolltree.set_vexpand(True)
        scrolltree.add(treeview)

        self.add(scrolltree)

    def process_match(self, matches):
        if len(matches) == 1:
            self.custom_title.set_text('1 match found')
        else:
            self.custom_title.set_text('{} matches found'.format(len(matches)))

        self.match_button.set_sensitive(True)
        self.hb.props.custom_title = self.custom_title

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect('hiset.db')
        for match in matches:
            conn.execute("insert into matches(d, artist, track, album, year) values (?, ?, ?, ?, ?)", (now, match.artist, match.track, match.album, match.year))
            conn.commit()
            self.table.insert(0, (str(now), match.artist, match.track, match.album, match.year))
        conn.close()

    def start_match(self, button):
        app = Gio.Application.get_default()
        threading.Thread(target=app.match.start_match).start()
        spinner = Gtk.Spinner()
        spinner.start()
        spinner.show()
        self.hb.props.custom_title = spinner
        self.match_button.set_sensitive(False)

    def check_db_history(self):
        conn = sqlite3.connect('hiset.db')
        tables = conn.execute("select name from sqlite_master where type='table'").fetchall()
        is_in = False
        for table in tables:
            if 'matches' in table:
                is_in = True
        if not is_in:
            print("history not in, creating table")
            conn.execute('create table matches (d timestamp, artist text, track text, album text, year text)')
            conn.commit()
        conn.close()
