import socket, select
import time
import re

class TCPServer():

    def __init__(self, server_ip: str, server_port: int, code: str):
        self.server_ip = server_ip
        self.server_port = server_port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(0)
        self.server.bind((server_ip, server_port))
        self.server.listen(5)
        self.tcp_inputs = [self.server]
        self.tcp_outputs = []
        self.code = code

    def get_select(self):
        self.readable, self.writable, _ = select.select(self.tcp_inputs, self.tcp_outputs, self.tcp_inputs)

    def accept_conn(self, s):

        connection, client_address = s.accept()
        connection.setblocking(0)
        self.tcp_inputs.append(connection)
        print("Server connected to", client_address[0])
        time.sleep(0.5)

    def server_recv(self, connection=0, client_ip="-1"):

        if client_ip == "-1":

            total_data = connection.recv(1024)
            if not total_data:

                self.remove_conn(connection)

                return None

            else:

                total_data = self.decode_input(total_data)

                return total_data

        else:
            self.get_select() 
            for client in self.readable:

                if client.getpeername()[0]==client_ip:
                    
                    total_data = client.recv(1024)

                    if not total_data:
                
                        self.remove_conn(client)

                        return None

                    else:
                        
                        total_data = self.decode_input(total_data)

                        return total_data

            return ["-1"] #didn't find the connection yet

    def decode_input(self, data: str):
        
        decoded_message = data.decode("utf8", "strict")
        
        #this way, only "good" messages are parsed (the ones that begin AND end with the correct codes)
        raw_input = re.findall(r'#(.+?)%', decoded_message)

        output_data = raw_input[-1].split("_")

        return output_data

    def server_send(self, client_ip: str, message: str):
        for client in self.tcp_outputs:
            if client.getpeername()[0]==client_ip:
                encoded_message = self.encode_output(message)
                client.send(encoded_message)
                return 0

        print("Couldn't find client with IP address:", client_ip, "to send", message)
        return 0

    def server_close(self):

        self.server.close()
        print("Server closed!")

    def remove_conn(self,s):

        if s in self.tcp_outputs:
            self.tcp_outputs.remove(s)
        self.tcp_inputs.remove(s)
        print("Disconnected from", s.getpeername()[0])
        s.close()
    
    def encode_output(self, message: str):

        tmp_output = message + "_" + self.code

        output = "#" + tmp_output + "%"
        encoded_output = output.encode()

        return encoded_output
    
    def add_to_outputs(self, s):
        if s not in self.tcp_outputs:
            self.tcp_outputs.append(s)

class TCPClient():
    def __init__(self, server_ip: str, server_port: int, code: str):
        self.server_ip = server_ip
        self.server_port = server_port
        self.code = code

    def client_connect(self):

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.server_ip, self.server_port))
        self.client_send("init_0")
        self.connected = True
        print("Connected to server!")

    def client_send(self, message: str):
        
        encoded_message = self.encode_output(message)
        self.client.send(encoded_message)
    
    def encode_output(self, message: str):

        tmp_output = message + "_" + self.code

        output = "#" + tmp_output + "%"
        encoded_output = output.encode()
        
        return encoded_output
        
    def client_recv(self):

        total_data = self.client.recv(1024)
        if not total_data:
            
            return ["-1"]

        else:
  
            total_data = self.decode_input(total_data)
            
            return total_data
        
    def decode_input(self, data: str):
        decoded_str = data.decode("utf8", "strict")
        #this way, only "good" messages are parsed (the ones that begin AND end with the correct codes)
        raw_input = re.findall(r'#(.+?)%', decoded_str)

        output_data = raw_input[-1].split("_")

        return output_data

    def client_close(self):
        self.client.send(bytes())
        self.client.close()
        self.connected = False
        print("Disconnected from server!")