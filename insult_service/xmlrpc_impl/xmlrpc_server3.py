# insult_service_xmlrpc.py
import xmlrpc.server
import xmlrpc.client
import random
import time
from threading import Thread
from socketserver import ThreadingMixIn
import sys

class InsultService:
    def __init__(self):
        self.insults = set()
        self.subscribers = set()

    def add_insult(self, insult):
        if insult not in self.insults:
            self.insults.add(insult)
            return True
        return False

    def get_insults(self):
        return list(self.insults)

    def get_random_insult(self):
        if not self.insults:
            return ""
        return random.choice(list(self.insults))

    def add_subscriber(self, callback_url):
        if callback_url not in self.subscribers:
            self.subscribers.add(callback_url)
            return True
        return False

    def start_broadcasting(self, interval=5):
        def broadcast_loop():
            while True:
                if self.insults:
                    insult = self.get_random_insult()
                    self._notify_subscribers(insult)
                time.sleep(interval)
        Thread(target=broadcast_loop, daemon=True).start()

    def _notify_subscribers(self, insult):
        for url in list(self.subscribers):
            try:
                proxy = xmlrpc.client.ServerProxy(url)
                proxy.notify(insult)
            except Exception:
                self.subscribers.discard(url)

# 🔧 Aquí creamos el servidor multithread
class ThreadedXMLRPCServer(ThreadingMixIn, xmlrpc.server.SimpleXMLRPCServer):
    pass

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python insult_service_xmlrpc.py <puerto>")
        sys.exit(1)

    port = int(sys.argv[1])
    server = ThreadedXMLRPCServer(("0.0.0.0", port), allow_none=True)
    service = InsultService()
    service.start_broadcasting()
    server.register_instance(service)

    print(f"Servidor XML-RPC escuchando en el puerto {port}...")
    server.serve_forever()
