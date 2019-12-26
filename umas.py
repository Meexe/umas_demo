from random import randint
import socket
import sys

READ_ID = 0x02
TAKE_RESERVATION = 0x10
RELEASE_RESERVATION = 0x11
KEEP_ALIVE = 0x12
OK = 0xFE
ERROR = 0xFD


PROTOCOL_ID = 0x0000
FUNCTION_CODE = 0x5A


class UMASClient(object):

    def __init__(self, owner_id=randint(0, 255), slave_address=0x00):
        self.owner_id = owner_id
        self.transaction_id = 0x0000
        self.slave_address = slave_address

    def encode(self, code, data=None):
        pdu = bytearray()
        pdu.append(FUNCTION_CODE)
        pdu.append(self.owner_id)
        pdu.append(code)
        if data:
            pdu += data

        header = bytearray()
        header += self.transaction_id.to_bytes(2, 'big')
        header += PROTOCOL_ID.to_bytes(2, 'big')
        length = len(pdu) + 1
        header += length.to_bytes(2, 'big')
        header.append(self.slave_address)

        if self.transaction_id <= 0xffff:
            self.transaction_id += 1
        else:
            self.transaction_id = 0
        return header + pdu

    def decode(data):
        pass

    def run_client(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = ('localhost', 10003)
        sock.connect(server_address)

        while True:
            func = input('2 - READ_ID, 16 - TAKE_RESERVATION, 17 - RELEASE_RESERVATION, 18 - KEEP_ALIVE\n')
            try:
                func = int(func)
            except ValueError:
                continue
            
            print('connecting to {} port {}'.format(*server_address))

            message = self.encode(func)
            print('sending {}'.format(message.hex()))
            sock.sendall(message)

            amount_received = 0
            amount_expected = len(message)

            while amount_received < amount_expected:
                data = sock.recv(16)
                amount_received += len(data)
                print('received {}'.format(data.hex()))



class UMASServer(object):

    def __init__(self, owner_id=0x00, slave_address=0x00, plc_id=randint(0, 255)):
        self.owner_id = owner_id
        self.slave_address = slave_address
        self.plc_id = plc_id
        self.functions = {
            READ_ID: self.read_id,
            TAKE_RESERVATION: self.take_reservation,
            RELEASE_RESERVATION: self.release_reservation,
            KEEP_ALIVE: self.keep_alive
        }

    def read_id(self, data):
        pdu = bytearray()
        pdu.append(FUNCTION_CODE)
        pdu.append(self.owner_id)
        pdu.append(OK)
        pdu.append(self.plc_id)

        header = bytearray()
        header += data[:7]
        length = len(pdu) + 1
        header[-3:-1]= length.to_bytes(2, 'big')
        return header + pdu

    def take_reservation(self, data):
        self.owner_id = data[8]

        pdu = bytearray()
        pdu.append(FUNCTION_CODE)
        pdu.append(self.owner_id)
        pdu.append(OK)

        header = bytearray()
        header += data[:7]
        length = len(pdu) + 1
        header[-3:-1]= length.to_bytes(2, 'big')
        return header + pdu

    def release_reservation(self, data):
        self.owner_id = 0x00

        pdu = bytearray()
        pdu.append(FUNCTION_CODE)
        pdu.append(self.owner_id)
        pdu.append(OK)
        pdu.append(self.plc_id)

        header = bytearray()
        header += data[:7]
        length = len(pdu) + 1
        header[-3:-1]= length.to_bytes(2, 'big')
        return header + pdu

    def keep_alive(self, data):
        pdu = bytearray()
        pdu.append(FUNCTION_CODE)
        pdu.append(self.owner_id)
        pdu.append(OK)

        header = bytearray()
        header += data[:7]
        length = len(pdu) + 1
        header[-3:-1]= length.to_bytes(2, 'big')
        return header + pdu

    def respond(self, data):
        func_code = data[9]
        func = self.functions[func_code]
        return func(data)

    def run_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = ('localhost', 10003)
        print('starting up on {} port {}'.format(*server_address))
        sock.bind(server_address)

        sock.listen(1)

        while True:
            print('waiting for a connection')
            connection, client_address = sock.accept()
            try:
                print('connection from', client_address)

                while True:
                    
                    data = connection.recv(16)
                    if data:
                        response = self.respond(data)
                        print('received {}'.format(data.hex()))
                        print('sending {}'.format(response.hex()))
                        connection.sendall(response)
                    else:
                        break

            finally:
                connection.close()


