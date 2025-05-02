import re
import pika
import threading
import time
from datetime import datetime

class RabbitMQInsultFilterServer:
    def __init__(self, host='localhost'):
        self.insults = {"moron", "idiot", "fool", "stupid", "dumb", "loser"}
        self.filtered_results = []
        
        # Conexión a RabbitMQ
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        
        # Declarar colas
        self.channel.queue_declare(queue='filter_tasks')
        self.channel.queue_declare(queue='filter_results')
        
        # Configurar consumo de mensajes
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue='filter_tasks',
            on_message_callback=self._process_message
        )
        
        self._print_banner()

    def _print_banner(self):
        """Muestra información del servidor al iniciar"""
        print(f"Insultos registrados: {self.insults}")

    def _process_message(self, ch, method, properties, body):
        """Procesa cada mensaje recibido"""
        text = body.decode('utf-8')
        
        # Filtrar el texto
        filtered_text = self._filter_text(text)
        
        # Almacenar resultado
        self.filtered_results.append(filtered_text)
        
        # Mostrar en terminal
        self._display_processing(text, filtered_text)
        
        # Publicar resultado (opcional)
        self.channel.basic_publish(
            exchange='',
            routing_key='filter_results',
            body=filtered_text
        )
        
        # Confirmar procesamiento
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def _display_processing(self, original, filtered):
        """Muestra el procesamiento en el terminal del servidor"""
        print(f" Entrada: {original}")
        print(f" Salida: {filtered}")

    def _filter_text(self, text):
        """Filtra insultos en el texto, manejando signos de puntuación"""
        pattern = r'\b(' + '|'.join(map(re.escape, self.insults)) + r')\b'
        return re.sub(pattern, '***CENSORED***', text, flags=re.IGNORECASE)

    def add_insult(self, insult):
        """Añade un nuevo insulto al conjunto"""
        insult = insult.lower()
        if insult not in self.insults:
            self.insults.add(insult)
            print(f"\n NUEVO INSULTO REGISTRADO: {insult}")
            return True
        return False

    def get_filtered_results(self):
        """Obtiene todos los resultados filtrados"""
        return self.filtered_results

    def get_insults(self):
        """Obtiene la lista de insultos"""
        return list(self.insults)

    def start_consuming(self):
        """Inicia el consumo de mensajes"""
        print(" [*] Esperando mensajes. Presiona CTRL+C para salir")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.close()
            print("\nServidor deteniéndose...")

    def close(self):
        """Cierra la conexión de RabbitMQ de manera segura"""
        if self.channel:
            self.channel.stop_consuming()
        if self.connection:
            self.connection.close()
        print("Conexión cerrada correctamente.")


def main():
    print("\nIniciando servidor RabbitMQ InsultFilter...")
    server = RabbitMQInsultFilterServer()
    try:
        server.start_consuming()
    finally:
        server.close()

if __name__ == "__main__":
    main()