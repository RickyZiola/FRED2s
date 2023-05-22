from scapy.all import sniff, Packet, IP, UDP, Raw
import uuid
from payload_parser import PayloadParser
import zlib

def int128_to_uuid(int128):
    # Split the 128-bit integer into two 64-bit parts
    upper_part = int128 >> 64
    lower_part = int128 & ((1 << 64) - 1)
    
    # Convert each part to hexadecimal and zero-fill to 16 digits
    upper_hex = format(upper_part, '016x')
    lower_hex = format(lower_part, '016x')
    
    # Combine the parts with hyphens in the appropriate format
    uuid_string = f'{upper_hex[:8]}-{upper_hex[8:12]}-{upper_hex[12:16]}-{lower_hex[:4]}-{lower_hex[4:]}'
    
    return uuid.UUID(uuid_string)

def packet_callback(packet: Packet):
    # Check if packet is a Minecraft packet (assuming TCP)
    if packet.haslayer('TCP') and packet.haslayer('Raw'):
        tcp_layer = packet.getlayer('TCP')
        raw_layer = packet.getlayer('Raw')
        # Check if packet is sent to or from Minecraft server (port 25565)
        if tcp_layer.dport == 25565 or tcp_layer.sport == 25565:
            payload = raw_layer.load

            decoded_packet = IP(src=packet[IP].src, dst=packet[IP].dst) / tcp_layer / payload
            # Process and analyze the decoded packet here
            payload = decoded_packet[Raw].load
            # Check if the payload contains Minecraft chat message
            print("\n".join([bin(c)[2:].rjust(8, "0") for c in payload]))
            parser: PayloadParser = PayloadParser(payload)
            p_id  = parser.readVarInt()
            p_len = parser.readVarInt()
            d_len = parser.readVarInt()
            print()
            if p_id == 0x35:
                print(p_id)
                print(zlib.decompress(payload[p_len - d_len:]))

# Start sniffing packets on the Ethernet interface
sniff(iface='Ethernet', filter='tcp port 25565', prn=packet_callback)
