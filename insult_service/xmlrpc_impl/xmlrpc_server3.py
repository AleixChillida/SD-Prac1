import xmlrpc.server
import xmlrpc.client
import random
import time
from threading import Thread
import sys

class InsultService:
    def __init__(self):
        self.insults = set()
        self.subscribers = set()  # Usamos set para evitar duplicados
        
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
            except Exception as e:
                print(f"Error notifying {url}: {str(e)}")
                self.subscribers.discard(url)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python xmlrpc_server.py <puerto>")
        sys.exit(1)

    port = int(sys.argv[1])
    server = xmlrpc.server.SimpleXMLRPCServer(("localhost", port), allow_none=True)
    service = InsultService()
    service.start_broadcasting(interval=5)
    
    server.register_instance(service)
    print(f"XML-RPC InsultService running on port {port}...")
    print("Broadcasting insults every 5 seconds to subscribers...")
    server.serve_forever()
