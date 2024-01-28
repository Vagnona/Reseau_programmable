from .equipment import Equipment

class Host(Equipment):
	""" Classe représentant un host
	"""

	#region Constructeur

	def __init__(self, name, network):
		""" Crée l'hôte à partir de son nom
		"""
		super().__init__(name, network)

	#endregion
		
	#region Méthodes d'instances publiques
	def start(self):
		""" Démarre l'hôte
		"""
		pass

	#endregion

	#region Getters/Setters

	def get_ip(self):
		""" Renvoie l'adresse IP de l'hôte
		"""
		return self.network.get_topology().get_host_ip(self.name)
	

	def get_mac(self):
		""" Renvoie l'adresse MAC de l'hôte
		"""
		return self.network.get_topology().get_host_mac(self.name)
	
	#endregion