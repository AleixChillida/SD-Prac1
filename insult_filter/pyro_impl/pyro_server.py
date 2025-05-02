import Pyro4
import threading
import queue

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class InsultFilterService:
    def __init__(self):
        self.insults = {"moron", "idiot", "fool", "stupid", "dumb", "loser"}
        self.filtered_results = []
        self.work_queue = queue.Queue()
        self._start_workers(num_workers=3)
        self._print_banner()

    def _print_banner(self):
        print("\n" + "="*60)
        print("PYRO INSULT FILTER SERVICE - ACTIVO")
        print(f"Insultos registrados: {self.insults}")

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
            
            # Mostrar resultados en el servidor
            self._display_processing(text, filtered_text)
            
            self.work_queue.task_done()

    def _display_processing(self, original, filtered):
        print(f" Entrada: {original}")
        print(f" Salida: {filtered}")

    def _filter_text(self, text):
        words = text.split()
        filtered_words = [
            "***CENSORED***" if word.lower() in self.insults else word 
            for word in words
        ]
        return " ".join(filtered_words)

    def add_insult(self, insult):
        insult = insult.lower()
        if insult not in self.insults:
            self.insults.add(insult)
            print(f"\n NUEVO INSULTO REGISTRADO: {insult}")
            return True
        return False

    def filter_text(self, text):
        self.work_queue.put(text)
        return f"Texto añadido a cola. Tamaño cola: {self.work_queue.qsize()}"

    def get_filtered_results(self):
        return self.filtered_results

    def get_insults(self):
        return list(self.insults)

def main():
    Pyro4.config.SERIALIZER = "serpent"
    Pyro4.config.SERVERTYPE = "multiplex"
    
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()

    uri = daemon.register(InsultFilterService)
    ns.register("insult.filter.service", uri)

    print("\n Servidor PyRO InsultFilter iniciado")

    
    try:
        daemon.requestLoop()
    finally:
        print("\nServidor deteniéndose...")

if __name__ == "__main__":
    main()