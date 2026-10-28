from socket import timeout
import udp as udp
import hashlib
import time
import csv
import os                      
import random                  
import gbn                     
import sr   
from datetime import datetime

states = {
    0: "Waiting for call 0 from above",
    1: "Waiting for ACK 0",
    2: "Waiting for call 1 from above",
    3: "Waiting for ACK 1",
}

class FSM:
    def __init__(self) -> None:
        self.state = states[0]
        self.seq_waiting = 0
        self.md5 = hashlib.md5()
        self.metrics_file = None

    # Registra metricas dos segmnetos gbn e sr no arquivo CSV
    def registrar(self, seq, tamanho, rtt_ms, timeout_ms, retx, timeout_occ, perda_sim):
        throughput_kbps = (tamanho * 8) / rtt_ms if rtt_ms > 0 else 0
        if retx == 0:
            self.rtts.append(rtt_ms)
        with open(self.metrics_file, mode='a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                seq, datetime.now().isoformat(), tamanho, round(rtt_ms, 2),
                0, timeout_ms, round(throughput_kbps, 2),
                retx, timeout_occ, self.window, self.protocol, perda_sim
            ])

    # parâmetros protocol, window, loss e timeout_s
    def execute(self, server, group, file, protocol="saw", window=1, loss=0.0, timeout_s=1.0):
        if protocol == "saw":               
            window = 1
        self.protocol = protocol            
        self.window = window                
        self.md5 = hashlib.md5()            
        self.rtts = []                      
        self.total_retx = 0                 
        perda_simulada = False              

        count_seq = 0
        arquivo = bytearray()
        
        con = udp.setupConnection(server, group, timeout_s)   
        result = udp.sendHello(con=con, file=file)
        print("Fazendo o download ", end="")
        
        timestamp_atual = int(time.time())
        self.metrics_file = f"metrics_{group}_{protocol}_w{window}_{file}_loss{loss:g}_{timestamp_atual}.csv"
        
        with open(self.metrics_file, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'segment', 'timestamp', 'size_bytes', 'rtt_ms', 
                'rtt_estimated_ms', 'timeout_ms', 'throughput_kbps', 
                'retransmissions', 'timeout_occurred', 'window_size', 'protocol',
                'simulated_loss'
            ])

        inicio = time.time()

        if protocol == "saw":                                    
            while count_seq < int(result['totalSegmentos']):
                print(".", end="", flush=True)
                if self.state == states[0]:
                    try:
                        # Marca o tempo antes de enviar/receber o segmento
                        start_time = time.time()
                    
                        a = udp.sendSegment(count_seq, con)

                        # Simula perda de pacote com base na taxa de perda especificada
                        if random.random() < loss / 100:
                            perda_simulada = True
                            time.sleep(con.gettimeout())
                            raise timeout
                    
                        # Marca o tempo depois que o pacote chegou com sucesso
                        end_time = time.time()
                        rtt_medido_ms = (end_time - start_time) * 1000
                        #udp.sendACK(count_seq,con)

                        arquivo.extend(a)
                    
                        tamanho_payload = len(a)
                        throughput_kbps = (tamanho_payload * 8) / rtt_medido_ms if rtt_medido_ms > 0 else 0
                        horario_recebimento = datetime.now().isoformat()
                        timeout_configurado = con.gettimeout() * 1000 if con.gettimeout() else 1000
                        self.rtts.append(rtt_medido_ms)

                        with open(self.metrics_file, mode='a', newline='') as csvfile:
                            writer = csv.writer(csvfile)
                            writer.writerow([
                                count_seq,
                                horario_recebimento,
                                tamanho_payload,
                                round(rtt_medido_ms, 2),
                                0, 
                                timeout_configurado,
                                round(throughput_kbps, 2),
                                0, # retransmissão
                                0, # ocorreu_timeout
                                1, 
                                'saw',
                                0 #Simula perda
                            ])

                        count_seq += 1

                    except timeout:
                        print("\nTimeout! Retransmitindo pacote", count_seq)
                        self.total_retx += 1 
                        # Registrando a ocorrência de timeout no CSV
                        with open(self.metrics_file, mode='a', newline='') as csvfile:
                            writer = csv.writer(csvfile)
                            writer.writerow([
                                count_seq, datetime.now().isoformat(), 0, 0, 0, 
                                con.gettimeout() * 1000 if con.gettimeout() else 1000, 
                                0, 1, 1, 1, 'saw',
                                int(perda_simulada)
                            ])
                            perda_simulada = False  # Resetando a flag de perda simulada
                        continue
                    except Exception as e:
                        print("deu um erro aqui uai", e)
                        break

        elif protocol == "gbn":                                   
            arquivo, self.total_retx = gbn.receber(con, int(result['totalSegmentos']), window, loss, self.registrar)
            con.settimeout(timeout_s)
        else:                                                    
            arquivo, self.total_retx = sr.receber(con, int(result['totalSegmentos']), window, loss, self.registrar)
            con.settimeout(timeout_s)

        tempo_total = time.time() - inicio 

        self.md5.update(arquivo)
        print()
        checksum_final = self.md5.hexdigest()
        print("MD5 Final do arquivo:", checksum_final)
        print("MD5 esperado        :", result['checkSum'], "->",
              "OK" if checksum_final == result['checkSum'].strip().lower() else "DIFERENTE!")   
        
        thr_medio = len(arquivo) * 8 / (tempo_total * 1000)       # kbps
        rtt_medio = sum(self.rtts) / len(self.rtts) if self.rtts else 0
        thr_teorico = window * int(result['segment_size']) * 8 / rtt_medio if rtt_medio else 0
        print(f"Tempo total: {tempo_total:.2f}s | Throughput: {thr_medio:.2f} kbps | "
              f"Teórico: {thr_teorico:.2f} kbps | RTT médio: {rtt_medio:.2f} ms | "
              f"Retransmissões: {self.total_retx}")

        novo = not os.path.exists("resultados_resumo.csv")
        with open("resultados_resumo.csv", "a", newline='') as f:
            w = csv.writer(f)
            if novo:
                w.writerow(['file', 'protocol', 'window', 'loss', 'tempo_total_s',
                            'throughput_medio_kbps', 'rtt_medio_ms',
                            'throughput_teorico_kbps', 'retransmissoes', 'md5'])
            w.writerow([file, protocol, window, loss, round(tempo_total, 3),
                        round(thr_medio, 2), round(rtt_medio, 2),
                        round(thr_teorico, 2), self.total_retx, checksum_final])
        
        udp.limparBuffer(con)          
        con.settimeout(timeout_s)
        try:
            result = udp.sendMessage(f'FIN|checksum={checksum_final}', con)
            print(result)
        except timeout:
            print("Sem resposta ao FIN (timeout)")
        con.close()

    def sendHello(self):
        sucess = -1
        try:
            while(sucess != 0):
                print("estou aqui tentando ferozmente")
                sucess = udp.sendHello()
                return sucess
        except timeout:
            print("to aqui pai")
            raise