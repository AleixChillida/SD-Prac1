import time
import xmlrpc.client
from multiprocessing import Pool

NUM_REQUESTS = 1000
NUM_PROCESSES = 20

# Lista con URLs de los 3 servidores XML-RPC
SERVER_URLS = [
    "http://localhost:8000",
    "http://localhost:8001",
    "http://localhost:8002"
]

def send_insult(i):
    """Envía un insulto único al servidor XML-RPC correspondiente"""
    insult = f"insult-{i}"
    server_url = SERVER_URLS[i % len(SERVER_URLS)]  # Round-robin entre nodos
    try:
        proxy = xmlrpc.client.ServerProxy(server_url, allow_none=True)
        proxy.add_insult(insult)
    except Exception as e:
        print(f"Error enviando insulto {i} a {server_url}: {str(e)}")

if __name__ == "__main__":
    start = time.perf_counter()

    with Pool(NUM_PROCESSES) as pool:
        pool.map(send_insult, range(NUM_REQUESTS))

    duration = time.perf_counter() - start
    throughput = NUM_REQUESTS / duration

    print(f"[XML-RPC - Concurrente 3 nodos] Mensajes enviados: {NUM_REQUESTS}")
    print(f"[XML-RPC - Concurrente 3 nodos] Tiempo total: {duration:.2f}s")
    print(f"[XML-RPC - Concurrente 3 nodos] Throughput: {throughput:.2f} req/s")
