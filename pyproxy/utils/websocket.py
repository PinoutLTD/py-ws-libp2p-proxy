import asyncio
import websockets
import typing as tp
import json
from .logger import logger
from .message import format_msg_from_libp2p, format_msg_for_subscribing
from .decorators import set_websocket
from .protocols_manager import ProtocolsManager


class WebsocketClient:
    def __init__(
        self, protocols_manager: ProtocolsManager, proxy_server_url: str, peer_id_callback: tp.Optional[tp.Callable]
    ) -> None:
        self.websocket = None
        self.proxy_server_url: str = proxy_server_url
        self.is_listening = False
        self.protocols_manager = protocols_manager
        self.peer_id_callback = peer_id_callback

    @set_websocket
    async def set_listener(self) -> None:
        try:
            logger.debug(f"Is connected: {self.is_listening}")
            if self.is_listening:
                return
            self.is_listening = True
            logger.debug(f"Connected to WebSocket server at {self.proxy_server_url}")
            await self._consumer_handler()

        except websockets.exceptions.ConnectionClosedOK:
            self.is_listening = False
            logger.debug(f"Websockets connection closed")

        except Exception as e:
            self.is_listening = False
            logger.error(f"Websocket exception: {e}")
            await asyncio.sleep(5)
            await self._reconnect()

    @set_websocket
    async def send_msg(self, msg: str) -> None:
        await self.websocket.send(msg)

    async def send_msg_to_subscribe(self, protocols: list) -> None:
        logger.debug(f"Subscribing to: {protocols}")
        msg = format_msg_for_subscribing(protocols)
        await self.send_msg(msg)

    async def close_connection(self) -> None:
        if self.websocket is not None:
            await self.websocket.close()

    async def _consumer_handler(self) -> None:
        while True:
            message = await self.websocket.recv()
            logger.debug(f"Received message from server: {message}")
            await self._consumer(message)

    async def _consumer(self, message: str) -> None:
        message = json.loads(message)
        if "peerId" in message:
            if self.peer_id_callback is not None:
                self.peer_id_callback(message["peerId"])
                return
        if message.get("protocol") in self.protocols_manager.protocols:
            protocol = message.get("protocol")
            formated_msg = format_msg_from_libp2p(message)
            self.protocols_manager.protocols[protocol](formated_msg)

    async def _reconnect(self) -> None:
        logger.debug(f"Reconnecting...")
        self.websocket = None
        asyncio.ensure_future(self.set_listener())
        while self.websocket is None:
            await asyncio.sleep(0.1)
            if not self.is_listening:
                return
        logger.debug(f"Callbacks to resubscribe: {self.protocols_manager.protocols}")
        await self.send_msg_to_subscribe(self.protocols_manager.protocols)
