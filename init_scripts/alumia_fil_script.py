from threading import Thread, Event
from queue import Queue
import paramiko
import time

class sshPortal(Thread):

    def __init__(self, client_ip: str, client_user: str, client_pwd: str="", machine_name: str="", *args, **kwargs):

        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.connect(client_ip, username=client_user, password=client_pwd)
        self.write_event = Event()
        self.write_queue = Queue(maxsize=0)
        self.machine_name = machine_name
        self.pwd = client_pwd
        self.kill_event = Event()

        super().__init__( *args, **kwargs)

        self.run()

    def run(self):
        thread = Thread(target=self.read_write_cmd)
        thread.daemon = True
        thread.start()

    def write_to_machine(self, input_to_write):
        
        self.write_queue.put(input_to_write)
        self.write_event.set()

    def read_write_cmd(self):

        stdin, stdout, stderr = "", "", ""

        while True:
            self.write_event.wait()

            cmd_to_write = self.write_queue.get()

            if self.write_queue.empty():
                self.write_event.clear()

            stdin, stdout, stderr = self.client.exec_command(cmd_to_write, get_pty=True)

            if "-S" in cmd_to_write:
                stdin.write(self.pwd + '\n')
                stdin.flush()

            for line in stdout:
                if "END SIGNAL" in line:
                    self.kill_event.set()

                print(self.machine_name + ": " + line.strip('\n'))

            for line in stderr:
                print(self.machine_name + ": " + line.strip('\n'))

if __name__ == "__main__":

    mon_conn = sshPortal(client_ip="193.168.1.4", client_pwd="PASSWORD_TO_MENU", client_user="phd", machine_name="mon")
    ras_conn = sshPortal(client_ip="193.168.1.2", client_pwd="PASSWORD_TO_RASP", client_user="phd", machine_name="ras")

    mon_conn.write_to_machine("(xhost +; cd ~/; sudo -S ./init_script.sh)")
    ras_conn.write_to_machine("(cd ~/; sudo -S bash init_script.sh)")

    while not mon_conn.kill_event.is_set() and not ras_conn.kill_event.is_set():
        time.sleep(1)

    mon_conn.client.close()
    ras_conn.client.close()