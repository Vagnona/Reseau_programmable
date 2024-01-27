from p4utils.mininetlib.network_API import NetworkAPI
from p4utils.utils.helper import load_topo

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

		# On crée un lien entre chaque équipement et son hôte
		for e in self.equipments:
			if e.type != HOST:
				self.links.append((e, self.get_host_of_equipment(e)))


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


	def get_host_of_equipment(self, equipment):
		""" Renvoie l'hôte d'un équipement
		"""
		for e in self.equipments:
			if e.name == equipment.name + '_host':
				return e
		return None


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
	#endregion

	#region Méthodes d'instances publiques

	def start(self):
		""" Démarre le réseau physique, puis upload les programmes P4 sur les switchs
		"""
		
		# On démarre le réseau physique
		self.start_physical_network()

		# On upload les programmes P4 sur les switchs
		self.push_p4_programs()		


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
			self.net.addLink(e.name, self.get_host_of_equipment(e).name)

		# On crée une clique entre les switchs
		for switch in self.net.switches():
			for switch2 in [s for s in self.net.switches() if s != switch]:
				# Si le lien inverse n'existe pas déjà
				if (switch2, switch) not in self.net.links():
					self.net.addLink(switch, switch2)

		# On démarre le réseau
		self.net.l2()
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