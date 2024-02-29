from functools import wraps
import websockets


def set_websocket(func):
    """Check if a websocket exists and create a new otherwise.

    :param func: Wrapped function.
    :return: Wrapped function after decoration.
    """

    @wraps(func)
    async def wrapper(ws_client_instance, *args, **kwargs):
        """
        :param ws_client_instance: WebsocketClient instance in a decorated function.
        :param args: Wrapped function args.
        :param kwargs: Wrapped function kwargs
        """
        if ws_client_instance.websocket is None:
            async with websockets.connect(ws_client_instance.proxy_server_url, ping_timeout=None) as websocket:
                ws_client_instance.websocket = websocket
                res = await func(ws_client_instance, *args, **kwargs)
                return res
        res = await func(ws_client_instance, *args, **kwargs)
        return res

    return wrapper
