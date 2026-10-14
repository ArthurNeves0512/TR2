from socket import timeout
import udp as udp
import hashlib

states={
    0:"Waiting for call 0 from above",
    1:"Waiting for ACK 0",
    2:"Waiting for 1 from above",
    3:"Waiting for ACK 1",
}
class FSM:
    
    def __init__(self) -> None:
        self.state=states[0] 
        self.seq_waiting = 0
        self.socket = udp.setupConnection(5)
        self.md5 = hashlib.md5()
    def execute(self):
        count_seq = 0
        arquivo = bytearray()

        con = udp.setupConnection()
        result = udp.sendHello(con=con)

        while count_seq < int(result['totalSegmentos']):
            if self.state == states[0]:
                try:
                    a = udp.sendSegment(count_seq, con)

                    arquivo.extend(a)

                    # udp.sendACKbySegmentRecieved(count_seq, con)

                    count_seq += 1

                except Exception as e:
                    print("deu um erro aqui uai", e)
                    continue


        self.md5.update(arquivo)

        result = udp.sendMessage(f'FIN|checksum={hashlib.md5(arquivo).hexdigest()}',con)
        print(result)
        con.close()




    def sendHello(self):
        sucess = -1
        try:
            while(sucess !=0):
                print("estou aqui tentando ferrozmente")
                sucess = udp.sendHello()
                return sucess
        except timeout:
            print("to aqui pai")
            raise



