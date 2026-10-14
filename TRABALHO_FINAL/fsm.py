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
        #talvez eu preciso de uma variavel aqui pra pegar a msg lida?
        count_seq =0
        con = udp.setupConnection()
        result = udp.sendHello(con=con)
        while(count_seq<int(result['totalSegmentos'])):
            if(self.state ==states[0]):
                try:
                    a = udp.sendSegment(count_seq,con)
                    udp.sendACKbySegmentRecieved(count_seq,con)
                    count_seq+=1
                    self.md5.update(a)
                   # self.state = states[1]
                except Exception as e:
                    print("deu um erro aqui uai",e)
                    continue
                    #raise
        con.close()

        print(self.md5.hexdigest())


    def nextState(self):
        print("aaa")

    def isAck0(self,data):
        print("sim é um ACK0 que eu recebi")

    def wait_for_0_from_bellow(self):
        print("bb")

    def wait_for_1_from_bellow(self):
        print("ccc")

    def make_pkt(self,ack_sequence,data):
        #alguma lógica aqui para ter o time etc e também adicionar o checksum?
        print("criei o pacote que voce quer")
        #self.udt_send(str(data)+ack_sequence)


    def udt_send(self,msg):
        try:
            udp.sendMessage(msg,self.socket)
        except ConnectionError:
            self.sendACK()

    def isCorrupted(self,data):
        #fazer o checksum bem aqui 
        print("corrompido")

    def hasSeg0(self):
        print("seq0")
    
    def hasSeg1(self):
        print("seq0")

    def sendACK1(self):
        print("mandei ack1")

    def sendACK(self):
        print("mandei ack0")

    def sendHello(self):
        sucess = -1
        try:
            sucess = udp.sendHello()
            return sucess
        except timeout:
            print("to aqui pai")
            raise
        while(sucess !=0):
            print("estou aqui tentando ferrozmente")
            sucess = udp.sendHello()
            return sucess


