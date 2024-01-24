""" Décrit le réseau "physique" utilisé par mininet.
C'est un réseau en clique de 8 équipements et 8 hotes.
Chaque hote est connecté à un équipement.
"""

from p4utils.mininetlib.network_API import NetworkAPI

net = NetworkAPI()

# Network general options
net.setLogLevel('info')

# On place 8 équipements et 8 hotes
net.addP4Switch('s0')
net.addP4Switch('s1')
net.addP4Switch('s2')
net.addP4Switch('s3')
net.addP4Switch('s4')
net.addP4Switch('s5')
net.addP4Switch('s6')
net.addP4Switch('s7')

net.addHost('h0')
net.addHost('h1')
net.addHost('h2')
net.addHost('h3')
net.addHost('h4')
net.addHost('h5')
net.addHost('h6')
net.addHost('h7')

# On connecte les équipements entre eux en clique
# Et un hote par équipement
net.addLink('s0', 's1')
net.addLink('s0', 's2')
net.addLink('s0', 's3')
net.addLink('s0', 's4')
net.addLink('s0', 's5')
net.addLink('s0', 's6')
net.addLink('s0', 's7')
net.addLink('s1', 's2')
net.addLink('s1', 's3')
net.addLink('s1', 's4')
net.addLink('s1', 's5')
net.addLink('s1', 's6')
net.addLink('s1', 's7')
net.addLink('s2', 's3')
net.addLink('s2', 's4')
net.addLink('s2', 's5')
net.addLink('s2', 's6')
net.addLink('s2', 's7')
net.addLink('s3', 's4')
net.addLink('s3', 's5')
net.addLink('s3', 's6')
net.addLink('s3', 's7')
net.addLink('s4', 's5')
net.addLink('s4', 's6')
net.addLink('s4', 's7')
net.addLink('s5', 's6')
net.addLink('s5', 's7')
net.addLink('s6', 's7')

net.addLink('s0', 'h0')
net.addLink('s1', 'h1')
net.addLink('s2', 'h2')
net.addLink('s3', 'h3')
net.addLink('s4', 'h4')
net.addLink('s5', 'h5')
net.addLink('s6', 'h6')
net.addLink('s7', 'h7')

#net.setP4SourceAll('p4src/ecmp.p4')
net.setP4SourceAll('repeater_without_table.p4')


# Assignment strategy
net.l2()

# Nodes general options
net.enablePcapDumpAll()
net.enableLogAll()
net.enableCli()
net.startNetwork()
