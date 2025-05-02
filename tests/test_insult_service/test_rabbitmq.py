import unittest
import pika
import time

class TestInsultServiceRabbitMQ(unittest.TestCase):

    def setUp(self):
        # Establecer conexión
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        # Limpieza de colas/exchanges existentes
        self._clean_rabbitmq_resources()

        # Configuración inicial
        self.channel.queue_declare(queue='insult_queue', durable=False)
        self.channel.exchange_declare(exchange='insult_exchange', exchange_type='fanout')

    def _clean_rabbitmq_resources(self):
        """Elimina colas y exchanges existentes para evitar conflictos"""
        # Limpiar cola de insultos
        try:
            self.channel.queue_delete(queue='insult_queue')
        except pika.exceptions.ChannelClosedByBroker:
            pass  # La cola no existía

        # Limpiar exchange de broadcasting
        try:
            self.channel.exchange_delete(exchange='insult_exchange')
        except pika.exceptions.ChannelClosedByBroker:
            pass  # El exchange no existía

    def tearDown(self):
        # Limpieza final
        try:
            self._clean_rabbitmq_resources()
        finally:
            self.connection.close()

    def test_producer_adds_insult_to_queue(self):
        """Verificar que el Producer añade insultos a la cola."""
        # Publicar mensaje de prueba
        test_insult = "Eres un tonto"
        self.channel.basic_publish(
            exchange='',
            routing_key='insult_queue',
            body=test_insult
        )

        # Recuperar el mensaje
        method_frame, _, body = self.channel.basic_get(queue='insult_queue', auto_ack=True)
        
        # Verificaciones
        self.assertIsNotNone(method_frame, "No se encontró mensaje en la cola")
        self.assertEqual(body.decode(), test_insult, "El insulto no coincide")

    def test_broadcaster_publishes_insult(self):
        """Verificar que el Broadcaster publica insultos en el exchange."""
        # Crear cola temporal para testing
        result = self.channel.queue_declare(queue='', exclusive=True)
        temp_queue = result.method.queue
        self.channel.queue_bind(exchange='insult_exchange', queue=temp_queue)

        # Publicar mensaje de prueba
        test_insult = "Eres un idiota"
        self.channel.basic_publish(
            exchange='insult_exchange',
            routing_key='',
            body=test_insult
        )

        # Pequeña pausa para permitir la entrega
        time.sleep(0.1)

        # Verificar recepción
        method_frame, _, body = self.channel.basic_get(queue=temp_queue, auto_ack=True)
        self.assertIsNotNone(method_frame, "No se recibió el mensaje broadcast")
        self.assertEqual(body.decode(), test_insult, "El insulto broadcast no coincide")

    def test_receiver_receives_insult(self):
        """Verificar que el Receiver recibe insultos del exchange."""
        # Configurar cola temporal
        result = self.channel.queue_declare(queue='', exclusive=True)
        temp_queue = result.method.queue
        self.channel.queue_bind(exchange='insult_exchange', queue=temp_queue)

        # Enviar mensaje de prueba
        test_insult = "Eres un imbécil"
        self.channel.basic_publish(
            exchange='insult_exchange',
            routing_key='',
            body=test_insult
        )

        # Verificar recepción
        method_frame, _, body = self.channel.basic_get(queue=temp_queue, auto_ack=True)
        self.assertIsNotNone(method_frame, "El receiver no recibió el mensaje")
        self.assertEqual(body.decode(), test_insult, "El insulto recibido no coincide")

    def test_consumer_processes_insult(self):
        """Verificar que el Consumer recibe insultos de la cola."""
        # Enviar mensaje de prueba
        test_insult = "Eres un ignorante"
        self.channel.basic_publish(
            exchange='',
            routing_key='insult_queue',
            body=test_insult
        )

        # Recuperar mensaje
        method_frame, _, body = self.channel.basic_get(queue='insult_queue', auto_ack=True)
        
        # Verificaciones
        self.assertIsNotNone(method_frame, "El consumer no encontró mensajes")
        self.assertEqual(body.decode(), test_insult, "El insulto procesado no coincide")

if __name__ == '__main__':
    unittest.main()