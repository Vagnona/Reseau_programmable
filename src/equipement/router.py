

class Router(object):

    def __init__(self, topology, node):
        self.topology = topology
        self.node = node
        self.route()
        
    def route(self):
        node = self.node

        for sw_dst in self.topology.getnode_list():
            #if its ourselves we create direct connections
            if node == sw_dst:
                for host in self.topology.get_hosts_connected_to(node):
                    if host not in self.topology.getnode_list():
                        continue                    

                    sw_port = self.topology.node_to_node_port_num(node, host)
                    host_ip = self.topology.get_host_ip(host) + "/32"
                    host_mac = self.topology.get_host_mac(host)

                    #add rule
                    print("table_add at {}:".format(node))
                    self.topology.getcontrollers()[node].table_add("ipv4_lpm", "set_nhop", [str(host_ip)], [str(host_mac), str(sw_port)])

            #check if there are directly connected hosts
            else:
                if self.topology.get_hosts_connected_to(sw_dst):

                    paths = self.topology.getshortest_path(node,sw_dst)

                    for host in self.topology.get_hosts_connected_to(sw_dst):
                        if host not in self.topology.getnode_list():
                            continue

                        print("len(paths) == 1")
                        next_hop = paths[0][1]
                        host_ip = self.topology.get_host_ip(host) + "/24"
                        sw_port = self.topology.node_to_node_port_num(node, next_hop)
                        dst_sw_mac = self.topology.node_to_node_mac(next_hop, node)

                        #add rule
                        print("table_add at {}:".format(node))
                        self.topology.getcontrollers()[node].table_add("ipv4_lpm", "set_nhop", [str(host_ip)],
                                                            [str(dst_sw_mac), str(sw_port)])