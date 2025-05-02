from unittest.mock import patch
import unittest
import time
import threading
from insult_filter.rabbitmq_impl.rabbitmq_client import RabbitMQInsultFilterClient
from insult_filter.rabbitmq_impl.rabbitmq_server import RabbitMQInsultFilterServer

class TestRabbitMQInsultFilter(unittest.TestCase):

    @patch("insult_filter.rabbitmq_impl.rabbitmq_client.pika.BlockingConnection")
    def test_client_publishes_message(self, mock_connection):
        """Verifica que el cliente publica mensajes correctamente sin entrar en bucle infinito"""
        mock_channel = mock_connection.return_value.channel.return_value

        client = RabbitMQInsultFilterClient()

        with patch.object(client, "_generate_text", return_value="This is a test message"):
            client.channel = mock_channel  
            
            def run_client():
                client.start_sending(interval=0.1)
            
            client_thread = threading.Thread(target=run_client, daemon=True)
            client_thread.start()

            time.sleep(0.3)  # Permitir algunos envíos
            self.assertTrue(mock_channel.basic_publish.called)

            client.connection.close()
            client_thread.join(timeout=1)

    @patch("insult_filter.rabbitmq_impl.rabbitmq_server.pika.BlockingConnection")
    def test_server_receives_and_filters_message(self, mock_connection):
        """Verifica que el servidor filtra correctamente un mensaje con insultos"""
        mock_channel = mock_connection.return_value.channel.return_value
        server = RabbitMQInsultFilterServer()
        server.channel = mock_channel

        message = "You are an idiot"
        expected_output = "You are an ***CENSORED***"

        filtered_message = server._filter_text(message)
        self.assertEqual(filtered_message, expected_output)

    def test_client_does_not_send_empty_messages(self):
        """Verifica que el cliente no envía mensajes vacíos"""
        client = RabbitMQInsultFilterClient()
        self.assertNotEqual(client._generate_text(), "")

    def test_server_does_not_filter_clean_message(self):
        """Verifica que el servidor no altera un mensaje sin insultos"""
        server = RabbitMQInsultFilterServer()
        message = "Hello, how are you?"
        self.assertEqual(server._filter_text(message), message)

    def test_server_filters_multiple_insults(self):
        """Verifica que el servidor filtra múltiples insultos en un mensaje"""
        server = RabbitMQInsultFilterServer()
        message = "You are a stupid idiot!"
        expected_output = "You are a ***CENSORED*** ***CENSORED***!"
        self.assertEqual(server._filter_text(message), expected_output)

    def test_server_does_not_modify_already_censored_message(self):
        """Verifica que el servidor no modifica mensajes ya censurados"""
        server = RabbitMQInsultFilterServer()
        message = "You are a ***CENSORED***"
        self.assertEqual(server._filter_text(message), message)

    def test_server_handles_special_characters(self):
        """Verifica que el servidor maneja caracteres especiales correctamente"""
        server = RabbitMQInsultFilterServer()
        message = "You are a STUPID idiot!!!"
        expected_output = "You are a ***CENSORED*** ***CENSORED***!!!"
        self.assertEqual(server._filter_text(message), expected_output)

if __name__ == "__main__":
    unittest.main()
