import re
from socket import *
import time
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
    except:
        raise ConnectionError("DEU RUIM PAIZAO CONEXAO DEU TIMEOUT HAHAHAHAHHAA TENTE DNV") 

def calculateRTT():
    start  = time.time()
    print("[1] PING")
    con = setupConnection()
    sendMessage("PING",con) 
    con.close()
    end = time.time()
    rtt = (end-start)*1000
    print(f"\tRTT: {rtt:.2f} ms")
    print()

def sendHello():
    msg = "HELLO|grupo="+grupo+"|segment_size=512|file=small"
    con = setupConnection()
    result = sendMessage(msg,con)
    con.close()
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

def sendSegment(segment=0):
    con = setupConnection()
    msg = "HELLO|grupo="+grupo+"|segment_size=512|file=small"
    sendMessage(msg,con)
    print("[3] REQ seg=0")
    result =  sendMessage("REQ|seq=0",con,False) 
    con.close()
    foundData = False
    countPipe =0
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
    data = []
    for c in primeiros:
        data.append(c)
    [print(f"{c:#x}", end=" ") for c in data]
    print()

    

if __name__ == "__main__":
    print("=== Tarefa 0 — RDT-UnB Explorer ===")
    print()
    print("Servidor: 137.131.178.229:8080")
    print()
    calculateRTT()
    sendHello()
    sendSegment()
