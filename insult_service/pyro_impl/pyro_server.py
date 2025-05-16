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