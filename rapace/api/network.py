from p4utils.mininetlib.network_API import NetworkAPI
from p4utils.utils.helper import load_topo

import networkx as nx

from .equipments.type import *
from .equipments.equipment import Equipment
from .constants import *
from .utils import create_if_not_exists

class Network:
	"""Classe représentant le réseau
	Contient la liste des équipements du réseau et les liens entre eux

	Attributs:
		equipments: Liste des équipements du réseau : [ equipement1, equipement2 ]
		links: Liste des liens entre les équipements : [ (equipement1, equipement2), ... ]

	Méthodes publiques:
		start: Démarre le réseau
		stop: Stoppe le réseau
	"""

	#region Constructeur

	def __init__(self, equipments, links):
		""" Crée le réseau à partir de la liste d'équipements et de leurs liens
		"""

		# On crée les équipements
		self.equipments = []
		for e in equipments:
			# On crée l'équipement et l'hôte associé
			s = Equipment.new_equipment(e['name'], EQUIPMENT_TYPES[e['type']], self)
			s_host = Equipment.new_equipment(f"{e['name']}_host", HOST, self)

			# On ajoute l'équipement et l'hôte à la liste des équipements
			self.equipments.append(s)
			self.equipments.append(s_host)


		# On crée les liens
		self.links = []
		for l in links:
			self.links.append(
				(
					self.get_equipment_by_name(l[0]),
		 			self.get_equipment_by_name(l[1])
				)
			)

		# On crée un lien entre chaque équipement et ses hôtes
		for e in self.equipments:
			if e.type != HOST:
				for h in [h for h in self.equipments if h.name == f"{e.name}_host"]:
					self.links.append((e, h))

		# On crée la topologie logique
		self.logic_graph = nx.Graph()

	#endregion
				
	#region Méthodes d'instances publiques

	def start(self):
		""" Démarre le réseau physique, puis upload les programmes P4 sur les switchs
		"""
		
		# On démarre le réseau physique
		self.start_physical_network()

		# On upload les programmes P4 sur les switchs
		self.push_p4_programs()
	
		# On calcule la topologie logique
		self.compute_logic_graph()

		# On démarre les équipements
		for e in self.get_equipments():
			e.start()


	def stop(self):
		""" Stoppe le réseau
		"""
		self.net.net.stop()

	#endregion
				
	#region Méthodes d'instances privées

	def start_physical_network(self):
		""" Démarre le réseau physique
		"""
		create_if_not_exists(WORKING_DIR)

		self.net = NetworkAPI()
		self.net.setLogLevel('info')
			
		# On crée les hôtes
		for h in self.get_equipments(HOST):
			self.net.addHost(h.name)

		# On crée les X switchs et leurs hosts
		for e in self.get_switchs():
			self.net.addP4Switch(e.name)
			for h in [h for h in self.equipments if h.name == f"{e.name}_host"]:
				self.net.addLink(e.name, h.name)

		# On crée une clique entre les switchs
		for switch in self.net.switches():
			for switch2 in [s for s in self.net.switches() if s != switch]:
				# Si le lien inverse n'existe pas déjà
				if (switch2, switch) not in self.net.links():
					self.net.addLink(switch, switch2)

		# On démarre le réseau
		self.net.l3()
		self.net.enablePcapDumpAll(self.get_pcap_path())
		self.net.enableLogAll(self.get_log_path())
		self.net.setTopologyFile(self.get_topology_path())
		self.net.disableCli()
		self.net.startNetwork()
					
	
	def push_p4_programs(self):
		""" Upload les programmes P4 sur les switchs
		"""
		# On upload les programmes P4 sur les switchs
		for e in self.get_switchs():
			e.push_p4_program()


	def compute_logic_graph(self):
		""" Calcule la topologie logique du réseau ET les chemins les plus courts entre les switchs
		"""

		self.logic_graph.clear()
		self.logic_graph.add_nodes_from(self.get_switchs())
		self.logic_graph.add_edges_from(self.get_links_not_host())

		# On calcule les chemins les plus courts entre les switchs
		self.shortest_paths = {}
		for n in self.logic_graph.nodes():
			self.shortest_paths[n] = nx.shortest_path(self.logic_graph, source=n)


	#endregion
		
	#region Getters/Setters
			
	def get_equipments(self, type=None):
		""" Renvoie la liste des équipements
		"""
		if type is None:
			return self.equipments
		else:
			return [e for e in self.equipments if e.type == type]
		

	def get_switchs(self):
		""" Renvoie la liste des équipements qui ne sont pas des hôtes
		"""
		return [e for e in self.equipments if not e.is_host()]
	

	def get_equipment_by_name(self, name):
		""" Renvoie l'équipement à partir de son nom
		"""
		for e in self.equipments:
			if e.name == name:
				return e
		return None


	def get_hosts_of_equipment(self, equipment):
		""" Renvoie les hôtes associés à un équipement
		"""
		hosts = self.get_topology().get_hosts_connected_to(equipment.name)
		return [self.get_equipment_by_name(h) for h in hosts]


	def get_links(self):
		""" Renvoie la liste des liens
		"""
		return self.links
	

	def get_links_from_equipment(self, equipment):
		""" Renvoie la liste des liens d'un équipement
		"""
		return [l for l in self.links if l[0] == equipment or l[1] == equipment]


	def get_links_not_host(self):
		""" Renvoie la liste des liens qui ne sont pas des liens d'hôtes
		"""
		return [l for l in self.links if not (l[0].is_host() or l[1].is_host())]

	
	def get_pcap_path(self):
		""" Renvoie le chemin des fichiers pcap
		"""
		return WORKING_DIR + 'pcap/'
	

	def get_log_path(self):
		""" Renvoie le chemin des fichiers log
		"""
		return WORKING_DIR + 'log/'
	

	def get_topology_path(self):
		""" Renvoie le chemin du fichier de topologie
		"""
		return WORKING_DIR + 'topology.json'


	def get_topology(self):
		""" Renvoie la topologie du réseau
		"""
		return load_topo(self.get_topology_path())
	

	def get_adjacent_nodes(self, node):
		""" Renvoie les noeuds adjacents à un noeud
		"""
		# On regarde si il existe un lien entre le noeud et un autre noeud
		adjacent_nodes = []
		for l in self.get_links():
			if l[0] == node:
				adjacent_nodes.append(l[1])
			elif l[1] == node:
				adjacent_nodes.append(l[0])
		
		return adjacent_nodes
	

	def get_adjacent_switchs(self, node):
		""" Renvoie les switchs adjacents à un noeud
		"""
		return [n for n in self.get_adjacent_nodes(node) if not n.is_host()]
	

	def get_adjacent_hosts(self, node):
		""" Renvoie les hôtes adjacents à un noeud
		"""
		return [n for n in self.get_adjacent_nodes(node) if n.is_host()]
	

	def get_shortest_path(self, sw_name, sw_dst):
		""" Renvoie le plus court chemin entre deux switchs
		"""
		paths = []
		paths.append(tuple(self.shortest_paths[sw_name][sw_dst]))
		return paths


	def get_port_num_node_to_node(self, n1, n2):
		""" Renvoie le numéro de port entre deux noeuds
		"""
		return self.get_topology().node_to_node_port_num(n1.name, n2.name)
	

	def get_mac_node_to_node(self, n1, n2):
		""" Renvoie l'adresse MAC entre deux noeuds
		"""
		return self.get_topology().node_to_node_mac(n1.name, n2.name)

	#endregion

	#region Méthodes spéciales

	def __str__(self):
		""" Affiche le réseau
		"""
		s = '==== Network: ====\n'

		# On affiche les équipements
		s += 'Equipments:\n'
		for e in self.get_switchs():
			s += f"  {e}\n"

		# On affiche les liens
		s += '\nLinks:\n'
		for l in self.get_links_not_host():
			s += f"  {l[0]} <-> {l[1]}\n"
		return s
	

	#endregion