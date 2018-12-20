import struct

struct_dns_name_compression = struct.Struct('!H')
len_dns_name_compression = struct_dns_name_compression.size


def parse_dns_name(data, idx_name_start=0):
    """Parses a domain name label sequence from a received DNS message and 
    converts it into a readable domain name string.
    
    :param data: Received data holding a DNS message.
    :type data: str
    :param idx_name_start: Index in the data buffer where the domain name 
                           starts.
    :type idx_name_start: integer
    :returns : A tuple holding (1) the parsed/readable domain name, 
               (2) the encoded version of the domain name (i.e., as a DNS 
               label sequence), and (3) the number of bytes that were 
               consumed from data.
    :rtype: tuple
    
    In case something goes wrong, an IndexError is raised. The encoded 
    domain name is expected to start at index idx_name_start in the data 
    argument. To be able to cope with DNS message compression, the data 
    argument should encompass the *full* DNS message."""

    name_parsed = ''
    name_label_sequence = ''

    is_pointer = False
    idx = idx_name_start

    while idx < len(data):
        byte = ord(data[idx])
        print(byte)
        # Parsing complete?
        if (byte == 0):
            #            print('(Q)NAME PARSING: Encountered the stop byte (i.e., 00)')
            if not is_pointer:
                name_label_sequence += data[idx]
            break

        # Handle DNS message compression (i.e., a pointer redirect)
        if (byte & 0xC0 == 0xC0):  # two left-most bits equal 1?
            try:
                (offset,) = struct_dns_name_compression.unpack_from(data, idx)
            except struct.error, se:
                print('struct.error occurred while deserializing the byte offset for a compressed (Q)NAME: %s' % (se,))
                raise IndexError('Could not unpack 2-byte pointer offset (DNS message compression)')

            # Trim two left-most bits from the offset
            offset &= 0x3FFF

            # Update label sequence as well as number of bytes read; 
            # only do this upon the first redirect
            if not is_pointer:
                name_label_sequence += data[idx:idx + len_dns_name_compression]

            # Continue (Q)NAME parsing from the specified byte offset
            idx = offset
            is_pointer = True

            #            print('DNS message compression: Parsing (Q)NAME from offset %d' % (offset,))

            continue

        # Parse token length
        len_token = byte

        #        print('(Q)NAME PARSING: Reading a token of length %d' % (len_token,))

        # Read token
        if (idx + len_token < len(data)):
            name_parsed += data[idx + 1:idx + 1 + len_token]
            name_parsed += '.'

            #            print('(Q)NAME PARSING: Read token "%s"' % (data[idx+1:idx+1+len_token],))
            if not is_pointer:
                name_label_sequence += data[idx:idx + 1 + len_token]

        # Advance index
        idx += 1 + len_token

    # Verify parsing success
    if (idx >= len(data)):
        raise IndexError('idx exceeded data size')

    name_parsed = name_parsed[:-1]  # trim trailing "." character

    return (name_parsed, name_label_sequence, len(name_label_sequence))


a = parse_dns_name(
    "\x00\x03\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x06google\x02be\x08uhasselt\x02be\x00\x00\x1c\x00\x01")

print(a)
