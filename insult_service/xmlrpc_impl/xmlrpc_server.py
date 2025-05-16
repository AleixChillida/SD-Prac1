        """Notifica a los suscriptores"""
        for url in list(self.subscribers):  # Usamos lista para evitar cambios durante iteración
            try:
                proxy = xmlrpc.client.ServerProxy(url)
                proxy.notify(insult)
            except Exception as e:
                print(f"Error notifying {url}: {str(e)}")
                self.subscribers.discard(url)

# Configuración del servidor
if __name__ == "__main__":
    server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    service = InsultService()
    service.start_broadcasting(interval=5)  # Broadcast cada 5 segundos
    
    server.register_instance(service)
    print("XML-RPC InsultService running on port 8000...")
    print("Broadcasting insults every 5 seconds to subscribers...")
    server.serve_forever()