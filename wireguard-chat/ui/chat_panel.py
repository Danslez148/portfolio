from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QLabel, QPushButton, QTabWidget, QFrame, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QTextCursor


class ChatPanel(QWidget):
    """
    Main right-hand panel. Shared between channel and DM views.
    The header and tabs adjust based on context.
    """

    # Signals
    message_sent    = pyqtSignal(str)   # raw text from input
    leave_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("main-panel")
        self._current_context = None  # ('channel', name) or ('dm', username)

        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # Header
        self.header = QWidget()
        self.header.setObjectName("chat-header")
        self.header.setStyleSheet("background: #0a0c0a; border-bottom: 1px solid #1a281a;")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(18, 10, 18, 10)

        self.header_name = QLabel("")
        self.header_name.setStyleSheet("color: #4ade80; font-size: 14px; font-weight: bold;")
        self.header_desc = QLabel("")
        self.header_desc.setStyleSheet("color: #3a5a3a; font-size: 11px; margin-left: 6px;")
        self.header_count = QLabel("")
        self.header_count.setStyleSheet("color: #3a5a3a; font-size: 11px;")

        self.leave_btn = QPushButton("leave")
        self.leave_btn.setStyleSheet("font-size: 10px; padding: 3px 8px;")
        self.leave_btn.clicked.connect(self.leave_requested.emit)
        self.leave_btn.hide()

        header_layout.addWidget(self.header_name)
        header_layout.addWidget(self.header_desc)
        header_layout.addStretch()
        header_layout.addWidget(self.header_count)
        header_layout.addWidget(self.leave_btn)
        root.addWidget(self.header)

        # Tabs (messages | info | members) — only shown for channels
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # Tab 1: Messages
        msg_tab = QWidget()
        msg_layout = QVBoxLayout(msg_tab)
        msg_layout.setSpacing(0)
        msg_layout.setContentsMargins(0, 0, 0, 0)
        self.message_view = QTextEdit()
        self.message_view.setReadOnly(True)
        self.message_view.setObjectName("message-view")
        msg_layout.addWidget(self.message_view)
        self.tabs.addTab(msg_tab, "messages")

        # Tab 2: Info
        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)
        info_layout.setContentsMargins(18, 14, 18, 14)
        info_layout.setSpacing(8)
        self.info_name_lbl    = QLabel("")
        self.info_name_lbl.setStyleSheet("color: #4ade80; font-size: 14px; font-weight: bold;")
        self.info_desc_lbl    = QLabel("")
        self.info_desc_lbl.setWordWrap(True)
        info_layout.addWidget(self.info_name_lbl)
        info_layout.addWidget(self.info_desc_lbl)
        info_layout.addStretch()
        self.tabs.addTab(info_tab, "info")

        # Tab 3: Members
        members_tab = QWidget()
        members_layout = QVBoxLayout(members_tab)
        members_layout.setContentsMargins(0, 0, 0, 0)
        self.members_list = QListWidget()
        members_layout.addWidget(self.members_list)
        self.tabs.addTab(members_tab, "members")

        root.addWidget(self.tabs)

        # Input area
        input_container = QWidget()
        input_container.setStyleSheet("padding: 10px 18px 14px 18px;")
        input_v = QVBoxLayout(input_container)
        input_v.setSpacing(4)
        input_v.setContentsMargins(0, 0, 0, 0)

        input_frame = QFrame()
        input_frame.setObjectName("input-frame")
        input_frame.setStyleSheet(
            "background: #0a0c0a; border: 1px solid #1a281a; border-radius: 4px;"
        )
        input_row = QHBoxLayout(input_frame)
        input_row.setContentsMargins(10, 6, 10, 6)
        input_row.setSpacing(8)

        prompt = QLabel("$")
        prompt.setStyleSheet("color: #2e4a2e; font-size: 13px;")
        self.input_field = QLineEdit()
        self.input_field.setObjectName("input-field")
        self.input_field.setPlaceholderText("type a message...")
        self.input_field.returnPressed.connect(self._on_send)

        input_row.addWidget(prompt)
        input_row.addWidget(self.input_field)
        input_v.addWidget(input_frame)

        self.hint_label = QLabel("enter to send  ·  /join #channel  ·  /dm @user  ·  /who  ·  /leave")
        self.hint_label.setObjectName("input-hint")
        self.hint_label.setStyleSheet("color: #2e4a2e; font-size: 10px;")
        input_v.addWidget(self.hint_label)

        root.addWidget(input_container)

    def _on_send(self):
        text = self.input_field.text().strip()
        if text:
            self.input_field.clear()
            self.message_sent.emit(text)

    # Context switching

    def switch_to_channel(self, name: str, description: str = "", member_count: int = 0):
        self._current_context = ("channel", name)
        self.header_name.setText(f"# {name}")
        self.header_desc.setText(f"— {description}" if description else "")
        self.header_count.setText(f"{member_count} members" if member_count else "")
        self.leave_btn.show()
        self.tabs.setTabVisible(1, True)   # info tab
        self.tabs.setTabVisible(2, True)   # members tab
        self.tabs.setCurrentIndex(0)

    def switch_to_dm(self, username: str):
        self._current_context = ("dm", username)
        self.header_name.setText(f"@ {username}")
        self.header_desc.setText("")
        self.header_count.setText("")
        self.leave_btn.show()
        self.tabs.setTabVisible(1, False)  # no info tab for DMs
        self.tabs.setTabVisible(2, False)  # no members tab for DMs
        self.tabs.setCurrentIndex(0)

    # Public methods — called by controller

    def add_message(self, sender: str, text: str, timestamp: str = "",
                    is_self: bool = False, is_system: bool = False, is_dm: bool = False):
        """Append a formatted message to the chat view."""
        cursor = self.message_view.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        ts_html = f'<span style="color:#2e4a2e; font-size:10px;">{timestamp}</span> ' if timestamp else ""

        if is_system:
            html = (
                f'{ts_html}'
                f'<span style="color:#2e4a2e; font-style:italic;">{text}</span><br>'
            )
        elif is_dm:
            html = (
                f'<div style="background:#0f1a0f; border-left:2px solid #4ade80; '
                f'padding:4px 8px; margin:2px 0;">'
                f'<span style="color:#4ade80; font-weight:bold;">{sender}</span> '
                f'{ts_html}'
                f'<br><span style="color:#86efac;">{text}</span></div><br>'
            )
        elif is_self:
            html = (
                f'<span style="color:#4ade80; font-weight:bold;">you</span> '
                f'{ts_html}<br>'
                f'<span style="color:#7aab7a;">{text}</span><br>'
            )
        else:
            html = (
                f'<span style="color:#86efac; font-weight:bold;">{sender}</span> '
                f'{ts_html}<br>'
                f'<span style="color:#7aab7a;">{text}</span><br>'
            )

        cursor.insertHtml(html)
        self.message_view.setTextCursor(cursor)
        self.message_view.ensureCursorVisible()

    def show_system_event(self, msg: str):
        self.add_message("", msg, is_system=True)

    def set_channel_info(self, name: str, description: str):
        self.info_name_lbl.setText(f"# {name}")
        self.info_desc_lbl.setText(description)

    def set_members(self, members: list[str]):
        self.members_list.clear()
        for m in members:
            self.members_list.addItem(f"  {m}")

    def clear_messages(self):
        self.message_view.clear()