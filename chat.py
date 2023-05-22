from scapy.all import sniff, Packet, IP, UDP, Raw
import uuid
import zlib
from payload_parser import PayloadParser
from mcproto.buffer import Buffer
from mcproto.packets.interactions import sync_read_packet
from mcproto.protocol.base_io import BaseSyncReader

def packet_callback(packet: Packet):
    # Check if packet is a Minecraft packet (assuming TCP)
    if packet.haslayer('TCP') and packet.haslayer('Raw'):
        tcp_layer = packet.getlayer('TCP')
        raw_layer = packet.getlayer('Raw')
        # Check if packet is sent to or from Minecraft server (port 25565)
        if tcp_layer.dport == 25565 or tcp_layer.sport == 25565:
            payload = raw_layer.load
            parser = PayloadParser(payload)
            try:
                packet_id = parser.readVarLong()
            except ValueError as e:
                print("".join([chr(c) for c in payload]))
                raise e
            if packet_id == 0x35:
                print(payload)
                #print(zlib.decompress(payload))
                print(packet_id)

# Start sniffing packets on the Ethernet interface
sniff(iface='Ethernet', filter='tcp port 25565', prn=packet_callback)
