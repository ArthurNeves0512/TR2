import re
from socket import *
import time
serverName="137.131.178.229"
serverPort = 8080
grupo = "grupo01"
def setupConnection(timeout=5.0):
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(timeout)
    return  clientSocket 

def sendMessage(msg)->str:
    try:
        socket = setupConnection()
        socket.sendto(msg.encode(), (serverName, serverPort))
        modifiedMessage, serverAddress = socket.recvfrom(65507)
        print(modifiedMessage.decode())
        socket.close()
        return modifiedMessage.decode()
    except:
        raise ConnectionError("DEU RUIM PAIZAO CONEXAO DEU TIMEOUT HAHAHAHAHHAA TENTE DNV") 

def calculateRTT():
    start  = time.time()
    sendMessage("PING") 
    end = time.time()
    rtt = (end-start)*1000
    print("RTT at ms",rtt)

def sendHello():
    msg = "HELLO|grupo="+grupo+"|segment_size=512|file=small"
    result = sendMessage(msg)
    splitted = result.split("|")
    helloData ={
        "fileSize":"",
        "checkSum": "",
        "segment_size": ""
    }
    helloData["fileSize"]=splitted[1].split("=")[1]
    helloData["checkSum"]=splitted[2].split("=")[1]
    helloData["segment_size"]=splitted[4].split("=")[1]
    print(helloData)


def sendSegment(segment=0):
    sendMessage("REQ|seg=0")

if __name__ == "__main__":
    sendMessage("PING")
    calculateRTT()
    sendHello()
    sendSegment()
