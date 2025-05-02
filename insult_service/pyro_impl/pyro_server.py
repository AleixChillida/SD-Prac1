import random
import time
import threading
import Pyro4

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class InsultService:
    def __init__(self):
        self.insults = set()
        self.subscribers = []  # Usamos lista en vez de set
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
            self.subscribers.append(subscriber_uri)  # Añadimos correctamente
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
        broken_subscribers = []
        for uri in self.subscribers:
            try:
                subscriber = Pyro4.Proxy(uri)
                subscriber.notify(insult)  # Llamada correcta
                print(f"Notified: {uri}")
            except Exception as e:
                print(f"Notification failed for {uri}: {str(e)}")
                broken_subscribers.append(uri)

        # Eliminamos los suscriptores que fallaron
        self.subscribers = [uri for uri in self.subscribers if uri not in broken_subscribers]

if __name__ == "__main__":
    Pyro4.config.SERIALIZER = "serpent"
    Pyro4.config.SERVERTYPE = "multiplex"
    
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()

    uri = daemon.register(InsultService)
    ns.register("insult.service", uri)

    print("PyRO InsultService running...")
    print(f"Service URI: {uri}")
    print("Broadcasting insults every 5 seconds...")
    
    try:
        daemon.requestLoop()
    finally:
        ns.remove("insult.service")
