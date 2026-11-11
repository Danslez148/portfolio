from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

# Welcome / empty state panel

class WelcomePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel("[ select a channel or DM ]")
        lbl.setStyleSheet("color: #2e4a2e; font-size: 13px; letter-spacing: 2px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)

        sub = QLabel("or use /join #channel to get started")
        sub.setStyleSheet("color: #1a281a; font-size: 11px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)
