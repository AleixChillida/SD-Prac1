import Pyro4
import threading
import time

@Pyro4.expose
class Subscriber:
    def notify(self, insult):
        print(f"Received insult: {insult}")
        return True

def main():
    # Configuración esencial
    Pyro4.config.SERIALIZER = "serpent"
    
    # Crear e instanciar subscriber
    subscriber = Subscriber()
    daemon = Pyro4.Daemon()
    uri = daemon.register(subscriber)
    
    # Conectar al servidor principal
    ns = Pyro4.locateNS()
    service = Pyro4.Proxy(ns.lookup("insult.service"))
    
    # Registrar el callback
    if service.subscribe(uri):
        print(f"Successfully subscribed! URI: {uri}")
    else:
        print("Subscription failed")
    
    print("Waiting for insults... (Ctrl+C to stop)")

    # Iniciar el loop en segundo plano
    thread = threading.Thread(target=daemon.requestLoop, daemon=True)
    thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSubscriber stopped")

if __name__ == "__main__":
    main()
