"""Fonctions relatives au prompt
"""

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'

PROMPT = "rapace> "

INFO = "[INFO] "
WARNING = "[WARNING] "
ERROR = "[ERROR] "

def log(level, message):
	"""Affiche un message de log
	"""

	if level == INFO:
		print_color(BLUE, level)
	elif level == WARNING:
		print_color(YELLOW, level)
	elif level == ERROR:
		print_color(RED, level)

	print(message)

def print_color(color, message):
	"""Affiche un message en couleur
	"""
	print(f"{color}{message}\033[0m", end='')