import copy
import json


def format_msg_from_libp2p(message: dict) -> dict:
    protocol = message.get("protocol")
    message_copy = copy.deepcopy(message)
    message_copy.pop("protocol", None)
    return message_copy


def format_msg_to_libp2p(data: str, protocol: str, server_peer_id: str, save_data: bool) -> str:
    message = {"protocol": protocol, "serverPeerId": server_peer_id, "save_data": save_data, "data": data}
    return json.dumps(message)


def format_msg_for_subscribing(protocols: list) -> str:
    msg = {"protocols_to_listen": protocols}
    return json.dumps(msg)
