/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

#include "include/headers.p4"
#include "include/parser.p4"

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

	counter(1, CounterType.packets_and_bytes) nombre_paquets_total;
	counter(1, CounterType.packets_and_bytes) nombre_paquets_dropped;

    action forward(spec_t egress_port, macAddr_t dstAddr){
        standard_metadata.egress_spec = egress_port;
	hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
	hdr.ethernet.dstAddr = dstAddr;
    }

	/* augmente le compteur du nombre de paquets dropped ET drop le paquet courant */
	action drop(bit<32> t) {
		nombre_paquets_dropped.count((bit<32>)0);
		mark_to_drop(standard_metadata);
	}

	/* forward le paquet */
    table repeater {
        key = {
            standard_metadata.ingress_port: exact;
        }
        actions = {
            forward;
            NoAction;
        }
        size = 2;
        default_action = NoAction;
    }

	/* si le paquet correspond à un quintuplet (IP source, IP dst, protocole, port source, port destination)
	 * alors on le drop
	 */
	table firewall {
		key = {
			hdr.ipv4.srcAddr: exact;
			hdr.ipv4.dstAddr: exact;
			hdr.ipv4.protocol: exact;

			/* somme des 2 car un seul est utilisé, l'autre est nul */
			hdr.tcp.srcPort + hdr.udp.srcPort: exact @name("src port number");
			hdr.tcp.dstPort + hdr.tcp.dstPort: exact @name("dst port number");
		}
		actions = {
			drop;
			NoAction;
		}
		size = 256;
		default_action = NoAction;
	}

    apply {

	/* augmente le nombre de paquets total */
	nombre_paquets_total.count((bit<32>)0);

	/* forwarding + filtrage */
	switch (repeater.apply().action_run) {
		forward: {
			firewall.apply();
		}
	}
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
    apply { }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
