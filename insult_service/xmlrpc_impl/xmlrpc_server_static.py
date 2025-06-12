import xmlrpc.server
import random
from socketserver import ThreadingMixIn
import sys

class InsultService:
    def __init__(self):
        self.insults = set()

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

# Servidor multihilo
class ThreadedXMLRPCServer(ThreadingMixIn, xmlrpc.server.SimpleXMLRPCServer):
    pass

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python xmlrpc_threaded_server.py <puerto>")
        sys.exit(1)

    port = int(sys.argv[1])
    server = ThreadedXMLRPCServer(("localhost", port), allow_none=True)
    service = InsultService()
    server.register_instance(service)

    print(f"XML-RPC InsultService multihilo ejecutándose en el puerto {port}...")
    server.serve_forever()
