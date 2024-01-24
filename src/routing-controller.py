from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI

import sys
import networkx as nx

class RoutingController(object):
    def __init__(self):
        self.topo = load_topo('topology.json')
        self.controllers = {}

        if len(sys.argv) != 3:
            print("Usage: python script.py [Node list] [Edge list]")
            sys.exit(1)

        self.node_list = eval(sys.argv[1])
        self.edge_list = eval(sys.argv[2])

        self.shortest_paths = {}
        self.logic_graph = nx.Graph()
        
        self.init()

    def init(self):
        self.connect_to_switches()
        self.reset_states()
        self.set_table_defaults()
        self.set_graph()
        self.shortest_path()

    #Reset le controller
    def reset_states(self):
        [controller.reset_state() for controller in self.controllers.values()]

    def connect_to_switches(self):
        for p4switch in self.topo.get_p4switches():
            thrift_port = self.topo.get_thrift_port(p4switch)
            self.controllers[p4switch] = SimpleSwitchThriftAPI(thrift_port)

    def set_table_defaults(self):
        for controller in self.controllers.values():
            controller.table_set_default("ipv4_lpm", "drop", [])
            controller.table_set_default("ecmp_group_to_nhop", "drop", [])

    #Met en place le graph
    def set_graph(self):
        self.logic_graph.clear()
        self.logic_graph.add_nodes_from(self.node_list)
        self.logic_graph.add_edges_from(self.edge_list)
        

    def shortest_path(self):
        G = self.logic_graph

        shortest_paths = {}

        # Parcours de chaque nœud dans le graphe
        for node in G.nodes():
            # Calcul des plus courts chemins depuis le nœud actuel vers tous les autres nœuds
            paths = nx.shortest_path(G, source=node)

            # Ajout des chemins à shortest_paths
            shortest_paths[node] = paths

        self.shortest_paths = shortest_paths

    def route(self):
        switch_ecmp_groups = {sw_name:{} for sw_name in self.topo.get_p4switches().keys()}

        for sw_name, controller in self.controllers.items():
            if sw_name not in self.node_list:
                continue

            for sw_dst in self.topo.get_p4switches():
                if sw_dst not in self.node_list:
                    continue

                #if its ourselves we create direct connections
                if sw_name == sw_dst:
                    for host in self.topo.get_hosts_connected_to(sw_name):
                        if host not in self.node_list:
                            continue

                        sw_port = self.topo.node_to_node_port_num(sw_name, host)
                        host_ip = self.topo.get_host_ip(host) + "/32"
                        host_mac = self.topo.get_host_mac(host)

                        #add rule
                        print("table_add at {}:".format(sw_name))
                        self.controllers[sw_name].table_add("ipv4_lpm", "set_nhop", [str(host_ip)], [str(host_mac), str(sw_port)])

                #check if there are directly connected hosts
                else:
                    if self.topo.get_hosts_connected_to(sw_dst):

                        #paths = self.topo.get_shortest_paths_between_nodes(sw_name, sw_dst)
                        paths = self.shortest_paths[sw_name][sw_dst]

                        for host in self.topo.get_hosts_connected_to(sw_dst):

                            if host not in self.node_list:
                                continue

                            if len(paths) == 1:
                                next_hop = paths[0][1]
                                host_ip = self.topo.get_host_ip(host) + "/24"
                                sw_port = self.topo.node_to_node_port_num(sw_name, next_hop)
                                dst_sw_mac = self.topo.node_to_node_mac(next_hop, sw_name)

                                #add rule
                                print("table_add at {}:".format(sw_name))
                                self.controllers[sw_name].table_add("ipv4_lpm", "set_nhop", [str(host_ip)],
                                                                    [str(dst_sw_mac), str(sw_port)])

                            elif len(paths) > 1:
                                next_hops = [x[1] for x in paths]
                                dst_macs_ports = [(self.topo.node_to_node_mac(next_hop, sw_name),
                                                   self.topo.node_to_node_port_num(sw_name, next_hop))
                                                  for next_hop in next_hops]
                                host_ip = self.topo.get_host_ip(host) + "/24"

                                #check if the ecmp group already exists. The ecmp group is defined by the number of next
                                #ports used, thus we can use dst_macs_ports as key
                                if switch_ecmp_groups[sw_name].get(tuple(dst_macs_ports), None):
                                    ecmp_group_id = switch_ecmp_groups[sw_name].get(tuple(dst_macs_ports), None)
                                    print("table_add at {}:".format(sw_name))
                                    self.controllers[sw_name].table_add("ipv4_lpm", "ecmp_group", [str(host_ip)],
                                                                        [str(ecmp_group_id), str(len(dst_macs_ports))])

                                #new ecmp group for this switch
                                else:
                                    new_ecmp_group_id = len(switch_ecmp_groups[sw_name]) + 1
                                    switch_ecmp_groups[sw_name][tuple(dst_macs_ports)] = new_ecmp_group_id

                                    #add group
                                    for i, (mac, port) in enumerate(dst_macs_ports):
                                        print("table_add at {}:".format(sw_name))
                                        self.controllers[sw_name].table_add("ecmp_group_to_nhop", "set_nhop",
                                                                            [str(new_ecmp_group_id), str(i)],
                                                                            [str(mac), str(port)])

                                    #add forwarding rule
                                    print("table_add at {}:".format(sw_name))
                                    self.controllers[sw_name].table_add("ipv4_lpm", "ecmp_group", [str(host_ip)],
                                                                        [str(new_ecmp_group_id), str(len(dst_macs_ports))])

    def main(self):
        self.route()


if __name__ == "__main__":
    controller = RoutingController().main()
