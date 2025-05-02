import xmlrpc.client
import time
import random
from threading import Thread

class InsultFilterClient:
    def __init__(self):
        self.server = xmlrpc.client.ServerProxy("http://localhost:8000")
    
    def _generate_text(self):
        phrases = [
            "The weather is nice today",
            "I enjoy programming",
            "Let's go to the park",
            "Have a nice day",
            "You are such an idiot",
            "What a fool you are!",
            "Only a moron would do that",
            "Don't be dumb"
        ]
        return random.choice(phrases)
    
    def start_sending(self):
        def sender():
            while True:
                text = self._generate_text()
                try:
                    response = self.server.filter_text(text)
                    print(f"Sent: {text[:50]}... | Response: {response}")
                except ConnectionError:
                    print("Connection error, retrying...")
                time.sleep(3)
        
        Thread(target=sender, daemon=True).start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nClient stopped")

if __name__ == "__main__":
    client = InsultFilterClient()
    print("XML-RPC Filter Client started (Ctrl+C to stop)")
    client.start_sending()