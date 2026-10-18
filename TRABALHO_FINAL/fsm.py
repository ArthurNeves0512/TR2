from socket import timeout
import udp as udp
import hashlib
import time
import csv
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

    def execute(self, server, group, file):
        count_seq = 0
        arquivo = bytearray()
        
        con = udp.setupConnection(server, group)
        result = udp.sendHello(con=con, file=file)
        print("Fazendo o download ", end="")
        
        timestamp_atual = int(time.time())
        self.metrics_file = f"metrics_{group}_saw_{timestamp_atual}.csv"
        
        with open(self.metrics_file, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'segment', 'timestamp', 'size_bytes', 'rtt_ms', 
                'rtt_estimated_ms', 'timeout_ms', 'throughput_kbps', 
                'retransmissions', 'timeout_occurred', 'window_size', 'protocol'
            ])

        while count_seq < int(result['totalSegmentos']):
            print(".", end="", flush=True)
            if self.state == states[0]:
                try:
                    # Marca o tempo antes de enviar/receber o segmento
                    start_time = time.time()
                    
                    a = udp.sendSegment(count_seq, con)
                    
                    # Marca o tempo depois que o pacote chegou com sucesso
                    end_time = time.time()
                    rtt_medido_ms = (end_time - start_time) * 1000

                    arquivo.extend(a)
                    
                    tamanho_payload = len(a)
                    throughput_kbps = (tamanho_payload * 8) / rtt_medido_ms if rtt_medido_ms > 0 else 0
                    horario_recebimento = datetime.now().isoformat()
                    timeout_configurado = con.gettimeout() * 1000 if con.gettimeout() else 1000
                    
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
                            'saw'
                        ])

                    count_seq += 1

                except timeout:
                    print("\nTimeout! Retransmitindo pacote", count_seq)
                    # Registrando a ocorrência de timeout no CSV
                    with open(self.metrics_file, mode='a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([
                            count_seq, datetime.now().isoformat(), 0, 0, 0, 
                            con.gettimeout() * 1000 if con.gettimeout() else 1000, 
                            0, 1, 1, 1, 'saw'
                        ])
                    continue
                except Exception as e:
                    print("deu um erro aqui uai", e)
                    continue

        self.md5.update(arquivo)
        print()
        checksum_final = self.md5.hexdigest()
        print("MD5 Final do arquivo:", checksum_final)
        
        result = udp.sendMessage(f'FIN|checksum={checksum_final}', con)
        print(result)
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