from socket import *
from util import *

class Sender:
  def __init__(self):
        """ 
        Your constructor should not expect any argument passed in,
        as an object will be initialized as follows:
        sender = Sender()
        
        Please check the main.py for a reference of how your function will be called.
        """
        self.seqence_num = 0
        self.receiver_ip = '127.0.0.1'
        self.receiver_port = 10009
        self.sender_port = 10008
        self.packet_counter = 1
        self.ack_num = 0
        self.timeout = 3

  def rdt_send(self, app_msg_str):
      """realibly send a message to the receiver (MUST-HAVE DO-NOT-CHANGE)

      Args:
        app_msg_str: the message string (to be put in the data field of the packet)

      """
      #open socket
      sock = socket(AF_INET, SOCK_DGRAM)
      sock.bind(('localhost', self.sender_port))

      #create message packet to send
      msg_packet = make_packet(app_msg_str, self.ack_num, self.seqence_num)
      print(f"original message string: {app_msg_str}")
      print(f"packet created: {msg_packet}")

      while True:
        #set timeout for 3 sec
        sock.settimeout(self.timeout)

        #send message packet to receiver
        sock.sendto(msg_packet, (self.receiver_ip, self.receiver_port))

        #increment packet number and print it
        print(f"packet num. {self.packet_counter} is successfully sent to receiver.")
        self.packet_counter += 1

        # in case of timeout error use exception handling using try and catch
        try:
              #receive message packet from sender
              response, _ = sock.recvfrom(2048)

        except TimeoutError:
              print("socket timeout! Resend!\n")
              print('[timeout retransmission]: ',app_msg_str)
              print(f"packet num.{self.packet_counter} is successfully sent to receiver.")
        
              #retransmit message packet to receiver
              sock.sendto(msg_packet, (self.receiver_ip, self.receiver_port))

              #increment packet number after retransmission
              self.packet_counter += 1         
              response, _ = sock.recvfrom(2048)
            
        #print(int.from_bytes(response))
        response_length = int.from_bytes(response[10:12])

        #get sequence num by geeting last bit using bitwise and with 1
        seq = response_length & 1

        #get ack num by getting second last bit using right shift by 1 and then bitwise and with 1
        ack = (response_length >> 1) & 1

        #print("seq:", seq, "sequence_num: ",self.seqence_num,"ack_num:",self.ack_num,"ack:", ack,"verify_checksum: ",verify_checksum(response))

        #in case of valid checksum and sequence num is equal to acknowledgement number
        if verify_checksum(response) and self.seqence_num == ack:
          print(f"packet is received correctly: seq. num {self.seqence_num} = ACK num {ack}. all done!\n")
          #self.packet_counter += 1
          self.seqence_num = 1 - self.seqence_num
          break
        else:
          #retransmit the packet and acknowledge the last transmitted packet in case of invalid checksum or invalid acknowledgement
          print(f"receiver acked the previous pkt, resend!\n")
          print(f'[ACK-Previous retransmission]: {app_msg_str}')
          print(f"packet num. {self.packet_counter} is successfully sent to receiver.")

          self.packet_counter += 1
          sock.sendto(msg_packet, (self.receiver_ip, self.receiver_port))
          #receive message packet from sender
          response, addr = sock.recvfrom(2048)

          print(f"packet is received correctly: seq. num {self.seqence_num} = ACK num {ack}. all done!\n")

          #update sequence number to 0 if previous sequence num is 1 and 1 if previous sequence num is 0
          self.seqence_num = 1 - self.seqence_num
          break

  ####### Your Sender class in sender.py MUST have the rdt_send(app_msg_str)  #######
  ####### function, which will be called by an application to                 #######
  ####### send a message. DO NOT change the function name.                    #######                    
  ####### You can have other functions if needed.                             #######   