""" Fonction relatives au parsage du yaml de topologie logique
Rappel de la structure du fichier yaml:
switchs:
	- name: <nom du switch>
	  equipement: <type d'equipement>
	...
links:
	- [<nom du switch>, <nom du switch>]
	...
"""

from rapace.api.utils import parse_yaml, is_in_dict, is_list

def check_yaml(logic_file):
	""" Checke la validité du fichier yaml de topologie logique
	"""

	# On ouvre le fichier yaml
	topology = parse_yaml(logic_file)

	# On check le champ "switchs"
	check_topology_switchs(topology)

	# On check le champ "links"
	check_topology_links(topology)

	return topology["switchs"], topology["links"]

def check_topology_switchs(topology):
	""" Checke la validité du champ "switchs" du fichier yaml de topologie logique
	"""

	# On vérifie que le champ "switchs" existe
	is_in_dict("switchs", topology)

	for switch in topology["switchs"]:
		# On vérifie que chaque switch a deux champs "name" et "equipement"
		is_in_dict("name", switch)
		is_in_dict("type", switch)

		# On vérifie que chaque switch a un type d'equipement valide	# On vérifie que chaque switch a un type d'equipement valide
		for switch in topology["switchs"]:
			if switch["type"] != "firewall" and switch["type"] != "router":
				raise Exception(f"Le switch {switch['name']} a un type d'equipement invalide")
			
		if switch["type"] == "load_balancer":
			in_port = switch.get("in_port", None)
			if in_port is None:
				raise Exception(f"Le switch {switch['name']} doit avoir un champ \"in_port\"")

			# On ajoute le champ "in_port" à la topologie
			switch["in_port"] = in_port

	
	
	# On vérifie que chaque switch a un nom unique
	switchs_name = [s["name"] for s in topology["switchs"]]
	for switch in topology["switchs"]:
		if switchs_name.count(switch["name"]) > 1:
			raise Exception(f"Le switch {switch['name']} est defini plusieurs fois")
		
	return topology
	
def check_topology_links(topology):
	""" Checke la validité du champ "links" du fichier yaml de topologie logique
	"""
	# On vérifie que le champ "links" existe
	is_in_dict("links", topology)

	switchs_name = [s["name"] for s in topology["switchs"]]

	for link in topology["links"]:
		# On vérifie que chaque champ "links" est une liste
		is_list(link)

		# On vérifie que chaque champ "links" contient deux switchs
		if len(link) != 2:
			raise Exception("Un champ \"links\" ne contient pas deux switchs")

		# On vérifie que chaque champ "links" contient deux switchs existants
		for switch in topology["switchs"]:
			if not switch["name"] in switchs_name:
				raise Exception(f"Le switch {switch['name']} est defini dans un champ \"links\" mais n'est pas defini dans \"switchs\"")
		
		# On vérifie que chaque champ "links" contient deux switchs différents
		for link in topology["links"]:
			if link[0] == link[1]:
				raise Exception("Un champ \"links\" contient deux fois le même switch")
			
	return topology