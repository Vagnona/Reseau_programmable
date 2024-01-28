""" Module api pour RAPACE
Ici est renseigné tout les endpoints de l'api rapace
"""
from rapace.api.utils import file_exists, file_is_yaml
from rapace.api.parser import check_yaml
from rapace.api.network import Network

network = None # Représente tout le réseau : les équipements et les liens entre eux

def parse_topology(topology_file):
	""" Vérifie la validité du fichier de topologie logique
	Retourne le dictionnaire yaml du fichier
	Renvoie une exception si le fichier n'est pas valide
	"""

	# On vérifie que le fichier est valide
	file_exists(topology_file)

	# On vérifie que le fichier est un fichier yaml
	file_is_yaml(topology_file)

	# On check la validité du fichier yaml
	topo = check_yaml(topology_file)

	return topo


def start_network(topology_file):
	""" Démarre le réseau en fonction du fichier de topologie logique
	"""
	global network

	# On parse le fichier de topologie logique
	equipement, links = parse_topology(topology_file)

	network = Network(equipement, links)

	network.start()
	

def stop_network():
	""" Stoppe le réseau
	"""
	global network
	
	network.stop()


def see_topology():
	""" Affiche la topologie
	"""
	global network

	print(network)
	

def change_weight(equipement1, equipement2, weight):
	""" Change le poids d'un lien
	"""
	global network

	network.change_weight(equipement1, equipement2, weight)


def delete_link(equipement1, equipement2):
	""" Supprime un lien
	"""
	global network

	network.del_link(equipement1, equipement2)


def append_link(equipement1, equipement2):
	""" Ajoute un lien
	"""
	global network

	network.add_link(equipement1, equipement2)