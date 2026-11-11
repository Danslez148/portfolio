"""
Entry point for WireGuardChat

Runs the asyncio event loop inside PyQt6's event loop using qasync,
so all async/await code and all UI code live on the same thread.
"""

import sys
import asyncio
import logging

from PyQt6.QtWidgets import QApplication
import qasync

from ui import MainWindow
from controller import UIController


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main():
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow(show_connect_dialog=False)  # don't show dialog yet
    controller = UIController(window)               # wire up signals first
    window._show_connect_dialog()
    window.show()                

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()