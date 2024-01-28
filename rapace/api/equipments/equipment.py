from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.compiler import * 

from .type import HOST, ROUTER, EQUIPMENT_TYPE, FIREWALL, LOAD_BALANCER
from ..constants import P4SRC, WORKING_DIR
from ..utils import get_cksum

class Equipment():
	""" Classe représentant chaque équipement du réseau
	Classe abstraite, ne peut pas être instanciée directement

	Attributs:
		name: Nom de l'équipement
		type: Type de l'équipement (HOST, ROUTER, LOAD_BALANCER, FIREWALL)
		file: Nom du fichier P4 associé à l'équipement
		cksum: Checksum du fichier P4 associé à l'équipement
	"""

	#region Méthodes statiques

	def new_equipment(name, type, network):
		""" Crée un nouvel équipement à partir de son nom et de son type
		"""
		from .host import Host
		from .router import Router
		from .firewall import Firewall

		if type == HOST:
			return Host(name, network)
		elif type == ROUTER:
			return Router(name, network)
		elif type == FIREWALL:
			return Firewall(name, network)
		elif type == LOAD_BALANCER:
			return LoadBalancer(name, network)
		else:
			raise Exception(f"Unknown equipment type {type}")

	#endregion
	
	#region Constructeur

	def __init__(self, name, network):
		""" Crée l'équipement à partir de son nom
		"""
		from .host import Host
		from .router import Router
		from .firewall import Firewall

		self.name = name
		if isinstance(self, Host):
			self.type = HOST
		elif isinstance(self, Router):
			self.type = ROUTER
		elif isinstance(self, Firewall):
			self.type = FIREWALL
		elif isinstance(self, LoadBalancer):
			self.type = LOAD_BALANCER
		

		
		self.network = network

	#endregion

	#region Méthodes d'instances publiques

	def start(self):
		""" Démarre l'équipement, à implémenter dans les classes filles
		"""
		raise NotImplementedError("start() method not implemented")


	def push_p4_program(self):
		""" Push le programme P4 sur l'équipement
		"""
		if self.type == HOST:
			raise Exception("Hosts don't have a P4 program")
		
		# On compile le programme P4
		self.compile_p4_program()

		# On swap les configurations
		self.swap_configs()


	#endregion

	#region Méthodes d'instances privées
		
	def compile_p4_program(self):
		""" Compile le programme P4 de l'équipement
		Retourne le nom du fichier JSON généré
		"""
		if self.type == HOST:
			raise Exception("Hosts don't have a P4 program")

		source = P4C(self.get_p4file(), outdir=WORKING_DIR)

		# On compile uniquement si le fichier P4 a changé
		if self.source_has_changed():
			source.compile()
			self.set_json_out(source.get_json_out())

		return self.get_json_out()


	def swap_configs(self):
		""" Swap les configurations de l'équipement
		"""
		api = self.get_controller()
		api.load_new_config_file(self.get_json_out())
		api.swap_configs()
		api.switch_info.load_json_config(api.client)
		api.table_entries_match_to_handle = api.create_match_to_handle_dict()
		api.load_table_entries_match_to_handle()


	def source_has_changed(self):
		""" Renvoie True si le fichier P4 a changé, False sinon
		"""
		if self.type == HOST:
			raise Exception("Hosts don't have a P4 program")

		# On récupère le checksum du fichier P4
		new_cksum = get_cksum(self.get_p4file())

		# On compare avec le checksum précédent
		if new_cksum != self.get_cksum():
			self.set_cksum(new_cksum)
			return True
		
		return False

		
	#endregion

	#region getters/setters
			
	def is_host(self):
		""" Renvoie True si l'équipement est un host, False sinon
		"""
		return self.type == HOST
	
			
	def get_p4file(self):
		""" Renvoie le nom du fichier P4 associé à l'équipement
		"""
		if self.type == HOST:
			raise Exception("Hosts don't have a P4 file")
		
		return f"{P4SRC}{EQUIPMENT_TYPE[self.type][2]}"
	

	def get_thrift_port(self):
		""" Renvoie le port thrift de l'équipement
		"""
		return self.network.get_topology().get_thrift_port(self.name)
	

	def get_controller(self):
		""" Renvoie le controlleur de l'équipement
		"""
		return SimpleSwitchThriftAPI(self.get_thrift_port())	
	

	#endregion

	#region Méthodes spéciales
	
	def __str__(self):
		""" Renvoie le nom et le type de l'équipement
		"""
		return f"{self.name} ({EQUIPMENT_TYPE[self.type][1]})"
	
	#endregion