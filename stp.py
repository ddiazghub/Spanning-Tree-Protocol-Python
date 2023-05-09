from __future__ import annotations
import json
from typing import Dict, List, Set, Generator
from switch import Switch

class STPNetwork:
    switches: Dict[int, Switch]
    root_bridge: Switch

    def __init__(self) -> None:
        self.switches = dict()
    
    def add_switch(self, switch: Switch) -> None:
        self.switches[switch.switch_id] = switch

        if switch.is_root:
            self.root_bridge = switch

    def bfs(self) -> Generator[Switch, None, None]:
        visited: Set[Switch] = set()
        queue: List[Switch] = [self.root_bridge]

        while len(queue) > 0:
            switch = queue.pop(0)

            if switch not in visited:
                visited.add(switch)
                yield switch

                for neighbor in switch.neighbors():
                    if neighbor not in visited:
                        queue.append(neighbor)

    def run_stp(self):
        for switch in self.bfs():
            if switch is not self.root_bridge:
                switch.find_root_port()

        print("\n".join([str(switch) for switch in self.switches.values()]))
        
    def from_json(file: str) -> STPNetwork:
        with open(file) as json_file:
            network = STPNetwork()
            data = json.load(json_file)

            for sw in data["switches"]:
                switch = Switch(sw["id"], True if sw.get("root", None) else False)
                network.add_switch(switch)

                for port in sw["ports"]:
                    switch.add_port(port["id"])
            
            for link in data["links"]:
                switch_ids = tuple(link["switches"])
                port_ids = tuple(link["ports"])
                port1 = network.switches[switch_ids[0]].ports[port_ids[0]]
                port2 = network.switches[switch_ids[1]].ports[port_ids[1]]
                port1.link(port2)

            return network

if __name__ == "__main__":
    network = STPNetwork.from_json("network.json")
    network.run_stp()