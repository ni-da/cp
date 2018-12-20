import socket, sys


def bits2string(b):
    res = int(b, 2)
    if 0 <= res <= 32:
        return "."
    return chr(res)


def get_bin_query(raw_data):
    a = raw_data.encode("hex")
    data_bin_lst = []
    scale = 16
    num_of_bits = 8
    counter = 0
    while counter < len(a) - 1:
        if counter % 2 == 0:
            b = a[counter] + a[counter + 1]
            new_bin = bin(int(b, scale))[2:].zfill(num_of_bits)
            data_bin_lst.append(new_bin)
        counter += 1
    return data_bin_lst


def get_trans_id(data_list):
    trans_id = data_list[0], data_list[1]
    return str(int(trans_id[0], 2)) + str(int(trans_id[1], 2))


def get_answers_count(data_list):
    ans_count = data_list[6], data_list[7]
    return str(int(ans_count[0], 2)) + str(int(ans_count[1], 2))


def get_record_type(data_list, starting_index):
    record_type = data_list[int(starting_index)], data_list[int(starting_index) + 1]
    dec_type = str(int(record_type[0], 2)) + str(int(record_type[1], 2))
    if dec_type == "01":
        return "A"
    elif dec_type == "028":
        return "AA"
    elif dec_type == "044":
        return "SSHFP"
    elif dec_type == "012":
        return "PTR"


def get_name(data_list):
    dns_name = ""
    loop_len = (len(data_list))
    for counter in range(13, loop_len):
        i = data_list[counter]
        if bits2string(i) == '.' and bits2string(data_list[counter + 1]) == '.':
            return dns_name, counter + 1
        else:
            dns_name += bits2string(i)
    return dns_name


def handle_request_quries():
    while 1:
        data, addr = s.recvfrom(8192)
        s.sendto("Hello", addr)

        data_bin_list = get_bin_query(data)
        trans_id = get_trans_id(data_bin_list)
        dns_naam, name_counter = get_name(data_bin_list)
        if dns_naam in caches:
            msg_to_send = caches[dns_naam]
        else:
            google_dns_server = ('8.8.8.8', 53)
            udp_request_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_request_socket.sendto(data, google_dns_server)
            dns_answer, dns_addr = udp_request_socket.recvfrom(1024)
            msg_to_send = dns_answer
            # get an anwswer from google DNS -> save to cache
            answer_data_bin_list = get_bin_query(dns_answer)
            ans_count = get_answers_count(answer_data_bin_list)
            ans_name, name_ending_index = get_name(answer_data_bin_list)
            record_type = get_record_type(answer_data_bin_list, int(name_ending_index))
            if ans_count > 0 and ans_name not in caches:  # and record_type == "A"
                if len(caches) == cache_max:
                    oldest_item = item_key_list[0]
                    del caches[oldest_item]
                    del item_key_list[0]
                caches[dns_naam] = dns_answer
                item_key_list.append(dns_naam)
            udp_request_socket.shutdown(1)
            udp_request_socket.close()
        s.sendto(msg_to_send, addr)


if len(sys.argv) > 1:
    cache_max = sys.argv[1]
else:
    cache_max = 500
item_key_list = []
caches = {}
address = "localhost"
port = 53
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((address, port))
handle_request_quries()
