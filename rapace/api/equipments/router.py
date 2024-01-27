from .equipment import Equipment
from .type import HOST

class Router(Equipment):
	""" Classe représentant un routeur
		Attributs:
			p4file: Nom du fichier P4 associé au routeur
	"""

	cksum = None
	json = None

	#region Constructeur

	def __init__(self, name, network):
		""" Crée le routeur à partir de son nom
		"""
		super().__init__(name, network)

	#endregion
		
	#region getters/setters
		
	def get_cksum(self):
		return Router.cksum
	

	def set_cksum(self, cksum):
		Router.cksum = cksum

	
	def get_json_out(self):
		""" Renvoie le json de l'équipement
		"""
		return Router.json
	

	def set_json_out(self, json):
		Router.json = json

	
	def get_routing_table(self):
		""" Renvoie la table de routage de l'équipement
		"""
		return self.get_controller().get_routing_table(self.name)

	#endregion

	# region Méthodes d'instances publiques
	
	def start(self):
		""" Démarre le routeur
		"""
		#TODO: ranger !
		node = self.name
		self.topology = self.network.get_topology()

		for sw_dst in [h.name for h in self.network.get_equipments()]:
			#if its ourselves we create direct connections
			if node == sw_dst:
					for host in self.topology.get_hosts_connected_to(node):
							if host not in [h.name for h in self.network.get_equipments()]:
									continue                    

							sw_port = self.topology.node_to_node_port_num(node, host)
							host_ip = self.topology.get_host_ip(host) + "/32"
							host_mac = self.topology.get_host_mac(host)

							#add rule
							print("table_add at {}:".format(node))
							self.get_controller().table_add("ipv4_lpm", "set_nhop", [str(host_ip)], [str(host_mac), str(sw_port)])

			#check if there are directly connected hosts
			else:
					if self.topology.get_hosts_connected_to(sw_dst):

							paths = self.network.getshortest_path(self.network.get_equipment_by_name(node),self.network.get_equipment_by_name(sw_dst))

							for host in self.topology.get_hosts_connected_to(sw_dst):
									if host not in [h.name for h in self.network.get_equipments()]:
											continue

									print("len(paths) == 1")
									next_hop = paths[0][1].name
									host_ip = self.topology.get_host_ip(host) + "/24"
									sw_port = self.topology.node_to_node_port_num(node, next_hop)
									dst_sw_mac = self.topology.node_to_node_mac(next_hop, node)

									#add rule
									print("table_add at {}:".format(node))
									self.get_controller().table_add("ipv4_lpm", "set_nhop", [str(host_ip)],
																											[str(dst_sw_mac), str(sw_port)])