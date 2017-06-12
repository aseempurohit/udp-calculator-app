import socket

RECV_BUFF = 512
SEPARATOR = ':'

#Simulated enumeration function
def enum(**named_values):
    return type('Enum', (), named_values)

#Random string generator
def get_id(str_len = 6):
    import random, string
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(str_len))


class SupportedFunction(object):
    def __init__(self, code, string, handler):
        self.code = code
        self.string = string
        self.handler = handler


class CalculatorPacket():
    def __init__(self, identifier, operation, *args):
        self.id = identifier
        self.code = operation
        self.values = args

    def as_bytes(self):
        packet_string = self.id + \
            SEPARATOR + \
            str(self.code)

        for value in self.values:
            packet_string = packet_string + SEPARATOR + str(value)

        return bytearray(str(packet_string))

    @staticmethod
    def as_string(byte_data):
        return byte_data.decode().split(':')


class CalculatorService(object):

    def __init__(self, server_host, server_port, function_map):
        self.remote_host = server_host
        self.remote_port = server_port
        self.function_map = function_map
        self.local_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    def serve(self):
        self.local_sock.bind((self.remote_host, self.remote_port))
        print('Started serving on {}:{}'.format(self.remote_host, self.remote_port))
        while True:
            request_data, remote = self.local_sock.recvfrom(RECV_BUFF)

            print('Received request buffer:{}'.format(request_data))

            decoded_list = CalculatorPacket.as_string(request_data)
            
            #Get identifiers from request
            identifier = decoded_list[0]
            operation = decoded_list[1]

            #Get function handler
            handler = self.function_map[operation].handler

            #Perform operation
            response_val = handler(*decoded_list[2:])

            #Create response packet
            packet = CalculatorPacket(identifier, operation, response_val)

            #Send response
            print('Sending response buffer:{}'.format(packet.as_bytes()))
            self.local_sock.sendto(packet.as_bytes(), remote)
    def execute(self, *args):
        identifier = get_id()
        packet = CalculatorPacket(identifier, *args)
        
        self.local_sock.sendto(packet.as_bytes(), (self.remote_host, self.remote_port))

        calculated_packet_str, remote = self.local_sock.recvfrom(RECV_BUFF)

        decoded_response_list = CalculatorPacket.as_string(calculated_packet_str)

        if(decoded_response_list[0] == identifier):
            return decoded_response_list[2]
        else:
            return 0

    def terminate(self):
        self.local_sock.close()


def addition(*args):
    result = 0
    for value in args:
        result = result + int(value)

    return result

def subtraction(*args):
    result = int(args[0])
    for value in args[1:]:
        result = result - int(value)

    return result

def multiplication(*args):
    result = int(args[0])
    for value in args[1:]:
        result = result * int(value)

    return result

def division(*args):
    result = int(args[0])
    for value in args[1:]:
        result = result / int(value)

    return result

