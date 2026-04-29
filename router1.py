## Router 1 --- acts as client only
from router1_skeleton import *

# Main Program
# 0. Remove any output files in the output directory
# (this just prevents you from having to manually delete the output files before each run).
# I am unsure of whether the output directory should preexist or should our code handle that error possibility, so therefore, I am adding a safeguard

os.makedirs('./output', exist_ok=True)

files = glob.glob('./output/*')
for f in files:
    os.remove(f)

# 1. Connect to the appropriate sending ports (based on the network topology diagram).
#
router2 = create_socket('127.0.0.1', 8002)
router4 = create_socket('127.0.0.1', 8004)

# 2. Read in and store the forwarding table.
forwarding_table = read_csv("input/router_1_table.csv")
# 3. Store the default gateway port.
default_gateway_port = find_default_gateway(forwarding_table)
# 4. Generate a new forwarding table that includes the IP ranges for matching against destination IPS.
forwarding_table_with_range = generate_forwarding_table_with_range(forwarding_table)
# 5. Read in and store the packets.
packets_table = read_csv("input/packets.csv")

# 6. For each packet,
for packet in packets_table:
    # 7. Store the source IP, destination IP, payload, and TTL.
    sourceIP = packet[0].strip()
    destinationIP = packet[1].strip()
    payload = packet[2].strip()
    ttl = int(packet[3].strip())

    # 8. Decrement the TTL by 1 and construct a new packet with the new TTL.
    new_ttl = ttl - 1
    new_packet_list = [sourceIP, destinationIP, payload, str(new_ttl)]
    new_packet = ",".join(new_packet_list)
    
    # 9. Convert the destination IP into an integer for comparison purposes.
    destinationIP_bin = ip_to_bin(destinationIP)
    destinationIP_int = int(destinationIP_bin, 2)

    # 9. Find the appropriate sending port to forward this new packet to.
    send_port = ""
    for row in forwarding_table_with_range:
        firstIP_int = int(ip_to_bin(row[0][0]), 2)
        lastIP_int = int(ip_to_bin(row[0][1]), 2)
        if firstIP_int <= destinationIP_int <= lastIP_int:
            send_port = row[1].strip()
        
    # 10. If no port is found, then set the sending port to the default port.
    if (len(send_port) == 0):
        send_port = default_gateway_port.strip()

    if (new_ttl == 0 and send_port != '127.0.0.1'):
            print("DISCARD:", new_packet)
            write_to_file("output/discarded_by_router_1.txt", new_packet)
            continue
    
    print("PORT: ", send_port)
    # 11. Either
    # (a) send the new packet to the appropriate port (and append it to sent_by_router_1.txt),
    # (b) append the payload to out_router_1.txt without forwarding because this router is the last hop, or
    # (c) append the new packet to discarded_by_router_1.txt and do not forward the new packet
    if send_port == '8002':
        print("sending packet", new_packet, "to Router 2")
        write_to_file("output/sent_by_router_1.txt", new_packet, "2")
        router2.send(new_packet.encode())
    elif send_port == '8004':
        print("sending packet", new_packet, "to Router 4")
        write_to_file("output/sent_by_router_1.txt", new_packet, "4")
        router4.send(new_packet.encode())
    elif send_port == '127.0.0.1':
        print("OUT:", payload)
        write_to_file("output/out_router_1.txt", payload)
    else:
        print("DISCARD:", new_packet)
        write_to_file("output/discarded_by_router_1.txt", new_packet)

    # Sleep for some time before sending the next packet (for debugging purposes)
    time.sleep(1)
