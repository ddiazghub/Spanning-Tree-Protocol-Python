from __future__ import annotations
from typing import Dict, List, Set
from sys import maxsize as MAX_INT

DEFAULT_PORT_COST = 1
DEFAULT_BID = 32768

class Port:
    BLOCKED = 0
    ROOT = 1
    DESIGNATED = 2

    port_id: int
    cost: int
    dest_switch: Switch
    dest_port: Port
    port_type: int
    switch: Switch

    def __init__(self, port_id: int, switch: Switch, cost = DEFAULT_PORT_COST) -> None:
        self.port_id = port_id
        self.switch = switch
        self.cost = cost
        self.port_type = Port.BLOCKED
        self.dest_switch = None
        self.dest_port = None

    def link(self, port: Port) -> None:
        self.dest_switch = port.switch
        self.dest_port = port
        port.dest_switch = self.switch
        port.dest_port = self
    
    def is_linked(self) -> bool:
        return self.dest_switch is not None and self.dest_port is not None

    def get_total_cost(self) -> int:
        if not self.is_linked():
            return None
        
        remaining = self.dest_switch.total_cost

        return self.cost + remaining if remaining is not None else None

    def type_string(self) -> str:
        if self.port_type == Port.BLOCKED:
            return "BLOCKED"

        if self.port_type == Port.ROOT:
            return "ROOT"

        if self.port_type == Port.DESIGNATED:
            return "DESIGNATED"

    def __str__(self) -> str:
        total_cost = 0 if self.switch.is_root else self.get_total_cost()

        return f"   Port {self.port_id} is {self.type_string()}. Total cost: {'inf' if total_cost is None else total_cost}"

class Switch:
    switch_id: int
    bridge_id: int
    ports: Dict[int, Port]
    root_port: Port
    total_cost: int
    is_root: bool

    def __init__(self, switch_id: int, is_root = False, bridge_id = DEFAULT_BID) -> None:
        self.switch_id = switch_id
        self.bridge_id = bridge_id
        self.ports = dict()
        self.root_port = None
        self.total_cost = 0 if is_root else None
        self.is_root = is_root

    def add_port(self, port_id: int, cost = DEFAULT_PORT_COST) -> None:
        port = Port(port_id, self, cost)
        self.ports[port_id] = port

        if self.is_root:
            port.port_type = port.DESIGNATED

    def find_root_port(self) -> None:
        minimum_cost = MAX_INT
        ports = []

        for port in self.ports.values():
            total_cost = port.get_total_cost()

            if total_cost is None:
                continue

            if total_cost < minimum_cost:
                minimum_cost = total_cost
                ports = [port]
            elif total_cost == minimum_cost:
                ports.append(port)

        minimum_pid = MAX_INT
        p: Port = None

        for port in ports:
            if port.port_id < minimum_pid:
                minimum_pid = port.port_id
                p = port

        if p is None:
            return

        self.root_port = p
        self.total_cost = p.get_total_cost()
        p.port_type = p.ROOT
        p.dest_port.port_type = Port.DESIGNATED

        for port in self.ports.values():
            if port.get_total_cost() is not None and (port.port_type, port.dest_port.port_type) == (Port.BLOCKED, Port.BLOCKED):
                if self.total_cost <= port.dest_switch.total_cost:
                    port.port_type = Port.DESIGNATED
                else:
                    port.dest_port.port_type = Port.DESIGNATED

    def neighbors(self) -> List[Switch]:
        found: Set[Switch] = set()

        for port in self.ports.values():
            if port.dest_switch:
                found.add(port.dest_switch)

        return list(found)

    def __str__(self) -> str:
        return "Switch " + str(self.switch_id) + (" (ROOT)" if self.is_root else "") + ":\n" + "\n".join([str(port) for port in self.ports.values()])
