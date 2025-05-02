from xmlrpc.server import SimpleXMLRPCServer
import threading
import queue

class InsultFilterService:
    def __init__(self):
        self.insults = {"moron", "idiot", "fool", "stupid", "dumb", "loser"}
        self.filtered_results = []
        self.work_queue = queue.Queue()
        self._start_workers(num_workers=3)
        print("XML-RPC InsultFilterService initialized")

    def _start_workers(self, num_workers):
        for i in range(num_workers):
            worker = threading.Thread(
                target=self._process_queue,
                daemon=True,
                name=f"Worker-{i+1}"
            )
            worker.start()

    def _process_queue(self):
        while True:
            text = self.work_queue.get()
            filtered_text = self._filter_text(text)
            self.filtered_results.append(filtered_text)
            print(f"Processed: {text} -> {filtered_text}")
            self.work_queue.task_done()

    def _filter_text(self, text):
        words = text.split()
        filtered_words = [
            "CENSORED" if word.lower() in self.insults else word 
            for word in words
        ]
        return " ".join(filtered_words)

    def add_insult(self, insult):
        insult = insult.lower()
        if insult not in self.insults:
            self.insults.add(insult)
            print(f"New insult added: {insult}")
            return True
        return False

    def filter_text(self, text):
        self.work_queue.put(text)
        return f"Queued. Current queue size: {self.work_queue.qsize()}"

    def get_filtered_results(self):
        return self.filtered_results

    def get_insults(self):
        return list(self.insults)

def main():
    server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    service = InsultFilterService()
    server.register_instance(service)
    
    print("XML-RPC InsultFilterService running on port 8000...")
    server.serve_forever()

if __name__ == "__main__":
    main()