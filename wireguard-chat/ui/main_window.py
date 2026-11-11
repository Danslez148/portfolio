from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QDialog, QInputDialog
)
from PyQt6.QtCore import pyqtSignal

from .styles import STYLE
from .sidebar import Sidebar
from .chat_panel import ChatPanel
from .panels import WelcomePanel
from .dialogs import ConnectDialog, ChannelDialog, NewDMDialog


class MainWindow(QMainWindow):
    """
    Top-level window. Owns the sidebar and main panel stack.

    Signals emitted TO the controller:
        sig_connect(host, port, encrypted)
        sig_disconnect()
        sig_send_message(text)
        sig_join_channel(name)
        sig_leave_channel()
        sig_new_dm(username)
        sig_set_username(name)
        sig_select_channel(name)
        sig_select_user(username)
    """

    sig_connect        = pyqtSignal(str, int, bool)  # host, port, encrypted
    sig_disconnect     = pyqtSignal()
    sig_send_message   = pyqtSignal(str)
    sig_join_channel   = pyqtSignal(str)
    sig_create_channel = pyqtSignal(str, str)        # name, description
    sig_leave_channel  = pyqtSignal()
    sig_new_dm         = pyqtSignal(str)
    sig_set_username   = pyqtSignal(str)
    sig_select_channel = pyqtSignal(str)
    sig_select_user    = pyqtSignal(str)
    sig_show_log       = pyqtSignal()

    def __init__(self, show_connect_dialog: bool = True):
        super().__init__()
        self.setWindowTitle("chat client")
        self.resize(960, 620)
        self.setStyleSheet(STYLE)

        self._online_users: list[tuple[str, str]] = []  # kept for legacy compat

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_row = QHBoxLayout(central)
        main_row.setSpacing(0)
        main_row.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.channel_selected.connect(self._on_channel_selected)
        self.sidebar.dm_selected.connect(self._on_dm_selected)
        self.sidebar.new_channel_req.connect(self._on_new_channel)
        self.sidebar.new_dm_req.connect(self._on_new_dm)
        self.sidebar.rename_req.connect(self._on_rename)
        self.sidebar.logger_req.connect(self.sig_show_log.emit)
        self.sidebar.disconnect_req.connect(self.sig_disconnect.emit)
        self.sidebar.reconnect_req.connect(lambda: self._show_connect_dialog(is_startup=False))
        main_row.addWidget(self.sidebar)

        # Right panel stack: welcome screen or active chat
        self.stack = QStackedWidget()
        self.welcome_panel = WelcomePanel()
        self.chat_panel = ChatPanel()
        self.stack.addWidget(self.welcome_panel)   # index 0
        self.stack.addWidget(self.chat_panel)      # index 1
        self.stack.setCurrentIndex(0)
        main_row.addWidget(self.stack)

        # Wire chat panel signals
        self.chat_panel.message_sent.connect(self._on_message_sent)
        self.chat_panel.leave_requested.connect(self._on_leave)

        self._available_channels: list[str] = []

        # Show connect dialog on startup
        if show_connect_dialog:
            self._show_connect_dialog(is_startup=True)

    # Startup

    def _show_connect_dialog(self, is_startup: bool = False):
        dlg = ConnectDialog(self)
        dlg.setStyleSheet(STYLE)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            host, port, encrypted = dlg.get_values()
            self.sig_connect.emit(host, port, encrypted)
        else:
            if is_startup:
                # User cancelled = close the entire application
                import sys
                sys.exit(0)

    # Internal handlers

    def _on_channel_selected(self, name: str):
        self.sig_select_channel.emit(name)

    def _on_dm_selected(self, username: str):
        self.sig_select_user.emit(username)

    def _on_message_sent(self, text: str):
        # Handle slash commands locally or forward to controller
        if text.startswith("/join "):
            channel = text[6:].strip().lstrip("#")
            if channel in self._available_channels:
                self.sig_join_channel.emit(channel)
            else:
                self.show_system_event(f"channel '#{channel}' doesn't exist.")
        elif text.startswith("/dm "):
            user = text[4:].strip().lstrip("@")
            valid_users = [u for u, t in self.sidebar._users_with_transport]
            if user in valid_users:
                self.sig_new_dm.emit(user)
            else:
                self.show_system_event(f"user '{user}' is not online.")
        elif text.startswith("/leave"):
            self._on_leave()
        elif text.startswith("/nick "):
            name = text[6:].strip()
            self.sig_set_username.emit(name)
        else:
            self.sig_send_message.emit(text)

    def _on_leave(self):
        current = self.chat_panel._current_context
        if current and current[0] == "channel":
            self.sidebar.remove_channel(current[1])
            self.sig_leave_channel.emit()
        elif current and current[0] == "dm":
            self.sidebar.remove_dm(current[1])
        self.chat_panel._current_context = None
        self.show_welcome()

    def _on_new_channel(self):
        dlg = ChannelDialog(
            available_channels=self._available_channels,
            parent=self
        )
        dlg.setStyleSheet(STYLE)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, desc, create_new = dlg.get_values()
            if not name:
                return
            if create_new:
                self.sig_create_channel.emit(name, desc)
            else:
                if name in self._available_channels:
                    self.sig_join_channel.emit(name)
                else:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "unknown channel", f"'#{name}' doesn't exist. Use 'create new' to make it.")

    def _on_new_dm(self):
        dlg = NewDMDialog(
            self.sidebar._users_with_transport,
            is_cleartext_session=self.sidebar._is_cleartext,
            parent=self
        )
        dlg.setStyleSheet(STYLE)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            username = dlg.get_username()
            valid_users = [u for u, t in self.sidebar._users_with_transport]
            if username and username in valid_users:
                self.sig_new_dm.emit(username)
            elif username:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "unknown user", f"'{username}' is not online.")

    def _on_rename(self):
        from PyQt6.QtWidgets import QInputDialog
        current = self.sidebar.me_label.text()
        name, ok = QInputDialog.getText(
            self, "change username", "new username:",
            text=current
        )
        if ok and name.strip():
            new_name = name.strip()
            # Enforce clear- prefix for cleartext sessions
            if self.sidebar._is_cleartext and not new_name.startswith("clear-"):
                new_name = f"clear-{new_name}"
            # Strip disallowed colon character
            new_name = new_name.replace(":", "")
            self.sig_set_username.emit(new_name)

    # Public API — called by the controller to update UI state

    def update_connection_status(self, connected: bool, host: str = "",
                                  encrypted: bool = False, port: int = 51820):
        self.sidebar.set_connection_status(connected, host, encrypted, port)

    def set_username(self, username: str):
        self.sidebar.set_username(username)

    def set_channels(self, channels: list[str]):
        self.sidebar.set_channels(channels)

    def set_users(self, users: list[tuple[str, str]]):
        """users: list of (username, transport) tuples from USER_LIST responses"""
        self.sidebar.set_users(users)

    def set_available_channels(self, channels: list[str]):
        self._available_channels = channels

    def open_channel(self, name: str, description: str = "", member_count: int = 0):
        """Switch the main panel to a channel view."""
        self.sidebar.clear_unread("channel", name)
        self.chat_panel.switch_to_channel(name, description, member_count)
        self.stack.setCurrentIndex(1)
        

    def open_dm(self, username: str):
        """Switch the main panel to a DM view."""
        self.sidebar.clear_unread("dm", username)
        self.chat_panel.switch_to_dm(username)
        self.stack.setCurrentIndex(1)
        self.sidebar.add_dm(username)

    def add_message(self, sender: str, text: str, timestamp: str = "",
                    is_self: bool = False, is_system: bool = False, is_dm: bool = False):
        self.chat_panel.add_message(sender, text, timestamp, is_self, is_system, is_dm)

    def show_system_event(self, msg: str):
        self.chat_panel.show_system_event(msg)

    def set_channel_info(self, name: str, description: str):
        self.chat_panel.set_channel_info(name, description)

    def set_members(self, members: list[str]):
        self.chat_panel.set_members(members)

    def show_server_message(self, msg: str):
        """Broadcast from server (Shakespeare sonnet lines, etc.)"""
        self.chat_panel.add_message("server", msg, is_system=True)

    def show_shutdown_notice(self, msg: str):
        self.chat_panel.show_system_event(f"⚠ server shutdown: {msg}")
        self.update_connection_status(False)

    def show_welcome(self):
        self.stack.setCurrentIndex(0)

    def add_channel(self, name: str):
        self.sidebar.add_channel(name)

    def closeEvent(self, event):
        """Ensure we disconnect when the window is closed."""
        self.sig_disconnect.emit()
        event.accept()