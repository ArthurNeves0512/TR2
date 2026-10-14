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
        self.md5 = hashlib.md5()
    def execute(self,server,group,file):
        count_seq = 0
        arquivo = bytearray()

        con = udp.setupConnection(server,group)
        result = udp.sendHello(con=con,file=file)
        print("Fazendo o download ",end=" ")
        while count_seq < int(result['totalSegmentos']):
            print(".",end="",flush=True)
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
        print()
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



