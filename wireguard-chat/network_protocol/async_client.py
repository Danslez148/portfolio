"""
AsyncClient sits above the socket layer and owns:
  - a continuous receive loop that routes packets to the right place
  - a ping loop that keeps the session alive every 30 s
  - a futures map so send_request() returns an awaitable result
  - an event callback for unsolicited server messages
"""

import asyncio
import logging
from typing import Callable, Awaitable

from network_protocol.async_socket import AsyncSocketBase
from messages.ServerMessageGenerator import ServerMessage

logger = logging.getLogger(__name__)


class AsyncClient:
    """
    Async client.

    Usage(note):
        client = AsyncClient(socket)
        await client.connect()              # sends CONNECT, stores session_id
        response = await client.send_request(ServerMessage.ping(client.session_id))
        client.on_event = my_async_handler  # called for unsolicited packets
        await client.close()
    """

    PING_INTERVAL = 30.0   # seconds between pings
    RECV_TIMEOUT  = 5.0    # per-packet recv timeout (loops on TimeoutError)

    def __init__(self, socket: AsyncSocketBase):
        self._socket  = socket
        self.session_id: int | None = None
        self.username:   str | None = None

        # request_handle -> Future[dict]
        self._pending: dict[int, asyncio.Future] = {}

        # Called with every unsolicited packet (response_handle is None)
        # Signature: async def handler(packet: dict) -> None
        self.on_event: Callable[[dict], Awaitable[None]] | None = None

        # Logging callback for the protocol logger
        # Signature: def logger_cb(direction: str, packet: dict) -> None
        self.on_log: Callable[[str, dict], None] | None = None

        self._recv_task: asyncio.Task | None = None
        self._ping_task: asyncio.Task | None = None
        self._running = False

    async def connect(self) -> dict:
        """
        Send CONNECT, wait for the response, store session_id + username,
        then start the background loops.
        """
        request = ServerMessage.connect()
        # CONNECT has no session field, send manually before loops start
        if self.on_log: self.on_log("SENT", request)
        await self._socket.send_dict(request)
        response = await self._socket.recv_dict(timeout=10.0)
        if self.on_log: self.on_log("RECV", response)

        if response.get('response_type') != 22:
            raise ConnectionError(
                f"CONNECT failed: {response.get('error', 'unknown error')}"
            )

        self.session_id = response['session']
        self.username   = response.get('username')
        self._running   = True

        self._recv_task = asyncio.create_task(self._recv_loop(), name="recv_loop")
        self._ping_task = asyncio.create_task(self._ping_loop(), name="ping_loop")

        logger.info("Connected as '%s' (session %s)", self.username, self.session_id)
        return response

    async def close(self):
        """Graceful disconnect, sends DISCONNECT then tears down."""
        self._running = False

        if self.session_id is not None:
            try:
                await self.send_request(
                    ServerMessage.disconnect(self.session_id),
                    timeout=5.0
                )
            except Exception:
                pass

        for task in (self._recv_task, self._ping_task):
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        # Resolve any still-pending futures with an error
        for fut in self._pending.values():
            if not fut.done():
                fut.set_exception(ConnectionError("Client closed"))
        self._pending.clear()

        self._socket.close()
        self.session_id = None
        self.username   = None

    async def send_request(self, request: dict, timeout: float = 10.0) -> dict:
        """
        Send *request* and return the matching response dict.
        Raises asyncio.TimeoutError if no response arrives within *timeout* s.
        """
        handle = request['request_handle']
        loop   = asyncio.get_running_loop()
        fut: asyncio.Future[dict] = loop.create_future()
        self._pending[handle] = fut

        if self.on_log: self.on_log("SENT", request)
        await self._socket.send_dict(request)

        try:
            return await asyncio.wait_for(fut, timeout=timeout)
        except asyncio.TimeoutError:
            self._pending.pop(handle, None)
            raise
        finally:
            self._pending.pop(handle, None)

    async def _recv_loop(self):
        """Continuously reads packets and routes them."""
        while self._running:
            try:
                packet = await self._socket.recv_dict(timeout=self.RECV_TIMEOUT)
                if self.on_log: self.on_log("RECV", packet)
            except asyncio.TimeoutError:
                continue  # normal, just no data right now
            except Exception as exc:
                if self._running:
                    logger.warning("recv_loop error: %s", exc)
                break

            self._route(packet)

    async def _ping_loop(self):
        """Sends a PING every PING_INTERVAL seconds."""
        while self._running:
            await asyncio.sleep(self.PING_INTERVAL)
            if not self._running or self.session_id is None:
                break
            try:
                await self.send_request(
                    ServerMessage.ping(self.session_id),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                logger.warning("Ping timed out — server may have dropped the session")
            except Exception as exc:
                logger.warning("Ping error: %s", exc)

    def _route(self, packet: dict):
        handle = packet.get('response_handle')

        # Session guard: ignore packets for other sessions
        packet_session = packet.get('session')
        if (self.session_id is not None
                and packet_session is not None
                and packet_session != self.session_id):
            return

        if handle is not None:
            # Solicited response, resolve the waiting Future
            fut = self._pending.get(handle)
            if fut and not fut.done():
                fut.set_result(packet)
        else:
            # Unsolicited event
            self._dispatch_event(packet)

    def _dispatch_event(self, packet: dict):
        """Fire the on_event callback (schedules it as a task if it's a coroutine)."""
        if self.on_event is None:
            return
        result = self.on_event(packet)
        if asyncio.iscoroutine(result):
            asyncio.create_task(result)