from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI

class RoutingController(object):

    def __init__(self):

        self.topo = load_topo('topology.json')
        self.controllers = {}
        self.init()

    def init(self):
        self.connect_to_switches()
        self.reset_states()
        self.set_table_defaults()

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

    def route(self):

        # Creer un dictionnaire par clef de chaque switch de la topo. 
        switch_ecmp_groups = {sw_name:{} for sw_name in self.topo.get_p4switches().keys()}

        #Boucle sur les elements de la topologie.
        for sw_name, controller in self.controllers.items():

            # Boucle sur la liste des switchs tout court.
            for sw_dst in self.topo.get_p4switches():

                #if its ourselves we create direct connections
                if sw_name == sw_dst:
                    # Pour les hote directement connecté à sw_name
                    for host in self.topo.get_hosts_connected_to(sw_name):
                        # Recuperation du port sx - host
                        sw_port = self.topo.node_to_node_port_num(sw_name, host)

                        # L'ip
                        host_ip = self.topo.get_host_ip(host) + "/32"

                        # L'addresse MAC
                        host_mac = self.topo.get_host_mac(host)

                        #Ajout de la regle. 
                        print("table_add at {}:".format(sw_name))
                        self.controllers[sw_name].table_add("ipv4_lpm", "set_nhop", [str(host_ip)], [str(host_mac), str(sw_port)])

                #check if there are directly connected hosts
                # Maintenant sw_name et sw_dst sont differents. 
                else:
                    # Si la destination a un host directement co à lui sw_name - sw_dst - host
                    if self.topo.get_hosts_connected_to(sw_dst):

                        # Recupere le plus cours chemin entre sw_name et sw_dst
                        paths = self.topo.get_shortest_paths_between_nodes(sw_name, sw_dst)

                        # Boucle sur les host connecté à sw_dst.
                        for host in self.topo.get_hosts_connected_to(sw_dst):

                            # Si la taille du chemin est 1 
                            if len(paths) == 1:
                                next_hop = paths[0][1]

                                # ip de l'host
                                host_ip = self.topo.get_host_ip(host) + "/24"

                                # port et MAC du next_hop
                                sw_port = self.topo.node_to_node_port_num(sw_name, next_hop)
                                dst_sw_mac = self.topo.node_to_node_mac(next_hop, sw_name)

                                #Ajout de la regle.
                                print("table_add at {}:".format(sw_name))
                                self.controllers[sw_name].table_add("ipv4_lpm", "set_nhop", [str(host_ip)],
                                                                    [str(dst_sw_mac), str(sw_port)])
                                
                            # Si la taille du chemin est superieur à 1.
                            elif len(paths) > 1:
                                # Prend le prochain saut de tout les chamins possible.
                                next_hops = [x[1] for x in paths]

                                # Tableau des mac et port de tous les prochains saut.
                                dst_macs_ports = [(self.topo.node_to_node_mac(next_hop, sw_name),
                                                   self.topo.node_to_node_port_num(sw_name, next_hop))
                                                  for next_hop in next_hops]
                                
                                # Ip de l'hote. 
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
