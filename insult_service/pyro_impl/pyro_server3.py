# pyro_server_direct.py
import random
import time
import threading
import Pyro4
import sys

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class InsultService:
    def __init__(self):
        self.insults = set()
        self.subscribers = []
        self._start_broadcasting()

    def add_insult(self, insult):
        if insult not in self.insults:
            self.insults.add(insult)
            self._notify_subscribers(insult)
            return True
        return False

    def get_insults(self):
        return list(self.insults)

    def get_random_insult(self):
        if not self.insults:
            return ""
        return random.choice(list(self.insults))

    def subscribe(self, subscriber_uri):
        if subscriber_uri not in self.subscribers:
            self.subscribers.append(subscriber_uri)
            print(f"New subscriber: {subscriber_uri}")
            return True
        return False

    def _start_broadcasting(self, interval=5):
        def broadcast_loop():
            while True:
                if self.insults and self.subscribers:
                    insult = self.get_random_insult()
                    self._notify_subscribers(insult)
                time.sleep(interval)

        thread = threading.Thread(target=broadcast_loop, daemon=True)
        thread.start()

    def _notify_subscribers(self, insult):
        broken = []
        for uri in self.subscribers:
            try:
                sub = Pyro4.Proxy(uri)
                sub.notify(insult)
                print(f"Notified: {uri}")
            except Exception as e:
                print(f"Notification failed for {uri}: {str(e)}")
                broken.append(uri)
        self.subscribers = [uri for uri in self.subscribers if uri not in broken]

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python pyro_server_direct.py <service_name> <port>")
        sys.exit(1)

    service_name = sys.argv[1]
    port = int(sys.argv[2])

    Pyro4.config.SERIALIZER = "serpent"
    Pyro4.config.SERVERTYPE = "multiplex"

    daemon = Pyro4.Daemon(port=port)
    uri = daemon.register(InsultService(), objectId=service_name)

    print(f"PyRO InsultService '{service_name}' running on port {port}")
    print(f"Service URI: {uri}")
    print("Broadcasting insults every 5 seconds...")

    daemon.requestLoop()
