import asyncio
import typing as tp
from .utils.websocket import WebsocketClient
from .utils.message import format_msg_to_libp2p
from .utils.protocols_manager import ProtocolsManager, Callback, CallbackTypes


class Libp2pProxyAPI:
    def __init__(self, proxy_server_url: str, peer_id_callback: tp.Optional[tp.Callable] = None) -> None:
        self.protocols_manager = ProtocolsManager()
        self.ws_client = WebsocketClient(self.protocols_manager, proxy_server_url, peer_id_callback)

    async def subscribe_to_protocol_sync(self, protocol: str, callback: tp.Callable) -> None:
        asyncio.ensure_future(self.ws_client.set_listener())
        callback_obj = Callback(callback, CallbackTypes.SyncType)
        self.protocols_manager.add_protocol(protocol, callback_obj)
        protocols = self.protocols_manager.get_protocols()
        await self.ws_client.send_msg_to_subscribe(protocols)

    async def subscribe_to_protocol_async(self, protocol: str, callback: tp.Callable) -> None:
        asyncio.ensure_future(self.ws_client.set_listener())
        callback_obj = Callback(callback, CallbackTypes.AsyncType)
        self.protocols_manager.add_protocol(protocol, callback_obj)
        protocols = self.protocols_manager.get_protocols()
        await self.ws_client.send_msg_to_subscribe(protocols)

    async def send_msg_to_libp2p(
        self, data: str, protocol: str, server_peer_id: str = "", save_data: bool = False
    ) -> None:
        msg = format_msg_to_libp2p(data, protocol, server_peer_id, save_data)
        await self.ws_client.send_msg(msg)

    async def unsubscribe_from_protocol(self, protocol: str) -> None:
        self.protocols_manager.remove_protocol(protocol)
        protocols = self.protocols_manager.get_protocols()
        await self.ws_client.send_msg_to_subscribe(protocols)
        if not protocols:
            await self.ws_client.close_connection()

    async def unsubscribe_from_all_protocols(self) -> None:
        self.protocols_manager.remove_all_protocols()
        protocols = self.protocols_manager.get_protocols()
        await self.ws_client.send_msg_to_subscribe(protocols)
        await self.ws_client.close_connection()
