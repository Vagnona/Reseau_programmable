from p4utils.mininetlib.network_API import NetworkAPI
from p4utils.utils.helper import load_topo

import networkx as nx

from .equipments.type import *
from .equipments.equipment import Equipment
from .constants import *
from .utils import create_if_not_exists, to_size

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
				[
					self.get_equipment_by_name(l[0]),
		 			self.get_equipment_by_name(l[1]),
					int(MAX_WEIGHT/2)
				]
			)

		# On crée un lien entre chaque équipement et ses hôtes
		for e in self.equipments:
			if e.type != HOST:
				for h in [h for h in self.equipments if h.name == f"{e.name}_host"]:
					self.links.append([e, h, 512])

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

		self.check_valid_network()

		# On démarre les équipements
		for e in self.get_equipments():
			e.start()


	def stop(self):
		""" Stoppe le réseau
		"""
		self.net.net.stop()


	def change_weight(self, equipment1, equipment2, weight):
		""" Change le poids d'un lien
		Recalcule la topologie logique
		Réinstalle les règles de routage
		"""
		#On cherhce l'équipement 1 et 2
		e1 = self.get_equipment_by_name(equipment1)
		e2 = self.get_equipment_by_name(equipment2)
		
		# On vérifie que weight est un entier
		try:
			weight = int(weight)
		except:
			raise Exception("Le poids doit etre un entier")

		# On vérifie que le poids est valide
		if weight < 0 or weight > MAX_WEIGHT:
			raise Exception(f"Le poids doit etre compris entre 0 et {MAX_WEIGHT}")
		
		# On vériie que les équipements sont bien connectés
		if e1 not in self.get_adjacent_nodes(e2):
			raise Exception(f"Les equipements {e1} et {e2} ne sont pas connectes")

		# On change le poids du lien
		for l in self.links:
			if (l[0] == e1 and l[1] == e2) or (l[0] == e2 and l[1] == e1):
				l[2] = weight
		
		# On recalcule la topologie logique
		self.compute_logic_graph()

		# On réinstalle les règles de routage
		for e in self.get_equipments(ROUTER):
			e.start()


	def del_link(self, equipment1, equipment2):
		""" Supprime un lien
		"""
		e1 = self.get_equipment_by_name(equipment1)
		e2 = self.get_equipment_by_name(equipment2)

		# On supprime le lien
		link = [l for l in self.links if (l[0] == e1 and l[1] == e2) or (l[0] == e2 and l[1] == e1)][0]
		self.links = [l for l in self.links if l != link]

		# On recalcul la topologie logique
		self.compute_logic_graph()

		# On vérifie que le graphe est toujours valide
		try:
			self.check_valid_network()
		except Exception as e:
			# Si le graphe n'est pas valide, on remet le lien
			self.links.append(link)
			raise e

		# On réinstalle les règles de routage
		for e in self.get_equipments(ROUTER):
			e.start()


	def add_link(self, equipment1, equipment2):
		""" Ajoute un lien
		"""
		e1 = self.get_equipment_by_name(equipment1)
		e2 = self.get_equipment_by_name(equipment2)

		# On vérifie que les équipements ne sont pas déjà connectés
		if e1 in self.get_adjacent_nodes(e2):
			raise Exception(f"Les equipements {e1} et {e2} sont deja connectes")
		
		# On ajoute le lien
		self.links.append([e1, e2, 512])

		# On recalcul la topologie logique
		self.compute_logic_graph()

		# On réinstalle les règles de routage
		for e in self.get_equipments(ROUTER):
			e.start()

	def add_fw_rule(self, fw, ip_src, ip_dst, port_src, port_dst, protocol):
		""" Ajoute une règle au firewall
		"""
		# On récupère le firewall
		fw = self.get_equipment_by_name(fw)

		# On vérifie que le firewall est bien un firewall
		if fw.type != FIREWALL:
			raise Exception(f"{fw.name} n'est pas un firewall")

		# On ajoute la règle
		fw.add_rule(ip_src, ip_dst, port_src, port_dst, protocol)

	
	def see_filters(self):
		""" Affiche les règles du firewall
		"""
		# On récupère les firewalls
		firewalls = self.get_equipments(FIREWALL)

		# On affiche le nombre de paquet filtrés par chaque firewall
		for fw in firewalls:
			fw.see_filters()

	def see_load(self):
		""" Affiche le nombre de paquets recus 
		"""
		# On récupère les switchs
		switchs = self.get_switchs()

		# On affiche le nombre de paquet filtrés par chaque equipement
		for sw in switchs:
			sw.see_load()

	def sw(self, sw_id, equipment):
		""" Swap l'équipement sur un switch
		"""

		if equipment not in EQUIPMENT_TYPES:
			raise Exception(f"Type d'équipement {equipment} inconnu")
		
		# On get le switch
		switch_old = self.get_equipment_by_name(sw_id)


		# On ajoute le nouvel équipement
		switch_new = Equipment.new_equipment(sw_id, EQUIPMENT_TYPES[equipment], self)
		
		# On le remplce dans la liste des équipements
		self.equipments = [e for e in self.equipments if e.name != sw_id]
		self.equipments.append(switch_new)

		# On modifie les liens
		for l in self.links:
			if l[0] == switch_old:
				l[0] = switch_new
			elif l[1] == switch_old:
				l[1] = switch_new

		# On recalcule la topologie logique
		self.compute_logic_graph()

		# On vériie que le graphe est toujours valide
		try:
			self.check_valid_network()
		except Exception as e:
			# Si le graphe n'est pas valide, on remet le lien
			self.equipments = [e for e in self.equipments if e.name != sw_id]
			self.equipments.append(switch_old)
			for l in self.links:
				if l[0] == switch_new:
					l[0] = switch_old
				elif l[1] == switch_new:
					l[1] = switch_old
			raise e

		print(switch_new)
		print(self)

		# On réinstalle les règles de routage
		for e in self.get_equipments(ROUTER):
			e.start()
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
		self.logic_graph.add_weighted_edges_from(self.get_links_not_host())

		# On calcule les chemins les plus courts entre les switchs
		self.shortest_paths = {}
		for n in self.logic_graph.nodes():
			self.shortest_paths[n] = nx.shortest_path(self.logic_graph, source=n)


	def check_valid_network(self):
		""" Vérifie si le réseau est valide
		- Connexe
		- Firewall connecté à deux switchs
		"""

		# On vérifie que le graphe est connexe
		if not nx.is_connected(self.logic_graph):
			raise Exception("Le réseau n'est pas connexe")
		
		# On vérifie que chaque firewall est connecté à deux switchs
		for e in self.get_equipments(FIREWALL):
			e.is_valid()

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
		res = [e for e in self.equipments if e.name == name]
		if len(res) == 0:
			raise Exception(f"Equipement {name} introuvable")
		return res[0]


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

	
	def get_switchs_of_equipment(self, equipment):
		""" Renvoie la liste des switchs connectés à un équipement
		"""
		res = [l[1] for l in self.links if l[0] == equipment]
		res += [l[0] for l in self.links if l[1] == equipment]

		# Si on a plus de deux equipements, on supprime les hosts
		if len(res) > 2:
			res = [e for e in res if not e.is_host()]
		return res


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
		s = ''
		# On affiche les équipements
		s += 'Equipments:\n'
		for e in self.get_switchs():
			s += f"  {e}\n"

		# On affiche les liens
		s += '\nLinks:\n'
		for l in self.get_links_not_host():
			s += f"  {l[0]} <---{to_size(str(l[2]), 6)}---> {l[1]}\n"

		# On retire le dernier \n
		return s[:-1]

	#endregion