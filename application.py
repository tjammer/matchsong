import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GObject
from window import MainWindow
from dialogs import SettingsDialog
from musicstream import MusicStream
from gnsdkmatch import GNSDKMatch


class MyApp(Gtk.Application):
    """docstring for MyApp"""

    def __init__(self):
        super(MyApp, self).__init__(application_id='org.gnome.matchsong')
        self.window = None
        self.m = MusicStream()

        self.match = GNSDKMatch()

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = MainWindow(application=self, title="Main Window")
            self.window.setup_menu(self.setup_menu())

        self.window.present()

    def on_quit(self, action, param):
        self.quit()

    def setup_menu(self):
        builder = Gtk.Builder()
        builder.add_from_file('data/appmenu.ui')
        menu = builder.get_object('app-menu')

        quit_action = Gio.SimpleAction.new('quit', None)
        quit_action.connect('activate', self.on_quit)
        self.set_accels_for_action('app.quit', ["<Control>q"])
        self.add_action(quit_action)

        settings_action = Gio.SimpleAction.new('settings', None)
        settings_action.connect('activate', self._settings_dialog)
        self.set_accels_for_action('app.settings', ["<Control>s"])
        self.add_action(settings_action)

        return menu

    def _settings_dialog(self, action=None, param=None):
        dialog = SettingsDialog()
        dialog.show()

    def process_match(self, matches):
        self.window.process_match(matches)


if __name__ == '__main__':
    GObject.threads_init()
    app = MyApp()
    app.run()
