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
		
	# region Méthodes d'instances publiques
	
	def start(self):
		""" Démarre le routeur
		"""
		# On reset l'état du routeur
		self.get_controller().reset_state()

		# On ajoute les règles de routage
		self.add_routing_rules()


	def add_routing_rules(self):
		""" Ajoute les règles de routage
		"""

		# On supprime toutes les règles de routage
		self.get_controller().table_clear("ipv4_lpm")
		
		# On ajoute la règle de routage par défaut
		self.get_controller().table_set_default("ipv4_lpm", "drop", [])

		# Pour chaque switch
		for sw_dst in self.network.get_switchs():

		
			# Pour chaque hote connecté au switch
			for h in self.network.get_hosts_of_equipment(sw_dst):

				# On détermine le prochain saut pour rejoindre le switch
				if self == sw_dst:
					next_hop = h
				else:
					next_hop = self.network.get_shortest_path(self,sw_dst)[0][1]

				# On ajoute la règle de routage
				self.add_routing_rule(next_hop,h)

	
	def add_routing_rule(self, next_hop, h):
		"""Ajoute une règle de routage pour rejoindre un hôte
		"""

		ip = h.get_ip()
		port = self.network.get_port_num_node_to_node(self, next_hop)


		# Si c'est une connexion directe
		if next_hop == h:
			# On rajoute le /32
			ip += "/32"
			mac = h.get_mac()
		else:
			# On rajoute le /24
			ip += "/24"
			mac = self.network.get_mac_node_to_node(self, next_hop)

		# On ajoute la règle de routage
		self.get_controller().table_add(
			"ipv4_lpm", "set_nhop",
			[str(ip)],[str(mac), str(port)]
		)

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
