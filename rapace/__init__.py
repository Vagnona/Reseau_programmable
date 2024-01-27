""" Fonctions de bases du frontend CLI de RAPACE
"""
from rapace.api import start_network, stop_network

def start(fichier_logique):
	""" Démarre le réseau en fonction du fichier de topologie logique
	"""

	# On démarre le réseau
	start_network(fichier_logique)
	try:
		pass
	except Exception as e:
		print(f"ERROR: Erreur lors du demarrage du reseau : {e}")
		stop()
		exit(1)
	

def stop():
	""" Stoppe le réseau
	"""

	# On stoppe le réseau
	stop_network()