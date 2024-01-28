"""Fonctions relatives aux commandes
"""
from rapace.prompt import *
from rapace.api import see_topology, change_weight, delete_link, append_link

def execute_command(command):
	""" Execute une commande
	Renvoie si on doit quitter le prompt
	"""

	if command == "quit" or command == "exit":
		return True
	
	elif command == "help":
		help()

	elif command.startswith("swap"):
		# On récupère les arguments
		args = command.split(" ")
		if len(args) != 3:
			log(ERROR, "Usage: swap <node> <equipment>")
			return False
		node_id = args[1]
		equipment = args[2]

		swap(node_id, equipment)

	elif command == "see topology":
		see_topology()

	elif command.startswith("change_weight"):
		# On récupère les arguments
		args = command.split(" ")
		if len(args) != 4:
			log(ERROR, "Usage: change_weight <equipment1> <equipment2> <weight>")
			return False
		equipment1 = args[1]
		equipment2 = args[2]
		weight = args[3]

		set_weight(equipment1, equipment2, weight)

	elif command.startswith("remove link"):
		# On récupère les arguments
		args = command.split(" ")
		if len(args) != 4:
			log(ERROR, "Usage: remove link <equipment1> <equipment2>")
			return False
		equipment1 = args[2]
		equipment2 = args[3]

		del_link(equipment1, equipment2)

	elif command.startswith("add link"):
		# On récupère les arguments
		args = command.split(" ")
		if len(args) != 4:
			log(ERROR, "Usage: add link <equipment1> <equipment2>")
			return False
		equipment1 = args[2]
		equipment2 = args[3]

		add_link(equipment1, equipment2)
	
	else:
		log(ERROR, f"Commande inconnue : {command}")

	return False


def help():
	""" Affiche l'aide
	"""
	log(ERROR, "Commande help non implémentée")


def swap(node_id, equipment):
	"""Remplace l'équipement tournant actuellement sur le switch node_id par equipment.
	"""
	log(ERROR, "Commande swap non implémentée")


def set_weight(equipment1, equipment2, weight):
	""" Change le poids d'un lien
	"""
	try:
		change_weight(equipment1, equipment2, weight)
	except Exception as e:
		log(ERROR, e.args[0])
		return
	
def del_link(equipment1, equipment2):
	""" Supprime un lien
	"""
	try:
		delete_link(equipment1, equipment2)
	except Exception as e:
		log(ERROR, e.args[0])
		return
	
def add_link(equipment1, equipment2):
	""" Ajoute un lien
	"""
	try:
		append_link(equipment1, equipment2)
	except Exception as e:
		log(ERROR, e.args[0])
		return
	
