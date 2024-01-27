# Projet de réseau programmable

[Lien du git](git@github.com:Vagnona/reseau_programmable.git)
[Documentation p4utils](https://nsg-ethz.github.io/p4-utils/p4utils.html)



## Modifications apportées à la VM
```
Le nouveau fichier node.py rajoute l’option --enable-swap à la cible, pour activer la fonctionnalité
~/p4-tools/p4-utils/p4utils/utils/

le nouveau fichier thrift_API.py corrige un bug mineur de la plateforme.
~/p4-tools/p4-utils/p4utils/mininetlib/node.py
```

## remarque

- example_swap.py est fourni pour vous montrer comment implémenter cette fonctionnalité en python dans le contrôleur.
- Le module __topology__ contient notamment des fonctions qui vous seront utiles (en particulier pour extraire certaines informations comme le numéro de port, les adresses MAC, etc)

## Lancer la vm :

```bash
# Sans partage de dossier
qemu-system-x86_64 -drive file=vm.qcow2,format=qcow2 -m 2048 -boot c -nic user,hostfwd=tcp::8888-:22 --nographic

# Avec partage de dossier
qemu-system-x86_64 -drive file=vm.qcow2,format=qcow2 -m 2048 -boot c -nic user,hostfwd=tcp::8888-:22 -virtfs local,path=./rapace,security_model=none,mount_tag=rapace --nographic
```
(rapace /home/p4/rapace 9p _netdev,trans=virtio,version=9p2000.u,msize=104857600 0 0) dans /etc/fstab


Se connecter en ssh (mot de passe : p4) :

```bash
ssh p4@127.0.0.1 -p 8888
```


### À l'intérieur de p4

Pour lancer le réseau :
```bash
sudo p4run
```

Ensuite dans le mininet, pour reboot un switch :
```bash
p4switch_reboot s1
```

Pour se connecter à un host
```bash
mx h1
```