from .equipment import Equipment

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

	#endregion
