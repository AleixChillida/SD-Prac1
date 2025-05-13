import time
import xmlrpc.client
from multiprocessing import Pool

NUM_REQUESTS = 1000
NUM_PROCESSES = 20
SERVER_URL = "http://localhost:8000"

def send_insult(i):
    """Envía un insulto único al servicio XML-RPC"""
    insult = f"insult-{i}"
    try:
        proxy = xmlrpc.client.ServerProxy(SERVER_URL, allow_none=True)
        proxy.add_insult(insult)
    except Exception as e:
        print(f"Error enviando insulto {i}: {str(e)}")

if __name__ == "__main__":
    start = time.perf_counter()

    with Pool(NUM_PROCESSES) as pool:
        pool.map(send_insult, range(NUM_REQUESTS))

    duration = time.perf_counter() - start
    throughput = NUM_REQUESTS / duration

    print(f"[XML-RPC - Concurrente] Mensajes enviados: {NUM_REQUESTS}")
    print(f"[XML-RPC - Concurrente] Tiempo total: {duration:.2f}s")
    print(f"[XML-RPC - Concurrente] Throughput: {throughput:.2f} req/s")
