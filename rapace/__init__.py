""" Fonctions de bases du frontend CLI de RAPACE
"""

from rapace.api import start_network, stop_network
from rapace.prompt import *
from rapace.commands import execute_command

def start(fichier_logique):
	""" Démarre le réseau en fonction du fichier de topologie logique
	"""
	log(INFO, "Demarrage du reseau...")

	# On démarre le réseau
	start_network(fichier_logique)
	log(INFO, "Reseau demarre !")
	

def stop():
	""" Stoppe le réseau
	"""
	print("")
	# On stoppe le réseau
	log(INFO, "Arret du reseau...")
	stop_network()
	log(INFO, "Reseau arrete !")


def prompt():
	""" Boucle principale
	"""


	# On affiche le prompt
	while True:
		print("")
		print_color(GREEN, PROMPT)

		# On récupère la commande
		command = input()
	
		end = execute_command(command)

		if end:
			break


