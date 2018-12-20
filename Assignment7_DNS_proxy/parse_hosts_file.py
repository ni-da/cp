def parse_hosts_file(file_name):
    """Attempts to parse the specified file_name according to the hosts 
    file syntax (https://en.wikipedia.org/wiki/Hosts_(file)).

    :param file_name: The path/name of the file that must be parsed.
    :type file_name: str
    :returns: A Python dictionary that maps domain names to IP addresses.
    :rtype: dictionary
    
    Each line in the hosts file is expected to specify exactly a single 
    IP address and a single domain name.

    Raises an IOError in case there is an issue with the specified 
    file name (e.g., file does not exist on disk).
    """

    dict_redirect = {}

    with open(file_name, 'r') as f:
        line_num = 1

        for line in f:
            line.strip(' \n\t')

            # Skip comment lines
            if line.startswith('#'):
                line_num = line_num + 1
                continue

            # IP addresses and host names are separated by one or more 
            # whitespaces or tabs
            list_tokens = line.split()

            if len(list_tokens) != 2:
                print('WARNING: Incorrect syntax at line %d of hosts file "%s"' % (line_num, file_name))
            else:
                dict_redirect[list_tokens[1].strip(' \n\t')] = list_tokens[0].strip(' \n\t')

            line_num = line_num + 1

    return dict_redirect
