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

	counter(1, CounterType.packets_and_bytes) nombre_paquets;

	direct_meter<bit<32>>(MeterType.packets) meter;

	action drop() {
        	mark_to_drop(standard_metadata);
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

	action balance(bit<32> nombre_ports_out, bit<32> num_port_in){
		standard_metadata.egress_spec = (hdr.ipv4.srcAddr + hdr.ipv4.dstAddr + hdr.tcp.srcPort + hdr.tcp.dstPort + hdr.ipv4.protocol) % nombre_ports_out + 1;
		if (standard_metadata.egress_spec >= num_port_in) {
			standard_metadata.egress_spec = standard_metadata.egress_spec + 1;
		}
	}

	action forward_vers_in(macAddr_t dstAddr, egressSpec_t port_in) {
		standard_metadata.egress_spec = port_in;
		hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
		hdr.ethernet.dstAddr = dstAddr;
	}

	action forward_vers_out(macAddr_t dstAddr) {
		hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
		hdr.ethernet.dstAddr = dstAddr;
		meter.read(meta.meter_tag);
	}
		
	table post_balance {
		key = {
			standard_metadata.egress_spec: exact;
		}
		actions = {
			NoAction;
			forward_vers_out;
		}	
		size = 4096;
		meters = meter;
	}

	table forward {
		key = {
			standard_metadata.ingress_port: exact;
		}
		actions = {
			balance;
			forward_vers_in;
			NoAction;
		}
		default_action = NoAction;
		size = 4096;
	}

	/* choisi un port OUT */
	}

	apply {

		switch (forward.apply().action_run) {
			balance: {
				post_balance.apply();
				meter_filter.apply();
			}
		}
	
	        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
		nombre_paquets.count((bit<32>)0);
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
