""" fonctions utiles en tout genre
"""
import os
import yaml


def file_exists(file):
	""" Teste si un fichier existe """
	if not os.path.isfile(file):
		raise Exception(f"Le fichier {file} n'existe pas")


def file_is_yaml(file):
	""" Teste si un fichier est un fichier yaml """
	if not file.endswith(".yaml") and not file.endswith(".yml"):
		raise Exception(f"Le fichier {file} n'est pas un fichier yaml")


def parse_yaml(file):
	""" Parse un fichier yaml
	Retourne un dictionnaire yaml
	"""
	with open(file, 'r') as stream:
		try:
			y = yaml.safe_load(stream)
		except yaml.YAMLError as exc:
			raise Exception(f"Erreur lors du parsing de {file} : {exc}")

	return y


def is_in_dict(key, dict):
	""" Teste si une clé est dans un dictionnaire
	"""
	if not key in dict:
		raise Exception(f"Le champ {key} n'est pas defini")


def is_list(liste):
	""" Teste si un objet est une liste
	"""
	if not isinstance(liste, list):
		raise Exception(f"Le champ {liste} n'est pas une liste")
	

def get_cksum(file):
	""" Renvoie le checksum d'un fichier
	"""
	return os.popen(f"cksum {file}").read().split()[0]


def create_if_not_exists(path):
	""" Crée un dossier s'il n'existe pas
	"""
	if not os.path.exists(path):
		os.makedirs(path)

def to_size(text, size):
	""" Ajout des espaces au début et à la fin d'un texte pour qu'il fasse une certaine taille
	"""
	if len(text) > size:
		return text
	else:
		l = len(text)/2
		return " "*int(size/2-l) + text + " "*int(size/2-l)
	

def is_valid_ip(ip):
	""" Vérifie que l'ip est valide
	"""
	try:
		ip = ip.split(".")
		if len(ip) != 4:
			return False
		for i in ip:
			if int(i) < 0 or int(i) > 255:
				return False
	except:
		return False
	return True