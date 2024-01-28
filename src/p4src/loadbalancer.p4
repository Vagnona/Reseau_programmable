/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#include "include/headers.p4"
#include "include/parsers.p4"

const bit<8> PORT_IN = 1;
const bit<8> NOMBRE_PORTS_OUT = 2;

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


	register<bit<32>>(2048) nombre_paquets_total;

	direct_meter<bit<32>>(MeterType.packets) meter1;
	direct_meter<bit<32>>(MeterType.packets) meter2;

	action drop() {
        	mark_to_drop(standard_metadata);
	}

    	action meter_action() {
		if (standard_metadata.egress_spec == 2) {
	        	meter1.read(meta.meter_tag);
		}
		else {
			meter2.read(meta.meter_tag);
		}
	}

    	table meter1_read {
        	key = {
	            standard_metadata.egress_spec: exact;
        	}
	        actions = {
        	    meter_action;
	            NoAction;
        	}
	        default_action = NoAction;
        	meters = meter1;
		meters = meter2;
	        size = 16384;
    	}

	table meter2_read {
	    key = {
	            standard_metadata.egress_spec: exact;
	    }
	    actions = {
        	meter_action;
	        NoAction;
	    }
	    default_action = NoAction;
	    meters = meter2;
	    size = 16384;
	}

    	table meter_filter {
        	key = {
	            meta.meter_tag: exact;
        	}
	        actions = {
        	    drop;
	            NoAction;
        	}
	        default_action = drop;
        	size = 16;
	}

	/* choisi un port OUT */
	action balance() {
		/* permet que le port soit aleatoire et en meme temps qu'il reste le meme pour le quintuplet (@src, @dst, protocol, srcPort, dstPort) */
		standard_metadata.egress_spec = (hdr.ipv4.srcAddr + hdr.ipv4.dstAddr + hdr.tcp.srcPort + hdr.tcp.dstPort + hdr.ipv4.protocol) % NOMBRE_PORTS_OUT;
		/* egress_spec vaut 1 ou 2, les ports OUT sont les ports 2 et 3 donc il faut ajouter +2 */
		
		/* l'indexation des ports commence a 1, d'ou le 1er +1. De plus le port 1 est le port IN, d'ou le 2eme +1 */
		standard_metadata.egress_spec = standard_metadata.egress_spec + 1 + 1;
	}

	apply {
		/* augmente le compteur du nombre de paquets total */
                bit<32> temp;
                nombre_paquets_dropped.read(temp, 32);
                temp = temp + 1;
                nombre_paquets_dropped.write(temp, 32);


	/* Si le paquet vient du port IN, on le forward vers un des ports OUT
	   et on le filtre si il ne respecte pas la rate-limite imposee par l'utilisateur */
	if (standard_metadata.ingress_port == PORT_IN) {
		/* forward vers un port OUT */
		balance();

		/* filtre en fonction de la rate-limite */
	        if (standard_metadata.egress_spec == 2) {
			meter1_read.apply();
		}
		else {
			meter2_read.apply();
		}
		meter_filter.apply();
	}
	/* Si le paquet vient d'un port OUT, on le forward vers le port IN */
	else {
		standard_metadata.egress_spec = PORT_IN;
	}	
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
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

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {

    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

//switch architecture
V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
