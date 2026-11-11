"""
Controller: glue between the async network layer and the PyQt6 UI.

It:
  - owns an AsyncClient (which in turn owns the socket)
  - connects MainWindow's outgoing signals to async handlers (via qasync)
  - receives unsolicited events from AsyncClient and calls MainWindow's
    public update methods
"""

import asyncio
import logging
import os
import base64
from dotenv import load_dotenv

from network_protocol.async_socket import AsyncClearSocket, AsyncSecureSocket
from network_protocol.async_client import AsyncClient
# Managers encapsulate specific sets of related server interactions, keeping the controller cleaner
from messages.ChannelManager import ChannelManager
from messages.UserManager import UserManager
from ui.dialogs import ProtocolLogDialog
import datetime

logger = logging.getLogger(__name__)

# Response type constants — keeps the handlers readable
RT_OK               = 21
RT_ERROR            = 20
RT_CHANNEL_CREATE   = 25
RT_CHANNEL_LIST     = 26
RT_CHANNEL_INFO     = 27
RT_CHANNEL_JOIN     = 28
RT_CHANNEL_LEAVE    = 29
RT_CHANNEL_MESSAGE  = 30
RT_WHOIS            = 31
RT_WHOAMI           = 32
RT_USER_MESSAGE     = 33
RT_SET_USERNAME     = 34
RT_USER_LIST        = 35
RT_SERVER_MESSAGE   = 36
RT_SERVER_SHUTDOWN  = 37


class UIController:
    """
    Wires MainWindow with AsyncClient.

    Create one after the QApplication exists:
        controller = UIController(window)
    """

    def __init__(self, window):
        self.window = window
        self._client: AsyncClient | None = None

        # Track current view so we know where to route incoming messages
        self._current_channel: str | None = None
        self._current_dm:      str | None = None

        #Initialize managers
        self.channel_manager = None
        self.user_manager = None

        # Joined channels (name is description)
        self._joined_channels: dict[str, str] = {}

        self._user_refresh_task: asyncio.Task | None = None
        self._running = False

        self._message_history: dict[str, str] = {} # channel:name or dm:username
        self._packet_log: list[tuple[str, str, dict]] = []
        self._log_dialog: ProtocolLogDialog | None = None

        # Connect MainWindow signals to async handlers
        window.sig_connect.connect(
            lambda host, port, enc: asyncio.ensure_future(
                self.handle_connect(host, port, enc)
            )
        )
        window.sig_disconnect.connect(
            lambda: asyncio.ensure_future(self.handle_disconnect())
        )
        window.sig_send_message.connect(
            lambda text: asyncio.ensure_future(self.handle_send_message(text))
        )
        window.sig_join_channel.connect(
            lambda name: asyncio.ensure_future(self.handle_join_channel(name))
        )
        window.sig_create_channel.connect(
            lambda name, desc: asyncio.ensure_future(
                self.handle_create_channel(name, desc)
            )
        )
        window.sig_leave_channel.connect(
            lambda: asyncio.ensure_future(self.handle_leave_channel())
        )
        window.sig_new_dm.connect(
            lambda username: asyncio.ensure_future(self.handle_new_dm(username))
        )
        window.sig_set_username.connect(
            lambda name: asyncio.ensure_future(self.handle_set_username(name))
        )
        window.sig_select_channel.connect(
            lambda name: asyncio.ensure_future(self.handle_select_channel(name))
        )
        window.sig_select_user.connect(
            lambda username: asyncio.ensure_future(self.handle_select_user(username))
        )
        window.sig_show_log.connect(self._on_show_log)

    @staticmethod
    def _load_keys() -> tuple[bytes, bytes]:
        load_dotenv()
        user_key_b64   = os.getenv("USER_KEY")
        server_key_b64 = os.getenv("SERVER_KEY")
        if not user_key_b64 or not server_key_b64:
            raise EnvironmentError(
                "USER_KEY and SERVER_KEY must be set in .env (base64 encoded)"
            )
        return base64.b64decode(user_key_b64), base64.b64decode(server_key_b64)

    def _history_key(self) -> str | None:
        if self._current_channel:
            return f"channel:{self._current_channel}"
        elif self._current_dm:
            return f"dm:{self._current_dm}"
        return None

    async def handle_connect(self, host: str, port: int, encrypted: bool):
        print(f"[DEBUG] handle_connect called: host={host} port={port} encrypted={encrypted}")
        try:
            if encrypted:
                user_key, server_key = self._load_keys()
                sock = AsyncSecureSocket(user_key, server_key, host, port)
                await sock.open()
                await sock.establish_tunnel()
            else:
                sock = AsyncClearSocket(host, port)
                await sock.open()

            self._running = True
            self._client = AsyncClient(sock)
            self._client.on_event = self._on_server_event
            self._client.on_log   = self._on_packet_log

            response = await self._client.connect()
            
            #Create the managers after successful connection, passing the client to them
            self.channel_manager = ChannelManager(self._client)
            self.user_manager = UserManager(self._client)

            username = response.get('username', '')
            self.window.update_connection_status(True, host, encrypted, port)
            self.window.set_username(username)

            await self._refresh_channel_list()
            await self._refresh_user_list()

            self._user_refresh_task = asyncio.create_task(self._user_refresh_loop())

        except Exception as exc:
            self.window.show_system_event(f"connection failed: {exc}")
            self.window.update_connection_status(False)

    async def handle_disconnect(self):
        if self._client:
            await self._client.close()
            self._client = None
        self._joined_channels.clear()
        self._current_channel = None
        self._current_dm      = None
        self._running = False
        self.channel_manager = None
        self.user_manager = None
        self.window.update_connection_status(False)
        self.window.show_welcome()

    async def handle_send_message(self, text: str):
        if not self._client: return
        try:
            if self._current_channel:
                # Use ChannelManager
                success, err = await self.channel_manager.sendMessage(self._current_channel, text)
                if success:
                    self.window.add_message(self._client.username or "you", text, is_self=True)
                else:
                    self.window.show_system_event(f"failed to send: {err}")

            elif self._current_dm:
                # Use UserManager
                success, err = await self.user_manager.sendMessage(self._current_dm, text)
                if success:
                    self.window.add_message(self._client.username or "you", text, is_self=True, is_dm=True)
                else:
                    self.window.show_system_event(f"failed to send: {err}")
        except Exception as exc:
            self.window.show_system_event(f"failed to send: {exc}")

    async def handle_join_channel(self, name: str):
        if not self._client: return
        try:
            #Get info from ChannelManager instead of sending raw request in this channel
            success, desc, err = await self.channel_manager.joinChannel(name)

            if success:
                self._save_current_history()
                self._joined_channels[name] = desc
                self._current_channel = name
                self._current_dm = None
                self.window.add_channel(name)
                self.window.open_channel(name, desc)
                self._restore_history(f"channel:{name}")
                await self._refresh_members(name)
                await self._refresh_channel_info(name)
            else:
                self.window.show_system_event(f"could not join {name}: {err}")
        except Exception as exc:
            self.window.show_system_event(f"join failed: {exc}")

    async def handle_create_channel(self, name: str, description: str):
        if not self._client: return
        try:
            success, err = await self.channel_manager.createChannel(name, description)

            if success:
                self._save_current_history()
                self._joined_channels[name] = description
                self._current_channel = name
                self._current_dm = None
                self.window.add_channel(name)
                self.window.open_channel(name, description)
                self._restore_history(f"channel:{name}")
                await self._refresh_members(name)
            else:
                self.window.show_system_event(f"could not create {name}: {err}")
        except Exception as exc:
            self.window.show_system_event(f"create failed: {exc}")

    async def handle_leave_channel(self):
        if not self._client or not self._current_channel: return
        name = self._current_channel
        try:
            await self.channel_manager.leaveChannel(name)
        except Exception:
            pass 
        finally:
            self._joined_channels.pop(name, None)
            self._current_channel = None
            self.window.show_welcome()

    async def handle_select_channel(self, name: str):
        if not self._client:
            return
        if name not in self._joined_channels:
            self.window.show_system_event(f"you are not in #{name} — use /join or the + button to join")
            return
        self._save_current_history()
        self._current_channel = name
        self._current_dm      = None
        desc = self._joined_channels.get(name, '')
        self.window.open_channel(name, desc)
        self._restore_history(f"channel:{name}")
        await self._refresh_members(name)
        await self._refresh_channel_info(name)

    async def handle_new_dm(self, username: str):
        if not self._client:
            return
        self._save_current_history()
        self._current_dm      = username
        self._current_channel = None
        self.window.open_dm(username)
        self._restore_history(f"dm:{username}")

    async def handle_select_user(self, username: str):
        await self.handle_new_dm(username)

    async def handle_set_username(self, name: str):
        if not self._client: return
        try:
            success, new_name, err = await self.user_manager.setUsername(name)
            
            if success:
                self._client.username = new_name
                self.window.set_username(new_name)
            else:
                self.window.show_system_event(f"could not rename: {err}")
        except Exception as exc:
            self.window.show_system_event(f"rename failed: {exc}")

    async def _on_server_event(self, packet: dict):
        msg_type = packet.get('response_type')

        if msg_type == RT_CHANNEL_MESSAGE:
            channel  = packet.get('channel', '')
            sender   = packet.get('username', 'unknown')
            text     = packet.get('message', '')
            if channel == self._current_channel:
                self.window.add_message(sender, text)
            else:
                key = f"channel:{channel}"
                stored = self._message_history.get(key, '')
                # Temporarily render off-screen in chat_panel to get HTML
                self.window.chat_panel.message_view.setHtml(stored)
                self.window.chat_panel.add_message(sender, text)
                self._message_history[key] = self.window.chat_panel.message_view.toHtml()
                # Restore current view
                current_key = self._history_key()
                if current_key:
                    self.window.chat_panel.message_view.setHtml(
                        self._message_history.get(current_key, '')
                    )
                else:
                    self.window.chat_panel.clear_messages()
                
                # Increment unread count
                unread = self.window.sidebar.get_unread("channel", channel)
                self.window.sidebar.set_unread("channel", channel, unread + 1)

        elif msg_type == RT_CHANNEL_JOIN:
            user    = packet.get('username', 'someone')
            channel = packet.get('channel', '')
            if channel == self._current_channel:
                self.window.show_system_event(f"{user} joined {channel}")
                await self._refresh_members(channel)

        elif msg_type == RT_CHANNEL_LEAVE:
            user    = packet.get('username', 'someone')
            channel = packet.get('channel', '')
            if channel == self._current_channel:
                self.window.show_system_event(f"{user} left {channel}")
                await self._refresh_members(channel)

        elif msg_type == RT_USER_MESSAGE:
            sender = packet.get('from_username', 'unknown')
            text   = packet.get('message', '')
            key    = f"dm:{sender}"

            # Add sender to sidebar so the DM exists
            self.window.sidebar.add_dm(sender)

            # If we're currently viewing this DM, show it live
            if self._current_dm == sender and self._current_channel is None:
                self.window.add_message(sender, text, is_dm=True)
                self._save_current_history()
            else:
                # Store in history without switching view
                # Temporarily render the message off-screen by appending to stored html
                stored = self._message_history.get(key, '')
                # Use the chat panel briefly only if we're not mid-view
                self.window.chat_panel.message_view.setHtml(stored)
                self.window.chat_panel.add_message(sender, text, is_dm=True)
                self._message_history[key] = self.window.chat_panel.message_view.toHtml()
                # Restore current view
                current_key = self._history_key()
                if current_key:
                    self.window.chat_panel.message_view.setHtml(
                        self._message_history.get(current_key, '')
                    )
                else:
                    self.window.chat_panel.clear_messages()
                
                # Increment unread count
                unread = self.window.sidebar.get_unread("dm", sender)
                self.window.sidebar.set_unread("dm", sender, unread + 1)

        elif msg_type == RT_SET_USERNAME:
            old = packet.get('old_username', '')
            new = packet.get('new_username', '')
            self.window.show_system_event(f"{old} is now known as {new}")
            await self._refresh_user_list()

        elif msg_type == RT_SERVER_MESSAGE:
            self.window.show_server_message(packet.get('message', ''))

        elif msg_type == RT_SERVER_SHUTDOWN:
            self.window.show_shutdown_notice(packet.get('message', ''))
            await self.handle_disconnect()

    async def _refresh_channel_list(self):
        """Fetch all channels (handles pagination) and update the sidebar."""
        if not self._client: return
        channels = []
        offset = 0
        while True:
            try:
                # Use Manager
                ch_list, has_next = await self.channel_manager.listChannels(offset)
                channels.extend(ch_list)
                if has_next:
                    offset += 10
                else:
                    break
            except Exception:
                break
        self.window.set_available_channels(channels)

    async def _refresh_user_list(self):
        """Fetch all online users (handles pagination) and update the sidebar."""
        if not self._client: return
        raw_users = []
        offset = 0
        while True:
            try:
                # Use Manager
                u_list, has_next = await self.user_manager.userList(offset)
                for u in u_list:
                    if isinstance(u, dict):
                        raw_users.append((u.get('username', ''), u.get('transport', '')))
                    else:
                        raw_users.append((str(u), ''))
                if has_next:
                    offset += 20
                else:
                    break
            except Exception:
                break

        # Concurrently fetch transport information using WHOIS
        async def fetch_transport(username, transport):
            if transport:
                return username, transport
            try:
                info = await self.user_manager.whoIs(username)
                if info.get('response_type') == 31:
                    return username, info.get('transport', '')
            except Exception:
                pass
            return username, ''

        tasks = [fetch_transport(u, t) for u, t in raw_users]
        resolved_users = await asyncio.gather(*tasks)
        self.window.set_users(list(resolved_users))

    async def _refresh_members(self, channel: str):
        """Fetch the member list for a channel and update the members tab."""
        if not self._client: return
        members = []
        offset = 0
        while True:
            try:
                # Use Manager with channel parameter
                u_list, has_next = await self.user_manager.userList(offset, channel=channel)
                for u in u_list:
                    members.append(u.get('username', '') if isinstance(u, dict) else str(u))
                if has_next:
                    offset += 20
                else:
                    break
            except Exception:
                break
        self.window.set_members(members)

    async def _refresh_channel_info(self, channel: str):
        """Fetch channel info and update the info tab."""
        if not self._client: return
        try:
            desc, err = await self.channel_manager.getChannelInfo(channel)
            if not err:
                self.window.set_channel_info(channel, desc)
        except Exception:
            pass

    async def _user_refresh_loop(self):
        while self._client and self._running:
            await asyncio.sleep(15)
            await self._refresh_user_list()
            await self._refresh_channel_list()

    def _save_current_history(self):
        key = self._history_key()
        if key:
            self._message_history[key] = self.window.chat_panel.message_view.toHtml()

    def _restore_history(self, key: str):
        html = self._message_history.get(key)
        if html:
            self.window.chat_panel.message_view.setHtml(html)
        else:
            self.window.chat_panel.clear_messages()

    def _on_packet_log(self, direction: str, packet: dict):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = (direction, timestamp, packet)
        self._packet_log.append(entry)
        if self._log_dialog and self._log_dialog.isVisible():
            self._log_dialog.update_log(direction, timestamp, packet)

    def _on_show_log(self):
        if not self._log_dialog:
            self._log_dialog = ProtocolLogDialog(self._packet_log, self.window)
        self._log_dialog.show()
        self._log_dialog.raise_()
        self._log_dialog.activateWindow()
