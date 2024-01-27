HOST = 0
ROUTER = 1
LOAD_BALANCER = 2
FIREWALL = 3

EQUIPMENT_TYPE = (
		(HOST, 'host', 'no_p4file'),
		(ROUTER, 'router', 'router.p4'),
		(LOAD_BALANCER, 'load_balancer', 'load_balancer.p4'),
		(FIREWALL, 'firewall', 'firewall.p4')
	)

# On crée un dictionnaire pour pouvoir retrouver le type d'équipement à partir de son nom
EQUIPMENT_TYPES = {e[1]: e[0] for e in EQUIPMENT_TYPE}


def get_equipment_type_name(equipment_type):
	""" Renvoie le nom de l'équipement à partir de son type
	"""
	return EQUIPMENT_TYPE[equipment_type][1]