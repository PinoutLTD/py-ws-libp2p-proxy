from dataclasses import dataclass
import typing as tp


@dataclass
class ProtocolsManager:
    protocols: tp.Dict[str, tp.Callable] = {}

    def add_protocol(self, protocol, callback):
        self.protocols[protocol] = callback

    def remove_protocol(self, protocol):
        self.protocols.pop(protocol, None)

    def get_protocols(self) -> list:
        return list(self.protocols.keys())

    def remove_all_protocols(self):
        self.protocols = {}
