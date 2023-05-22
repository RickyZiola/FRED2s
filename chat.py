from scapy.all import sniff, Packet, IP, UDP, Raw, TCP
import uuid
import zlib
import cryptography
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
        if tcp_layer.dport == 25565 or tcp_layer.sport == 25565 and packet[IP].src == "127.0.0.1":
            payload = raw_layer.load
            parser = PayloadParser(payload)
            try:
                size = parser.readVarInt()
                packet_id = parser.readVarInt()
                
                #print(size, len(payload))
                data = parser.payload[parser.current:]
                data_parser = PayloadParser(data)
                if packet_id == 0x35:
                    print(data_parser.readVarInt())
            except Exception as e:
                print(e)
            
# Start sniffing packets on the Ethernet interface
sniff(filter='tcp port 25565', prn=packet_callback)
