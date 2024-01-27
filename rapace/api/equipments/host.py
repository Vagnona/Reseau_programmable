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