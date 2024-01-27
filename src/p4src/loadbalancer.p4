/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#include "include/headers.p4"
#include "include/parsers.p4"

const bit<8> PORT_IN = 1;
const bit<8> NOMBRE_OUT = 3;

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

	action balance() {
		standard_metadata.egress_spec = (hdr.ipv4.srcAddr + hdr.ipv4.dstAddr + hdr.tcp.srcPort + hdr.tcp.dstPort + hdr.ipv4.protocol) % NOMBRE_OUT + 1;
		if (standard_metadata.egress_spec == PORT_IN) {
			standard_metadata.egress_spec = standard_metadata.egress_spec + 1;
		}
	}

    apply {
                bit<32> temp;
                nombre_paquets_dropped.read(temp, 32);
                temp = temp + 1;
                nombre_paquets_dropped.write(temp, 32);


	if (standard_metadata.ingress_port == PORT_IN) {
		balance();
	}
	else {
		standard_metadata.egress_spec = PORT_IN;
	}

        switch (dmac.apply().action_run) {
            broadcast: {
                select_mcast_grp.apply();
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
