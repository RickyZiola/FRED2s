from scapy.all import IP, UDP, send
import time

# Define the source and destination IP addresses
source_ip = '192.168.0.10'
destination_ip = '157.90.90.171'

# Define the destination port
destination_port = 25565

# Define the packet ID and additional fields
packet_id = 0x05

# Create an IP packet
ip_packet = IP(src=source_ip, dst=destination_ip)

# Create a UDP packet with the destination port
udp_packet = UDP(dport=destination_port)

# Set the packet ID and additional fields
udp_packet.id = packet_id
udp_packet.Message = "test"
udp_packet.Timestamp = time.time()
udp_packet.Salt = 6942069
udp_packet.HasSignature = False
udp_packet.MessageCount = 1

# Combine the IP and UDP packets
packet = ip_packet / udp_packet

# Send the packet
send(packet)
