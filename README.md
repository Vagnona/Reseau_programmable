# Projet de réseau programmable

[Lien du git](git@github.com:Vagnona/reseau_programmable.git)
[Documentation p4utils](https://nsg-ethz.github.io/p4-utils/p4utils.html)



## Modification apporté 
```
Le nouveau fichier node.py rajoute l’option --enable-swap à la cible, pour activer la fonctionnalité
~/p4-tools/p4-utils/p4utils/utils/

le nouveau fichier thrift_API.py corrige un bug mineur de la plateforme.
~/p4-tools/p4-utils/p4utils/mininetlib/node.py
```

## remarque

- example_swap.py est fourni pour vous montrer comment implémenter cette fonctionnalité en python dans le contrôleur.
- Le module __topology__ contient notamment des fonctions qui vous seront utiles (en particulier pour extraire certaines informations comme le numéro de port, les adresses MAC, etc)

