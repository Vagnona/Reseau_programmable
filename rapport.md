# Rapport du projet **RAPACE**

## Architecture du projet

Le projet est composé de nombreux fichiers, dont l'usage est défini ci-joint :

- `network.py` : Ce fichier décrit la clique utilisée par *mininet*. Dans notre exemple, on a crée une clique de 8 équipements réseaux, comme sur le sujet, mais rien n'empêche de faire fonctionner le projet sur des cliques de taille différentes. Pour simplifier les test on a aussi disposé un hôte par équipement réseau. Là encore, rien n'oblige à faire ainsi, le projet pourrait aussi fonctionner avec plus ou moins d'hôtes sur chaque équipement.