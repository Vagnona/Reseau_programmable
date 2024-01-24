# example_swap.py
Fichier exemple, qui a utiliser pour changer le type de switch. 
Penser à regarder le module [topologie](https://nsg-ethz.github.io/p4-utils/p4utils.utils.topology.html)

## Idée faire fonctionner le projet 
```bash
#Pour lancer le réseau
sudo python network.py
##Sur un autre terminal
sudo topo.py <Liste des noeud actif> <Liste des liens à uttiliser> 

#Sur un autre terminal (Pour changer de type d'équipement)
sudo python swap.py
```
