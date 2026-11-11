from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QHBoxLayout, QPushButton, QFrame, QDialogButtonBox,
    QListWidget, QListWidgetItem, QCompleter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class ConnectDialog(QDialog):
    """
    Shown at startup. Collects host, port, and optional username.
    Emits accepted with (host, port, use_encryption) when user clicks Connect.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("connect to server")
        self.setModal(True)
        self.setMinimumWidth(380)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        root = QVBoxLayout(self)
        root.setSpacing(14)
        root.setContentsMargins(24, 24, 24, 20)

        # Title
        title = QLabel("[ CHAT CLIENT ]")
        title.setStyleSheet("color: #4ade80; font-size: 16px; font-weight: bold; letter-spacing: 2px;")
        root.addWidget(title)

        sub = QLabel("establish server connection")
        sub.setStyleSheet("color: #3a5a3a; font-size: 11px; margin-bottom: 8px;")
        root.addWidget(sub)

        self._sep()
        root.addWidget(self._make_sep())

        # Host (display only)
        root.addWidget(self._field_label("host"))
        host_label = QLabel("csc4026z.link")
        host_label.setStyleSheet("color: #7aab7a; font-size: 12px; padding: 5px 0;")
        root.addWidget(host_label)

        # Mode toggle with port labels above buttons
        root.addSpacing(12)
        mode_label = QLabel("Choose a mode:")
        mode_label.setStyleSheet("color: #3a5a3a; font-size: 11px; letter-spacing: 1px;")
        root.addWidget(mode_label)
        
        # Mode options layout
        mode_row = QHBoxLayout()
        mode_row.setSpacing(15)
        
        # 1. Cleartext Column
        clear_col = QVBoxLayout()
        clear_col.setSpacing(4)
        clear_port_label = QLabel("51825")
        clear_port_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        clear_port_label.setStyleSheet("color: #3a5a3a; font-size: 10px;")
        self.clear_btn = QPushButton("cleartext")
        self.clear_btn.setCheckable(True)
        self.clear_btn.setMinimumWidth(90)
        self.clear_btn.clicked.connect(lambda: self._set_mode('cleartext'))
        clear_col.addWidget(clear_port_label)
        clear_col.addWidget(self.clear_btn)
        mode_row.addLayout(clear_col)
        
        # 2. Encrypted Column
        enc_col = QVBoxLayout()
        enc_col.setSpacing(4)
        enc_port_label = QLabel("51820")
        enc_port_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        enc_port_label.setStyleSheet("color: #3a5a3a; font-size: 10px;")
        self.enc_btn = QPushButton("encrypted")
        self.enc_btn.setCheckable(True)
        self.enc_btn.setMinimumWidth(90)
        self.enc_btn.clicked.connect(lambda: self._set_mode('encrypted'))
        enc_col.addWidget(enc_port_label)
        enc_col.addWidget(self.enc_btn)
        mode_row.addLayout(enc_col)
        
        # 3. Extended Column
        ext_col = QVBoxLayout()
        ext_col.setSpacing(4)
        ext_port_label = QLabel("51821")
        ext_port_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ext_port_label.setStyleSheet("color: #3a5a3a; font-size: 10px;")
        self.ext_btn = QPushButton("extended wg")
        self.ext_btn.setCheckable(True)
        self.ext_btn.setMinimumWidth(90)
        self.ext_btn.clicked.connect(lambda: self._set_mode('extended'))
        ext_col.addWidget(ext_port_label)
        ext_col.addWidget(self.ext_btn)
        mode_row.addLayout(ext_col)
        
        mode_row.addStretch()
        root.addLayout(mode_row)

        root.addSpacing(8)
        root.addWidget(self._make_sep())
        root.addSpacing(8)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()
        cancel = QPushButton("cancel")
        cancel.setMinimumWidth(80)
        cancel.clicked.connect(self.reject)
        self.connect_btn = QPushButton("[ connect ]")
        self.connect_btn.setMinimumWidth(100)
        self.connect_btn.setStyleSheet(
            "color: #0a0c0a; background-color: #4ade80; border: none; padding: 6px 18px; font-weight: bold;"
        )
        self.connect_btn.clicked.connect(self.accept)
        self.connect_btn.setEnabled(False)
        btn_row.addWidget(cancel)
        btn_row.addWidget(self.connect_btn)
        root.addLayout(btn_row)
        root.addStretch()

        self._mode = None

    def _field_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #3a5a3a; font-size: 10px; letter-spacing: 1px;")
        return lbl

    def _make_sep(self):
        sep = QFrame()
        sep.setObjectName("h-sep")
        sep.setFrameShape(QFrame.Shape.HLine)
        return sep

    def _sep(self): pass  # placeholder so layout spacing is clean

    def _set_mode(self, mode: str):
        self._mode = mode
        
        active_style = (
            "background-color: #4ade80; color: #0a0c0a; border: 1px solid #4ade80; "
            "padding: 5px 14px; border-radius: 3px; font-weight: bold;"
        )
        inactive_style = (
            "background: transparent; border: 1px solid #1a281a; color: #4ade80; "
            "padding: 5px 14px; border-radius: 3px;"
        )
        
        self.clear_btn.setStyleSheet(active_style if mode == 'cleartext' else inactive_style)
        self.enc_btn.setStyleSheet(active_style if mode == 'encrypted' else inactive_style)
        self.ext_btn.setStyleSheet(active_style if mode == 'extended' else inactive_style)
        
        # Enable connect button
        self.connect_btn.setEnabled(True)

    def get_values(self):
        """Returns (host: str, port: int, encrypted: bool)"""
        if self._mode == 'encrypted':
            port = 51820
            encrypted = True
        elif self._mode == 'extended':
            port = 51821
            encrypted = True
        else:
            port = 51825
            encrypted = False
        return "csc4026z.link", port, encrypted


# New channel dialog

class ChannelDialog(QDialog):
    """
    Handles both joining an existing channel and creating a new one.
    Toggle between modes with the join/create buttons.
    Returns (name, description, create_new) via get_values().
    """
    def __init__(self, available_channels: list[str] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("channel")
        self.setModal(True)
        self.setMinimumWidth(320)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        self._create_mode = False
        self._available_channels = available_channels or []

        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(20, 20, 20, 16)

        # Mode toggle row
        mode_row = QHBoxLayout()
        self.join_btn   = QPushButton("join existing")
        self.create_btn = QPushButton("create new")
        self.join_btn.setCheckable(True)
        self.create_btn.setCheckable(True)
        self.join_btn.setChecked(True)
        self.join_btn.clicked.connect(lambda: self._set_mode(False))
        self.create_btn.clicked.connect(lambda: self._set_mode(True))
        mode_row.addWidget(self.join_btn)
        mode_row.addWidget(self.create_btn)
        mode_row.addStretch()
        root.addLayout(mode_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #1a281a; max-height: 1px;")
        root.addWidget(sep)

        # join mode widgets
        self._list_label = QLabel("available channels")
        self._list_label.setStyleSheet("color: #3a5a3a; font-size: 10px;")
        root.addWidget(self._list_label)

        self.channel_list_widget = QListWidget()
        self.channel_list_widget.setMaximumHeight(140)
        for ch in self._available_channels:
            self.channel_list_widget.addItem(f"  # {ch}")
        self.channel_list_widget.itemClicked.connect(
            lambda item: self.name_input.setText(item.text().strip().lstrip("# "))
        )
        root.addWidget(self.channel_list_widget)

        # name input
        self._name_label = QLabel("channel name")
        self._name_label.setStyleSheet("color: #3a5a3a; font-size: 10px;")
        root.addWidget(self._name_label)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("#channel-name")
        self.name_input.setMaxLength(20)
        root.addWidget(self.name_input)

        # create mode widgets
        self._desc_label = QLabel("description  (optional, max 100 chars)")
        self._desc_label.setStyleSheet("color: #3a5a3a; font-size: 10px;")
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("what is this channel for?")
        self.desc_input.setMaxLength(100)
        root.addWidget(self._desc_label)
        root.addWidget(self.desc_input)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

        # Start in join mode
        self._set_mode(False)

    def _set_mode(self, create: bool):
        self._create_mode = create
        self.join_btn.setChecked(not create)
        self.create_btn.setChecked(create)
        # Join mode shows the list, hides description
        self._list_label.setVisible(not create)
        self.channel_list_widget.setVisible(not create)
        # Create mode shows description, hides list
        self._desc_label.setVisible(create)
        self.desc_input.setVisible(create)
        self.adjustSize()

    def get_values(self) -> tuple[str, str, bool]:
        name = self.name_input.text().strip().lstrip("#")
        desc = self.desc_input.text().strip()
        return name, desc, self._create_mode

class NewDMDialog(QDialog):
    """
    users: list of (username, transport) tuples.
    transport is one of: 'cleartext', 'wireguard', 'wireguard_extended'
    is_cleartext_session: if True, wireguard users are greyed out (can't DM them)
    """
    def __init__(self, users: list[tuple[str, str]], is_cleartext_session: bool = True, parent=None):
        super().__init__(parent)
        self.setWindowTitle("new direct message")
        self.setModal(True)
        self.setMinimumWidth(320)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(20, 20, 20, 16)

        name_label = QLabel("username")
        name_label.setStyleSheet("color: #3a5a3a; font-size: 10px;")
        root.addWidget(name_label)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("@username")

        # Autocomplete from cleartext-compatible users only
        compatible = [u for u, t in users if not is_cleartext_session or t == "cleartext"]
        from PyQt6.QtWidgets import QCompleter
        completer = QCompleter(compatible)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.user_input.setCompleter(completer)
        root.addWidget(self.user_input)

        # User list with transport badges
        if users:
            list_label = QLabel("online users")
            list_label.setStyleSheet("color: #3a5a3a; font-size: 10px; margin-top: 4px;")
            root.addWidget(list_label)

            self.user_list = QListWidget()
            self.user_list.setMaximumHeight(140)
            for username, transport in users:
                blocked = is_cleartext_session and transport != "cleartext"
                badge = {"cleartext": "clr", "wireguard": "wg", "wireguard_extended": "wg+"}.get(transport, "?")
                item = QListWidgetItem(f"  {username}  [{badge}]")
                if blocked:
                    item.setForeground(QColor("#2e4a2e"))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                    item.setToolTip("cleartext sessions cannot DM wireguard users")
                self.user_list.addItem(item)
            self.user_list.itemClicked.connect(
                lambda item: self.user_input.setText(item.text().split("  [")[0].strip())
            )
            root.addWidget(self.user_list)

        if is_cleartext_session:
            note = QLabel("⚠  cleartext sessions cannot DM wireguard users")
            note.setStyleSheet("color: #7a5a1a; font-size: 10px;")
            root.addWidget(note)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def get_username(self) -> str:
        return self.user_input.text().strip().lstrip("@")

class ProtocolLogDialog(QDialog):
    """
    Shows a live log of sent and received protocol packets.
    """
    def __init__(self, log_data: list[tuple[str, str, dict]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("protocol log viewer")
        self.setMinimumSize(750, 550)
        self.setStyleSheet("background-color: #0a0c0a; color: #4ade80;")

        root = QVBoxLayout(self)

        header = QHBoxLayout()
        title = QLabel("PROTOCOL TRAFFIC LOG")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header.addWidget(title)
        header.addStretch()
        root.addLayout(header)

        info = QLabel("Select a packet from the list to see the full MessagePack structure below.")
        info.setStyleSheet("color: #3a5a3a; font-size: 11px; margin-bottom: 5px;")
        root.addWidget(info)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("border: 1px solid #1a281a; background: #0c0e0c;")

        for direction, timestamp, packet in log_data:
            self._add_entry(direction, timestamp, packet)

        root.addWidget(self.list_widget)

        # The "Black Box" (Detail Viewer)
        detail_header = QLabel("PACKET DETAILS (JSON)")
        detail_header.setStyleSheet("color: #3a5a3a; font-size: 10px; font-weight: bold; margin-top: 10px;")
        root.addWidget(detail_header)

        from PyQt6.QtWidgets import QTextEdit
        self.details = QTextEdit()
        self.details.setPlaceholderText("Select a packet to view its contents...")
        self.details.setReadOnly(True)
        self.details.setMaximumHeight(200)
        self.details.setStyleSheet("background: #000; border: 1px solid #1a281a; font-family: 'Consolas', monospace; font-size: 11px; padding: 5px;")
        root.addWidget(self.details)

        self.list_widget.itemClicked.connect(self._show_details)

        close_btn = QPushButton("close log")
        close_btn.setStyleSheet("padding: 8px;")
        close_btn.clicked.connect(self.close)
        root.addWidget(close_btn)

    def _get_packet_summary(self, packet: dict) -> str:
        """Extracts a one-line summary of important packet fields."""
        summary = []
        if 'channel' in packet: summary.append(f"#{packet['channel']}")
        if 'username' in packet: summary.append(f"@{packet['username']}")
        if 'from_username' in packet: summary.append(f"from:{packet['from_username']}")
        if 'to_username' in packet: summary.append(f"to:{packet['to_username']}")
        if 'error' in packet: summary.append(f"ERR:'{packet['error'][:20]}...'")

        msg = packet.get('message')
        if msg:
            clean_msg = str(msg).replace('\n', ' ')
            summary.append(f"msg:'{clean_msg[:30]}...'")

        return " | ".join(summary)

    def _add_entry(self, direction, timestamp, packet):
        import msgpack
        try:
            size = len(msgpack.packb(packet))
        except:
            size = "?"

        type_names = {
            # Requests (Sent)
            1: "CONNECT", 2: "DISCONNECT", 3: "PING", 4: "CH_CREATE", 
            5: "CH_LIST", 6: "CH_INFO", 7: "CH_JOIN", 8: "CH_LEAVE", 
            9: "CH_MSG", 10: "WHOIS", 11: "WHOAMI", 12: "DM_MSG", 
            13: "SET_NICK", 14: "USER_LIST",

            # Responses (Received)
            20: "ERROR", 21: "OK", 22: "CONNECT", 23: "DISCONNECT", 
            24: "PING", 25: "CH_CREATE", 26: "CH_LIST", 27: "CH_INFO", 
            28: "CH_JOIN", 29: "CH_LEAVE", 30: "CH_MSG", 31: "WHOIS", 
            32: "WHOAMI", 33: "DM_MSG", 34: "SET_NICK", 35: "USER_LIST", 
            36: "SRV_MSG", 37: "SHUTDOWN"
        }

        type_val = packet.get('request_type') or packet.get('response_type', '??')
        name = type_names.get(type_val, f"TYPE:{type_val}")
        summary = self._get_packet_summary(packet)

        # Format the list item text with columns
        text = f"[{timestamp}]  {direction.ljust(4)}  ({name.center(10)})  {str(size).rjust(3)}B"
        if summary:
            text += f"  >>  {summary}"
        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, packet)
        if direction == "SENT":
            item.setForeground(QColor("#4ade80"))
        else:
            item.setForeground(QColor("#7aab7a"))
        self.list_widget.addItem(item)
        self.list_widget.scrollToBottom()

    def _show_details(self, item):
        packet = item.data(Qt.ItemDataRole.UserRole)
        import json

        def clean(obj):
            if isinstance(obj, bytes):
                return f"<bytes:0x{obj.hex()}>"
            if isinstance(obj, dict):
                return {k: clean(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [clean(x) for x in obj]
            return obj

        formatted = json.dumps(clean(packet), indent=4)
        self.details.setText(formatted)

    def update_log(self, direction, timestamp, packet):
        self._add_entry(direction, timestamp, packet)