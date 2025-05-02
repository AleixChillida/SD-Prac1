import unittest
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
from threading import Thread
import time

class TestInsultFilterServiceXMLRPC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Crear una implementación real para testing
        class TestService:
            def __init__(self):
                self.insults = {"idiot", "moron"}
                self.filtered_results = []
            
            def add_insult(self, insult):
                insult = insult.lower()
                if insult not in self.insults:
                    self.insults.add(insult)
                    return True
                return False
            
            def filter_text(self, text):
                self.filtered_results.append(text)
                return f"Processed: {text}"
            
            def get_filtered_results(self):
                return self.filtered_results
            
            def get_insults(self):
                return list(self.insults)

        # Iniciar servidor de prueba
        cls.server = SimpleXMLRPCServer(("localhost", 8001), allow_none=True)
        cls.test_service = TestService()
        cls.server.register_instance(cls.test_service)
        
        cls.server_thread = Thread(target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        
        # Pequeña pausa para que el servidor inicie
        time.sleep(0.1)
        
        cls.client = xmlrpc.client.ServerProxy("http://localhost:8001")

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server_thread.join()

    def setUp(self):
        # Resetear el estado del servicio entre tests
        self.test_service.insults = {"idiot", "moron"}
        self.test_service.filtered_results = []

    def test_filter_text(self):
        response = self.client.filter_text("test message")
        self.assertEqual(response, "Processed: test message")
        self.assertEqual(self.test_service.filtered_results[-1], "test message")

    def test_add_insult(self):
        # Añadir nuevo insulto
        self.assertTrue(self.client.add_insult("jerk"))
        self.assertIn("jerk", self.test_service.insults)
        
        # Verificar duplicado
        self.assertFalse(self.client.add_insult("jerk"))

    def test_get_insults(self):
        insults = self.client.get_insults()
        self.assertIsInstance(insults, list)
        self.assertGreaterEqual(len(insults), 2)

    def test_get_filtered_results(self):
        self.client.filter_text("test 1")
        self.client.filter_text("test 2")
        results = self.client.get_filtered_results()
        self.assertEqual(len(results), 2)
        self.assertIn("test 1", results)

if __name__ == '__main__':
    unittest.main()