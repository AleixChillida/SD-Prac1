import unittest
import queue
from unittest.mock import MagicMock, patch
from concurrent.futures import ThreadPoolExecutor

# Mock de Pyro4
class MockPyro4:
    class Daemon: pass
    @staticmethod
    def expose(cls): return cls
    @staticmethod
    def behavior(*args, **kwargs): return lambda cls: cls

# Aplicar mock antes de importar
import sys
sys.modules['Pyro4'] = MockPyro4()

from insult_filter.pyro_impl.pyro_server import InsultFilterService

class TestInsultFilterServicePyro(unittest.TestCase):
    def setUp(self):
        # Configuración común
        self.service = InsultFilterService()
        
        # Mock de la cola manteniendo comportamiento real
        self.real_queue = queue.Queue()
        self.service.work_queue = self.real_queue
        
        # Mock para workers (desactivamos procesamiento automático)
        self.service._start_workers = MagicMock()

    def test_filter_text_adds_to_queue(self):
        """Verifica que los textos se añaden a la cola"""
        test_text = "Test message"
        response = self.service.filter_text(test_text)
        
        self.assertEqual(self.real_queue.qsize(), 1)
        self.assertEqual(self.real_queue.get(), test_text)
        self.assertIn("Texto añadido a cola", response)

    def test_add_insult_updates_set(self):
        """Verifica añadir nuevos insultos"""
        original_count = len(self.service.insults)
        
        # Añadir nuevo insulto
        self.assertTrue(self.service.add_insult("jerk"))
        self.assertIn("jerk", self.service.insults)
        self.assertEqual(len(self.service.insults), original_count + 1)
        
        # Verificar duplicados
        self.assertFalse(self.service.add_insult("jerk"))
        self.assertEqual(len(self.service.insults), original_count + 1)

    def test_get_insults_returns_list(self):
        """Verifica obtener lista de insultos"""
        insults = self.service.get_insults()
        self.assertIsInstance(insults, list)
        self.assertGreaterEqual(len(insults), 5)  # Al menos los insultos por defecto

    def test_text_filtering_logic(self):
        """Verifica la lógica de filtrado (sin cola)"""
        test_cases = [
            ("You idiot", "You ***CENSORED***"),
            ("Hello world", "Hello world"),
            ("Don't be stupid", "Don't be ***CENSORED***")
        ]
        
        for text, expected in test_cases:
            result = self.service._filter_text(text)
            self.assertEqual(result, expected)

    def test_concurrent_operations(self):
        """Verifica operaciones concurrentes"""
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Ejecutar operaciones concurrentemente
            futures = [
                executor.submit(self.service.filter_text, f"Text {i}") 
                for i in range(5)
            ]
            
            # Verificar respuestas
            for future in futures:
                response = future.result(timeout=1)
                self.assertIn("Texto añadido a cola", response)
            
            # Verificar cola
            self.assertEqual(self.real_queue.qsize(), 5)

if __name__ == '__main__':
    unittest.main()