from router2_skeleton import *

def processing_thread(connection, ip, port, forwarding_table_with_range, default_gateway_port,router5=None, router6=None, max_buffer_size=5120):
    # 1. Connect to the appropriate sending ports (based on the network topology diagram).
    # 2. Continuously process incoming packets
    while True:
        # 3. Receive the incoming packet, process it, and store its list representation
        packet = receive_packet(connection, "output/received_by_router_4.txt", max_buffer_size)

        # 4. If the packet is empty (Router 1 has finished sending all packets), break out of the processing loop
        if not packet or packet[0] == "":
            break

        # 5. Store the source IP, destination IP, payload, and TTL.
        sourceIP = packet[0].strip()
        destinationIP = packet[1].strip()
        payload = packet[2].strip()
        ttl = packet[3].strip()

        # 6. Decrement the TTL by 1 and construct a new packet with the new TTL.
        new_ttl = int(ttl) - 1
        new_packet_list = [sourceIP, destinationIP, payload, str(new_ttl)]
        new_packet = ",".join(new_packet_list)

        # 7. Convert the destination IP into an integer for comparison purposes.
        destinationIP_bin = ip_to_bin(destinationIP)
        destinationIP_int = int(destinationIP_bin, 2)

        # 8. Find the appropriate sending port to forward this new packet to.
        send_port = ""
        for row in forwarding_table_with_range:
            firstIP_int = int(ip_to_bin(row[0][0]), 2)
            lastIP_int = int(ip_to_bin(row[0][1]), 2)
            if firstIP_int <= destinationIP_int <= lastIP_int:
                send_port = row[1].strip()
                break

        # 9. If no port is found, then set the sending port to the default port.
        if (send_port == ""):
            send_port = default_gateway_port.strip()

        if (new_ttl == 0 and send_port != '127.0.0.1'):
            print("DISCARD:", new_packet)
            write_to_file("output/discarded_by_router_4.txt", new_packet)
            continue
        # 11. Either
        # (a) send the new packet to the appropriate port (and append it to sent_by_router_2.txt),
        # (b) append the payload to out_router_2.txt without forwarding because this router is the last hop, or
        # (c) append the new packet to discarded_by_router_2.txt and do not forward the new packet

        if send_port == '8005':
            print("sending packet", new_packet, "to Router 5")
            write_to_file("output/sent_by_router_4.txt", new_packet, "5")
            router5.send(new_packet.encode())
        elif send_port == '8006':
            print("sending packet", new_packet, "to Router 6")
            write_to_file("output/sent_by_router_4.txt", new_packet, "6")
            router6.send(new_packet.encode())
        elif send_port == '127.0.0.1':
            print("OUT:", payload)
            write_to_file("output/out_router_4.txt", payload)
        else:
            print("DISCARD:", new_packet)
            write_to_file("output/discarded_by_router_4.txt", new_packet)

router5 = create_socket('127.0.0.1', 8005)
router6 = create_socket('127.0.0.1', 8006)
start_server(8004, "input/router_4_table.csv", processing_thread, router5, router6)
