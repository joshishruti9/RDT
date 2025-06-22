from socket import *
from time import sleep
from util import *
## No other imports allowed

receiver_ip = '127.0.0.1'
receiver_port = 10009

sender_ip = '127.0.0.1'
sender_port = 10008

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind((receiver_ip, receiver_port))

expected_seq = 0
packet_counter = 1

previous_response = b''


while True:
    #get data from sender
    data, addr = sock.recvfrom(2048)

    print(f'packet num.{packet_counter} received: {data}')

    #extract data length field and get sequence number and payload 
    data_length = int.from_bytes(data[10:12])
        
    #get sequence number by getting right bit
    seq = data_length & 1

    #get payload
    payload = data[12:].decode()

    if not verify_checksum(data) or seq != expected_seq:
        print("Invalid Checksum!!")
        
    #in case of valid sequence number and checksum
    if verify_checksum(data) and seq == expected_seq:
        #simulate packet loss by adding sleep
        if packet_counter % 6 == 0:
            print(f"simulating packet loss: sleep while to trigger timeout event on the send side...")
            sleep(3)

        #simulate corruption of packet
        elif packet_counter % 3 == 0:
            print(f"simulating packet bit error/corrupted: ACK the previous packet!")
            #in case of corruption send previous response again
            sock.sendto(previous_response.encode(),(sender_ip, sender_port))

        #in case of valid packet    
        else:
            print(f'packet is expected, messages string delivered: {payload}')
            print(f'packet is delivered, now creating and sending the ACK packet...')

            #send packet with sequence number and ack num
            packet_msg = make_packet(payload, seq, seq)
            sock.sendto(packet_msg,(sender_ip, sender_port))

            #store successful response in case of next corrupted packet
            previous_response = f'packet is expected, messages string delivered: {payload}'

            #update sequence number to 0 if previous sequence num is 1 and 1 if previous sequence num is 0
            expected_seq = 1 - expected_seq

        print(f'all done for this packet!\n')

        #increase packet number
        packet_counter += 1   