from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI

import sys
import networkx as nx

from equipement.router import Router

class Topology(object):

    def __init__(self):
        self.topo = load_topo('topology.json')
        self.controllers = {}

        self.node_list = []
        self.equipements = []
        self.fnodes(sys.argv[1:],len(sys.argv[1:]))

        self.edge_list = self.fedges(sys.argv[1:],len(sys.argv[1:]))

        self.shortest_paths = {}
        self.logic_graph = nx.Graph()
        
        self.init()

    def init(self):
        self.connect_to_switches()
        self.reset_states()
        self.set_table_defaults()
        self.set_graph()
        self.shortest_path()

    def getnode_list(self):
        return self.node_list
    
    def get_hosts_connected_to(self, node):
        return self.topo.get_hosts_connected_to(node)

    def get_host_ip(self, host):
        return self.topo.get_host_ip(host)

    def getcontrollers(self):
        return self.controllers

    def node_to_node_port_num(self, node, next_hop):
        return self.topo.node_to_node_port_num(node, next_hop)

    def node_to_node_mac(self, next_hop, node):
        return self.topo.node_to_node_mac(next_hop, node)

    def get_host_mac(self, host):
        return self.topo.get_host_mac(host)

    #Recupere les noeuds en argument pour les mettre sous forme de liste
    def fnodes(self, l_arg, taille):
        nodes = []

        for i in range(0,taille):
            if l_arg[i] == '-n':
                index = i + 1
                break

        for arg in l_arg[index:]:
            if arg == '-e':
                break
            arg.split
            nodes.append(arg)
        
        for i in range(len(nodes)):
            if i % 2 == 0:
                self.node_list.append(nodes[i])
            else:
                self.equipements.append(nodes[i])

    #Recupere les liens en argument pour les mettre sous forme de liste
    def fedges(self,l_arg,taille):
        edges = []
        index = 0
        for i in range(0,taille):
            if l_arg[i] == '-e':
                index = i + 1
                break

        for arg in l_arg[index:]:
            if arg == '-n':
                break
            edges.append(tuple(arg.split()))
        return edges

    #Reset le controller
    def reset_states(self):
        [controller.reset_state() for controller in self.controllers.values()]


    def connect_to_switches(self):
        for p4switch in self.topo.get_p4switches():
            thrift_port = self.topo.get_thrift_port(p4switch)
            self.controllers[p4switch] = SimpleSwitchThriftAPI(thrift_port)

    #Met regles par defaut en place.
    def set_table_defaults(self):
        for controller in self.controllers.values():
            controller.table_set_default("ipv4_lpm", "drop", [])
            #controller.table_set_default("ecmp_group_to_nhop", "drop", [])

    #Met en place le graph
    def set_graph(self):
        self.logic_graph.clear()
        self.logic_graph.add_nodes_from(self.node_list)
        self.logic_graph.add_edges_from(self.edge_list)

    #Retourne le chemin le plus court de sw_name à sw_dst
    def getshortest_path(self, sw_name, sw_dst):
        paths = []
        paths.append(tuple(self.shortest_paths[sw_name][sw_dst]))
        return paths

    #Calcule tout les plus courts chemins de tous les noeuds du graph
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

    def main(self):        
        for i in range(len(self.equipements)):
            if self.equipements[i] == '1':
                Router(self, self.node_list[i])
            
                


if __name__ == "__main__":
    controller = Topology().main()
