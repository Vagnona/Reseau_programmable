from ..utils import is_valid_ip

from .equipment import Equipment
from .type import HOST

class Firewall(Equipment):
	""" Classe représentant un firewall
		Attributs:
			p4file: Nom du fichier P4 associé au routeur
	"""

	cksum = None
	json = None

	#region Constructeur

	def __init__(self, name, network):
		""" Crée le firewall à partir de son nom
		"""
		super().__init__(name, network)

	#endregion
		
	# region Méthodes d'instances publique
	
	def start(self):
		""" Démarre le firewall
		"""
		
		# On reset l'état du firewall
		self.get_controller().reset_state()

		# On supprime les règles existantes
		self.get_controller().table_clear("firewall")

		# On ajoute les règles de forwarding
		self.add_forwarding_rules()
	

	def is_valid(self):
		"""Vérifie que le firewall est bien connecté à deux switchs
		"""
		# On vérifie que le firewall est bien connecté à deux switchs, pas plus, pas moins
		if len(self.network.get_switchs_of_equipment(self)) != 2:
			raise Exception(f"{self.name} doit etre connecte a exactement 2 switchs")


	def add_rule(self, ip_src, ip_dst, port_src, port_dst, protocol):
		""" Ajoute une règle au firewall
		"""
		# On check que le port src
		try:
			port_src = int(port_src)
		except ValueError:
			raise Exception(f"Le port source doit etre un entier")
		
		if port_src < 0 or port_src > 65535:
			raise Exception(f"Le port source doit etre compris entre 0 et 65535")

		# On check que le port dst
		try:
			port_dst = int(port_dst)
		except ValueError:
			raise Exception(f"Le port destination doit etre un entier")
	
		if port_dst < 0 or port_dst > 65535:
			raise Exception(f"Le port destination doit etre compris entre 0 et 65535")
		
		# On vérifie que l'ip respecte le format
		if not is_valid_ip(ip_src):
			raise Exception(f"L'ip source {ip_src} n'est pas valide")
		
		if not is_valid_ip(ip_dst):
			raise Exception(f"L'ip destination {ip_dst} n'est pas valide")
		
		# On vérifie que le protocol est bien TCP ou UDP
		if protocol == "TCP" or protocol == "tcp":
			protocol = "6"
		elif protocol == "UDP" or protocol == "udp":
			protocol = "17"
		else:
			raise Exception(f"Le protocole doit etre TCP ou UDP")

		# On ajoute la règle
		self.get_controller().table_add(
			"firewall", "drop",
			[str(ip_src), str(ip_dst), str(protocol), str(port_src), str(port_dst)],["0"]
		)
	

	#endregion

	#region Méthodes d'instances privées

	def add_forwarding_rules(self):
		""" Ajoute les règles de forwarding au firewall
		"""
		# On récupère les switchs connectés au firewall
		switchs = self.network.get_switchs_of_equipment(self)
		
		# On récupère les ports qui connectent le firewall aux switchs
		port1 = self.network.get_port_num_node_to_node(self, switchs[0])
		port2 = self.network.get_port_num_node_to_node(self, switchs[1])

		mac1 = self.network.get_mac_node_to_node(self, switchs[0])
		mac2 = self.network.get_mac_node_to_node(self, switchs[1])

		# table_add repeater forward 2 => 1 MAC
		self.get_controller().table_add(
			"repeater", "forward",
			[str(port1)],
			[str(port2), str(mac1)]
		)

		self.get_controller().table_add(
			"repeater", "forward",
			[str(port2)],
			[str(port1), str(mac2)]
		)


	def see_filters(self):
		""" Affiche le nombre de paquets dropés par le firewall
		"""
		#On récupère le compteur
		drop = self.get_controller().counter_read("nombre_paquets_dropped", 1)

		print(f"{self.name} a droppe {drop} paquets")


	def see_load(self):
		""" Affiche le nombre de paquets recus 
		"""
		#On récupère le compteur
		drop = self.get_controller().counter_read("nombre_paquets_total", 0)

		print(f"{self.name} a recu {drop} paquets")


	#endregion
		
	#region getters/setters
		
	def get_cksum(self):
		return Firewall.cksum
	

	def set_cksum(self, cksum):
		Firewall.cksum = cksum

	
	def get_json_out(self):
		""" Renvoie le json de l'équipement
		"""
		return Firewall.json
	

	def set_json_out(self, json):
		Firewall.json = json

	#endregion