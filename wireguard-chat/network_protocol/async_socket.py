"""
Async UDP socket wrappers.
AsyncClearSocket: cleartext msgpack over UDP
AsyncSecureSocket: WireGuard-encrypted msgpack over UDP

Both expose the same interface so async_client never has to care which one it has.
"""

import asyncio
import msgpack
from encryption.encryption_protocol import WireGuardProtocol


class _UDPProtocol(asyncio.DatagramProtocol):
    """Low-level asyncio protocol.  Incoming datagrams are put onto a queue."""

    def __init__(self):
        self._queue: asyncio.Queue[bytes] = asyncio.Queue()
        self._transport: asyncio.DatagramTransport | None = None

    def connection_made(self, transport: asyncio.DatagramTransport):
        self._transport = transport

    def datagram_received(self, data: bytes, addr):
        self._queue.put_nowait(data)

    def error_received(self, exc: Exception):
        pass  # UDP errors are non-fatal; let recv timeout if needed

    def connection_lost(self, exc):
        pass

    def send(self, data: bytes):
        if self._transport is None:
            raise RuntimeError("Socket not connected")
        self._transport.sendto(data)

    async def recv(self, timeout: float = 10.0) -> bytes:
        return await asyncio.wait_for(self._queue.get(), timeout=timeout)

    def close(self):
        if self._transport:
            self._transport.close()

class AsyncSocketBase:
    """Common open/close for both socket variants."""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._proto: _UDPProtocol | None = None

    async def open(self):
        loop = asyncio.get_running_loop()
        _, proto = await loop.create_datagram_endpoint(
            _UDPProtocol,
            remote_addr=(self.host, self.port),
        )
        self._proto = proto

    def close(self):
        if self._proto:
            self._proto.close()
            self._proto = None

    # Subclasses override these two
    async def send_dict(self, payload: dict):
        raise NotImplementedError

    async def recv_dict(self, timeout: float = 10.0) -> dict:
        raise NotImplementedError

class AsyncClearSocket(AsyncSocketBase):
    """
    Sends and receives plain msgpack dicts over UDP.
    No encryption, no handshake.
    """

    async def send_dict(self, payload: dict):
        if self._proto is None:
            raise RuntimeError("Call open() first.")
        self._proto.send(msgpack.packb(payload))

    async def recv_dict(self, timeout: float = 10.0) -> dict:
        if self._proto is None:
            raise RuntimeError("Call open() first.")
        raw = await self._proto.recv(timeout)
        return msgpack.unpackb(raw, raw=False)

class AsyncSecureSocket(AsyncSocketBase):
    """
    Performs the WireGuard-like handshake, then sends/receives encrypted
    msgpack dicts.  Drop-in replacement for AsyncClearSocket.
    """

    def __init__(self, my_priv_key: bytes, server_pub_key: bytes,
                 host: str = "csc4026z.link", port: int = 51820):
        super().__init__(host, port)
        self._proto_wg = WireGuardProtocol(my_priv_key, server_pub_key)

    async def establish_tunnel(self, timeout: float = 10.0):
        """
        Executes the WireGuard handshake.
        Handles cookie-retry automatically.
        Must be awaited before send_dict / recv_dict.
        """
        if self._proto is None:
            raise RuntimeError("Call open() first.")

        await self._do_handshake(timeout)
        if not self._proto_wg.is_transport_ready:
            raise ConnectionError("WireGuard handshake failed.")

    async def _do_handshake(self, timeout: float):
        init_pkt = self._proto_wg.create_initiation_packet()
        self._proto.send(init_pkt)

        response = await self._proto.recv(timeout)
        status = self._proto_wg.handle_response_packet(response)

        if status == "COOKIE_RETRY":
            retry_pkt = self._proto_wg.create_initiation_packet()
            self._proto.send(retry_pkt)
            final = await self._proto.recv(timeout)
            status = self._proto_wg.handle_response_packet(final)

        if status != "SUCCESS":
            raise ConnectionError("Handshake failed after cookie retry.")

    async def send_dict(self, payload: dict):
        if self._proto is None:
            raise RuntimeError("Call open() first.")
        if not self._proto_wg.is_transport_ready:
            raise RuntimeError("Call establish_tunnel() before sending data.")
        packed = msgpack.packb(payload)
        encrypted = self._proto_wg.encrypt_message(packed)
        self._proto.send(encrypted)

    async def recv_dict(self, timeout: float = 10.0) -> dict:
        if self._proto is None:
            raise RuntimeError("Call open() first.")
        raw = await self._proto.recv(timeout)
        decrypted = self._proto_wg.decrypt_message(raw)
        return msgpack.unpackb(decrypted, raw=False)