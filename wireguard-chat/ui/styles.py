# Palette / Theme

STYLE = """
QWidget {
    background-color: #0d0f0d;
    color: #7aab7a;
    font-family: 'Courier New', monospace;
    font-size: 12px;
}

/* Sidebar */
#sidebar {
    background-color: #0a0c0a;
    border-right: 1px solid #1a281a;
}
#sidebar QLabel {
    color: #3a5a3a;
    font-size: 10px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* Section headers inside sidebar */
#section-label {
    color: #3a5a3a;
    font-size: 10px;
}

/* List widgets (channels / users) */
QListWidget {
    background: transparent;
    border: none;
    outline: none;
}
QListWidget::item {
    color: #6b8f6b;
    padding: 4px 8px;
    border-radius: 4px;
}
QListWidget::item:hover {
    background-color: #111f11;
    color: #a3d9a3;
}
QListWidget::item:selected {
    background-color: #152415;
    color: #4ade80;
}

/* Main chat area */
#main-panel {
    background-color: #0d0f0d;
}

/* Chat header */
#chat-header {
    background-color: #0a0c0a;
    border-bottom: 1px solid #1a281a;
    padding: 8px 16px;
}

/* Tab bar */
QTabWidget::pane {
    border: none;
    background: transparent;
}
QTabBar::tab {
    background: transparent;
    color: #3a5a3a;
    padding: 4px 14px;
    font-size: 11px;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected {
    color: #4ade80;
    border-bottom: 2px solid #4ade80;
}
QTabBar::tab:hover {
    color: #a3d9a3;
}

/* Message display */
QTextEdit {
    background: transparent;
    border: none;
    color: #7aab7a;
    selection-background-color: #1a281a;
}

/* Input box */
#input-frame {
    background-color: #0a0c0a;
    border: 1px solid #1a281a;
    border-radius: 4px;
    padding: 2px 8px;
}
#input-field {
    background: transparent;
    border: none;
    color: #4ade80;
    font-family: 'Courier New', monospace;
    font-size: 12px;
}
#input-field:focus {
    outline: none;
}

/* Hint label below input */
#input-hint {
    color: #2e4a2e;
    font-size: 10px;
}

/* Buttons */
QPushButton {
    background: transparent;
    border: 1px solid #1a281a;
    color: #4ade80;
    padding: 5px 14px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
}
QPushButton:hover {
    background-color: #111f11;
    border-color: #4ade80;
}
QPushButton:pressed {
    background-color: #152415;
}

/* Small icon button ("+") */
#icon-btn {
    background: transparent;
    border: none;
    color: #2e4a2e;
    font-size: 16px;
    padding: 0 2px;
    min-width: 18px;
    max-width: 18px;
}
#icon-btn:hover {
    color: #4ade80;
}

#log-btn {
    background: transparent;
    border: 1px solid #1a281a;
    color: #4ade80;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 10px;
    font-family: 'Courier New', monospace;
}
#log-btn:hover {
    background-color: #111f11;
    border-color: #4ade80;
}

/* Line edit (dialogs) */
QLineEdit {
    background-color: #0a0c0a;
    border: 1px solid #1a281a;
    color: #4ade80;
    padding: 5px 8px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
}
QLineEdit:focus {
    border-color: #4ade80;
}

/* Dialog */
QDialog {
    background-color: #0d0f0d;
    border: 1px solid #1a281a;
}

/* Separator lines */
#h-sep {
    background-color: #1a281a;
    max-height: 1px;
    min-height: 1px;
}

/* Connection status dot (set via property) */
#status-dot[status="connected"] { color: #4ade80; }
#status-dot[status="disconnected"] { color: #444444; }

/* Me bar at bottom of sidebar */
#me-bar {
    background-color: #0a0c0a;
    border-top: 1px solid #1a281a;
    padding: 8px 14px;
}
"""