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

	register<bit<32>>(2048) nombre_paquets_dropped;
	register<bit<32>>(2048) nombre_paquets_total;

    action forward(bit<9> egress_port){
        standard_metadata.egress_spec = egress_port;
    }

	action drop(bit<32> t) {
		bit<32> temp;
		nombre_paquets_dropped.read(temp, 32);
		temp = temp + 1;
		nombre_paquets_dropped.write(temp, 32);
		mark_to_drop(standard_metadata);
	}

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

	table firewall {
		key = {
			standard_metadata.ingress_port: exact;
			standard_metadata.egress_spec: exact;
			hdr.ipv4.srcAddr: exact;
			hdr.ipv4.dstAddr: exact;
/*			hdr.ipv4.protocol: exact;*/
		}
		actions = {
			drop;
			NoAction;
		}
		size = 256;
		default_action = NoAction;
	}

    apply {
	bit<32> temp;
	nombre_paquets_total.read(temp, 32);
	temp = temp + 1;
	nombre_paquets_total.write(temp, 32);

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
