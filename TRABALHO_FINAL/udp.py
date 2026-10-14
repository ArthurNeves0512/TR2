from socket import *
serverName="137.131.178.229"
serverPort = 8080
grupo = "grupo09"

def setupConnection(timeout=5.0):
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(timeout)
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

def sendHello(segment_size=512,con=None):
    msg = "HELLO|grupo="+grupo+"|segment_size="+str(segment_size)+"|file=small"
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
    print(f"\t Arquivo: small ({helloData['fileSize']} bytes = {int(helloData['fileSize'])/1024} KB)")
    print(f"\t Checksum MD5: {helloData['checkSum']}")
    print(f"\t Total segmentos: {helloData['totalSegmentos']}")
    print(f"\t Tamanho segmento: {helloData['segment_size']} bytes")
    print()
    return helloData

def sendSegment(segment=0,con=None):
    print("segmento solicitado: ",segment)
    try:
        result =  sendMessage("REQ|seq="+str(segment),con,False) 
        sendMessage("ACK|seq="+str(segment),con,False) 
    except Exception as e:
        print("pow dei problema aqui cara",e)
        raise

    #con.close()
    foundData = False
    countPipe =0
    #print("Mensagem recebida:", repr(result))
    #print("Tamanho:", len(result))
    it =0
    while(not foundData):
        if(countPipe==3):
            break
        elif(result[it]==0x7C):
           countPipe+=1
        it+=1 
    it+=1
    print(f"\tPrimeiros 8 bytes: ", end=" ")
    primeiros = result[it:it+8]
    print(type(primeiros))
    return result
    data = []
    for c in primeiros:
        data.append(c)
    [print(f"{c:#x}", end=" ") for c in data]
    print()

def sendACKbySegmentRecieved(segment,con):
    sendMessage(f'ACK|seq={segment}',con)

