import re
from socket import *
serverName="137.131.178.229"
serverPort = 8080
grupo = "grupo09"

def setupConnection(server,group,timeout=5.0):
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(timeout)
    global serverName
    global  grupo
    serverName=server
    grupo = group


    return  clientSocket 

def sendMessage(msg,socket,toDecode=True)->str:
    try:
        socket.sendto(msg.encode(), (serverName, serverPort))
        modifiedMessage, serverAddress = socket.recvfrom(65507)
        if(toDecode):
            return modifiedMessage.decode()
        return modifiedMessage
    except timeout:
        raise 
    except Exception as e: 
        print("ih rapaz deu outro problema")
        return ""


def sendHello(segment_size=512,con=None,file=None):
    msg = "HELLO|grupo="+grupo+"|segment_size="+str(segment_size)+"|file="+str(file)
    result =''
    try:
        result = sendMessage(msg,con)
    except timeout:
        raise
    splitted = result.split("|")
    helloData ={
        "fileSize":"",
        "checkSum": "",
        "segment_size": ""
    }
    helloData["fileSize"]=splitted[1].split("=")[1]
    helloData["checkSum"]=splitted[2].split("=")[1]
    helloData["totalSegmentos"]=splitted[4].split("=")[1]
    helloData["segment_size"]=splitted[5].split("=")[1]

    print("[2] HELLO")
    print(f"\t Arquivo: {file} ({helloData['fileSize']} bytes = {int(helloData['fileSize'])/1024} KB)")
    print(f"\t Checksum MD5: {helloData['checkSum']}")
    print(f"\t Total segmentos: {helloData['totalSegmentos']}")
    print(f"\t Tamanho segmento: {helloData['segment_size']} bytes")
    print()
    return helloData

def sendSegment(segment=0,con=None):
    #print("segmento solicitado: ",segment)
    try:
        result =  sendMessage("REQ|seq="+str(segment),con,False) 
        #sendMessage("ACK|seq="+str(segment),con,False) 
    except Exception as e:
        print("pow dei problema aqui cara",e)
        raise

    while True:
        countPipe = 0
        it = 0
        
        while it < len(result) and countPipe < 3:
            if result[it] == 0x7C:
                countPipe += 1
            it += 1 
            
        if countPipe < 3:
            raise Exception(f"Pacote malformado do servidor: {result}")

        # confere se o pacote recebido é o que pedimos (mesmo seq)
        achou = re.search(rb"seq=(\d+)", result[:it])
        if achou and int(achou.group(1)) == segment:
            return result[it:]
        result, _ = con.recvfrom(65507)

def sendACKbySegmentRecieved(segment,con):
    sendMessage(f'ACK|seq={segment}',con)

def sendREQ(segment, con):
    # só envia o REQ e NÃO espera resposta
    con.sendto(("REQ|seq=" + str(segment)).encode(), (serverName, serverPort))

def sendACK(segment, con):
    # só envia o ACK e NÃO espera resposta
    con.sendto(("ACK|seq=" + str(segment)).encode(), (serverName, serverPort))

def recvDATA(con, espera):
    # espera um pacote por no máximo 'espera' segundos
    # devolve (seq, payload) ou None se deu timeout
    con.settimeout(max(espera, 0.001))
    try:
        pacote, _ = con.recvfrom(65507)
    except timeout:
        return None
    except ConnectionResetError:   
        return None
    pipes = 0
    it = 0
    while it < len(pacote) and pipes < 3:
        if pacote[it] == 0x7C:
            pipes += 1
        it += 1
    achou = re.search(rb"seq=(\d+)", pacote[:it])
    if pipes < 3 or not achou:
        return None
    return int(achou.group(1)), pacote[it:]

def limparBuffer(con):
    con.settimeout(0.05)
    try:
        while True:
            con.recvfrom(65507)
    except timeout:
        pass
    except ConnectionResetError:
        pass