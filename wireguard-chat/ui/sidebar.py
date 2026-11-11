from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor


class Sidebar(QWidget):
    # Signals up to MainWindow
    channel_selected  = pyqtSignal(str)   # channel name
    dm_selected       = pyqtSignal(str)   # username
    new_channel_req   = pyqtSignal()
    new_dm_req        = pyqtSignal()
    rename_req        = pyqtSignal()      # user wants to change their username
    logger_req        = pyqtSignal()      # user wants to see the protocol log
    disconnect_req    = pyqtSignal()
    reconnect_req     = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._suppress_signals = False
        self.setObjectName("sidebar")
        self.setFixedWidth(250)
        self._users_with_transport: list[tuple[str, str]] = []  # (username, transport)
        self._is_cleartext = True
        self._unread_counts: dict[str, int] = {}

        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # Server / connection status
        header = QWidget()
        header.setStyleSheet("border-bottom: 1px solid #1a281a; padding: 10px 14px;")
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(14, 10, 14, 10)
        h_layout.setSpacing(4)

        self.server_label = QLabel("csc4026z.link")
        self.server_label.setStyleSheet("color: #4ade80; font-size: 13px; font-weight: bold;")
        
        log_btn = QPushButton("LOG")
        log_btn.setObjectName("log-btn")
        log_btn.setToolTip("protocol log")
        log_btn.clicked.connect(self.logger_req.emit)
        
        server_row = QHBoxLayout()
        server_row.addWidget(self.server_label)
        server_row.addStretch()
        server_row.addWidget(log_btn)
        h_layout.addLayout(server_row)

        status_row = QHBoxLayout()
        self.status_dot = QLabel("●")
        self.status_dot.setObjectName("status-dot")
        self.status_dot.setStyleSheet("color: #444444; font-size: 9px;")
        self.status_label = QLabel("disconnected")
        self.status_label.setStyleSheet("color: #444444; font-size: 11px;")
        status_row.addWidget(self.status_dot)
        status_row.addWidget(self.status_label)
        status_row.addStretch()
        h_layout.addLayout(status_row)

        # Connection button row to prevent overlapping (left-aligned)
        conn_row = QHBoxLayout()
        self.conn_action_btn = QPushButton("CONNECT")
        self.conn_action_btn.setObjectName("log-btn")
        self.conn_action_btn.setToolTip("connect/disconnect from server")
        self.conn_action_btn.clicked.connect(self._on_conn_action)
        conn_row.addWidget(self.conn_action_btn)
        conn_row.addStretch()
        h_layout.addLayout(conn_row)
        root.addWidget(header)

        # Channels section
        root.addWidget(self._section_header("channels", self._on_new_channel))
        self.channel_list = QListWidget()
        self.channel_list.setSpacing(1)
        self.channel_list.itemClicked.connect(lambda item: self._on_channel_click(item.text()))
        root.addWidget(self.channel_list)

        # DMs section
        root.addWidget(self._section_header("direct messages", self._on_new_dm))
        self.dm_list = QListWidget()
        self.dm_list.setSpacing(1)
        self.dm_list.itemClicked.connect(lambda item: self._on_dm_click(item.text()))
        root.addWidget(self.dm_list)

        # Online users section
        root.addWidget(self._section_header("online", None))
        self.user_list = QListWidget()
        self.user_list.setSpacing(1)
        self.user_list.setMaximumHeight(180)
        self.user_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        root.addWidget(self.user_list)

        root.addStretch()

        # Me bar
        me_bar = QWidget()
        me_bar.setObjectName("me-bar")
        me_bar.setStyleSheet("background: #0a0c0a; border-top: 1px solid #1a281a;")
        me_layout = QHBoxLayout(me_bar)
        me_layout.setContentsMargins(14, 8, 14, 8)

        self.me_dot = QLabel("●")
        self.me_dot.setStyleSheet("color: #4ade80; font-size: 9px;")
        self.me_label = QLabel("not connected")
        self.me_label.setStyleSheet("color: #4ade80; font-size: 12px;")
        
        rename_btn = QPushButton("✎")
        rename_btn.setObjectName("icon-btn")
        rename_btn.setToolTip("change username")
        rename_btn.clicked.connect(self.rename_req.emit)

        me_layout.addWidget(self.me_dot)
        me_layout.addWidget(self.me_label)
        me_layout.addStretch()
        me_layout.addWidget(rename_btn)
        root.addWidget(me_bar)

    def _section_header(self, title: str, callback) -> QWidget:
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(14, 10, 10, 4)
        lbl = QLabel(title.upper())
        lbl.setObjectName("section-label")
        lbl.setStyleSheet("color: #3a5a3a; font-size: 10px; letter-spacing: 1px;")
        layout.addWidget(lbl)
        layout.addStretch()
        if callback:
            btn = QPushButton("+")
            btn.setObjectName("icon-btn")
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        return w

    def _on_channel_click(self, name: str):
        if name and not self._suppress_signals:
            raw_name = name.lstrip("# ").split(" (")[0].strip()
            self.dm_list.clearSelection()
            self.channel_selected.emit(raw_name)

    def _on_dm_click(self, name: str):
        if name and not self._suppress_signals:
            raw_name = name.lstrip("@ ").split(" (")[0].strip()
            self.channel_list.clearSelection()
            self.dm_selected.emit(raw_name)

    def _on_new_channel(self):
        self.new_channel_req.emit()

    def _on_new_dm(self):
        self.new_dm_req.emit()

    def _on_conn_action(self):
        if self.conn_action_btn.text() == "DISCONNECT":
            self.disconnect_req.emit()
        else:
            self.reconnect_req.emit()

    # Public methods — called by controller

    def set_connection_status(self, connected: bool, host: str = "", encrypted: bool = False, port: int = 51820):
        self._is_cleartext = not encrypted
        if connected:
            if not encrypted:
                mode_str = "CLR"
            elif port == 51821:
                mode_str = "WG+"
            else:
                mode_str = "WG"
            self.status_dot.setStyleSheet("color: #4ade80; font-size: 9px;")
            self.status_label.setStyleSheet("color: #4ade80; font-size: 11px;")
            self.status_label.setText(f"connected · {mode_str}")
            self.conn_action_btn.setText("DISCONNECT")
        else:
            self.status_dot.setStyleSheet("color: #444444; font-size: 9px;")
            self.status_label.setStyleSheet("color: #444444; font-size: 11px;")
            self.status_label.setText("disconnected")
            self.conn_action_btn.setText("CONNECT")
            
            # Clear all local states upon disconnect
            self._users_with_transport.clear()
            self._unread_counts.clear()
            self.channel_list.clear()
            self.dm_list.clear()
            self.user_list.clear()
            self.me_label.setText("not connected")
            self.me_dot.setStyleSheet("color: #444444; font-size: 9px;")

    def set_username(self, username: str):
        self.me_label.setText(username)

    def set_channels(self, channels: list[str]):
        self._suppress_signals = True
        self.channel_list.clear()
        for ch in channels:
            count = self._unread_counts.get(f"channel:{ch}", 0)
            suffix = f" ({count})" if count > 0 else ""
            self.channel_list.addItem(f"# {ch}{suffix}")
        self.channel_list.setCurrentItem(None)
        self._suppress_signals = False

    def add_channel(self, name: str):
        self._suppress_signals = True
        items = [self.channel_list.item(i).text() for i in range(self.channel_list.count())]
        raw_items = [t.lstrip("# ").split(" (")[0].strip() for t in items]
        if name not in raw_items:
            count = self._unread_counts.get(f"channel:{name}", 0)
            suffix = f" ({count})" if count > 0 else ""
            self.channel_list.addItem(f"# {name}{suffix}")
        self._suppress_signals = False

    def set_dms(self, usernames: list[str]):
        self._suppress_signals = True
        self.dm_list.clear()
        for u in usernames:
            count = self._unread_counts.get(f"dm:{u}", 0)
            suffix = f" ({count})" if count > 0 else ""
            self.dm_list.addItem(f"@ {u}{suffix}")
        self.dm_list.setCurrentItem(None)
        self._suppress_signals = False

    def add_dm(self, username: str):
        self._suppress_signals = True
        items = [self.dm_list.item(i).text() for i in range(self.dm_list.count())]
        raw_items = [t.lstrip("@ ").split(" (")[0].strip() for t in items]
        if username not in raw_items:
            count = self._unread_counts.get(f"dm:{username}", 0)
            suffix = f" ({count})" if count > 0 else ""
            self.dm_list.addItem(f"@ {username}{suffix}")
        self._suppress_signals = False

    def set_users(self, users: list[tuple[str, str]]):
        """users: list of (username, transport) tuples"""
        self._suppress_signals = True
        self._users_with_transport = users
        self.user_list.clear()
        for username, transport in users:
            badge = {"cleartext": "clr", "wireguard": "wg", "wireguard_extended": "wg+"}.get(transport, "?")
            item = QListWidgetItem(f"  {username}  [{badge}]")
            if self._is_cleartext and transport != "cleartext":
                item.setForeground(QColor("#3a5a3a"))
            self.user_list.addItem(item)
        self._suppress_signals = False

    def set_unread(self, target_type: str, name: str, count: int):
        """Mark a channel or DM with an unread badge."""
        key = f"{target_type}:{name}"
        self._unread_counts[key] = count
        self._refresh_lists_text()

    def get_unread(self, target_type: str, name: str) -> int:
        key = f"{target_type}:{name}"
        return self._unread_counts.get(key, 0)

    def clear_unread(self, target_type: str, name: str):
        key = f"{target_type}:{name}"
        self._unread_counts[key] = 0
        self._refresh_lists_text()

    def _refresh_lists_text(self):
        self._suppress_signals = True
        for i in range(self.channel_list.count()):
            item = self.channel_list.item(i)
            raw_text = item.text().lstrip("# ").split(" (")[0].strip()
            count = self._unread_counts.get(f"channel:{raw_text}", 0)
            suffix = f" ({count})" if count > 0 else ""
            item.setText(f"# {raw_text}{suffix}")
            
        for i in range(self.dm_list.count()):
            item = self.dm_list.item(i)
            raw_text = item.text().lstrip("@ ").split(" (")[0].strip()
            count = self._unread_counts.get(f"dm:{raw_text}", 0)
            suffix = f" ({count})" if count > 0 else ""
            item.setText(f"@ {raw_text}{suffix}")
        self._suppress_signals = False

    def remove_channel(self, name: str):
        self._suppress_signals = True
        items = [self.channel_list.item(i).text() for i in range(self.channel_list.count())]
        if f"# {name}" in items:
            self.channel_list.takeItem(items.index(f"# {name}"))
        self.channel_list.clearSelection()
        self.channel_list.setCurrentItem(None)
        self._suppress_signals = False

    def remove_dm(self, username: str):
        self._suppress_signals = True
        items = [self.dm_list.item(i).text() for i in range(self.dm_list.count())]
        if f"@ {username}" in items:
            self.dm_list.takeItem(items.index(f"@ {username}"))
        self.dm_list.clearSelection()
        self.dm_list.setCurrentItem(None)
        self._suppress_signals = False