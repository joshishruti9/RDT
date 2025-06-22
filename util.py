def create_checksum(packet_wo_checksum):
    """create the checksum of the packet (MUST-HAVE DO-NOT-CHANGE)

    Args:
      packet_wo_checksum: the packet byte data (including headers except for checksum field)

    Returns:
      the checksum in bytes

    """
    total = 0

    #add padding if length is odd to make it even
    if len(packet_wo_checksum) % 2 != 0: 
      packet_wo_checksum += b'\x00'
    
    #calculate total for whole packet message to calculate checksum
    for i in range(0, len(packet_wo_checksum), 2):
      #combine two bytes into one 16-bit word and add word to make total
      word = (packet_wo_checksum[i] << 8) + packet_wo_checksum[i + 1]
      total += word
      #wrap the total to handle overflow cases
      total = (total & 0xFFFF) + (total >> 16)
    
    #take the 1's complement of the sum
    checksum = ~total & 0xFFFF

    #return checksum in bytes format
    return checksum.to_bytes(2,"big")

def verify_checksum(packet):
    """verify packet checksum (MUST-HAVE DO-NOT-CHANGE)

    Args:
      packet: the whole (including original checksum) packet byte data

    Returns:
      True if the packet checksum is the same as specified in the checksum field
      False otherwise

    """
    #if length of packet is less than 12 return false
    if len(packet) < 12:
      return False
    
    #get checksum from packet
    received_checksum = int.from_bytes(packet[8:10], 'big')

   
    #calculate total for packet
    total = 0

    #add padding if length is odd to make it even
    if len(packet) % 2 != 0: 
      packet += b'\x00'
    
    #calculate total for whole packet message to calculate checksum
    for i in range(0, len(packet), 2):
      #ignore 8 and 9th byte to ignore chesksum of the packet
      if i==8 or i==9:
         continue
      #combine two bytes into one 16-bit word and add word to make total
      word = (packet[i] << 8) + packet[i + 1]
      total += word

      #wrap the total to handle overflow cases
      total = (total & 0xFFFF) + (total >> 16)


    #add received check sum and packet checksum to check if its addition equal to 0xFFFF 
    total_sum = total + received_checksum

    #wrap the total to handle overflow cases
    total_sum = (total_sum & 0xFFFF) + (total_sum >> 16)

    return  total_sum == 0xFFFF

def make_packet(data_str, ack_num, seq_num):
    """Make a packet (MUST-HAVE DO-NOT-CHANGE)

    Args:
      data_str: the string of the data (to be put in the Data area)
      ack: an int tells if this packet is an ACK packet (1: ack, 0: non ack)
      seq_num: an int tells the sequence number, i.e., 0 or 1

    Returns:
      a created packet in bytes

    """

    #8 byte given fixed header value
    header_value = b'COMPNETW'

    #declare header size. 8 byte fixed value, 2 byte checksum, 2 byte length field containing sequence and acknoeledgement number
    header_size = 12

    #encode data to make payload
    data = data_str.encode()

    #calculate total length of the packet
    total_length = header_size + len(data)

    #calculate length field by putting total length as 2 byte ack num as second last bit by shifting it right and sequence num as last num 
    length_field = (total_length << 2) | (ack_num << 1) | seq_num

    #Create packet
    packet = header_value + b'\x00\x00' + length_field.to_bytes(2, 'big') + data
    
    #create checksum value for packet
    checksum = create_checksum(packet)

    #update reserved checksum value fiels in packet
    packet = header_value + checksum + length_field.to_bytes(2, 'big') + data

    #return packet
    return packet

    # make sure your packet follows the required format!


###### These three functions will be automatically tested while grading. ######
###### Hence, your implementation should NOT make any changes to         ######
###### the above function names and args list.                           ######
###### You can have other helper functions if needed.                    ######  
