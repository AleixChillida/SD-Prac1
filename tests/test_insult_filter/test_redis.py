import unittest
import fakeredis
import time
from unittest.mock import patch
from insult_filter.redis_impl.redis_server import RedisInsultFilterServer

class TestRedisInsultFilter(unittest.TestCase):
    def setUp(self):
        # Configurar Redis falso
        self.fake_redis = fakeredis.FakeStrictRedis()
        
        # Inyectar Redis falso en el servidor
        self.server = RedisInsultFilterServer()
        self.server.redis = self.fake_redis
        
        # Limpiar datos de prueba
        self.fake_redis.flushall()
        
        # Reiniciar insultos básicos
        self.server._init_insults({"moron", "idiot", "fool", "stupid", "dumb", "loser"})

    def test_initial_insults(self):
        """Verifica que los insultos iniciales se cargan correctamente"""
        insults = self.server.get_insults()
        self.assertEqual(len(insults), 6)
        self.assertIn("idiot", insults)

    def test_add_insult(self):
        """Test para añadir nuevos insultos"""
        # Añadir nuevo insulto
        self.assertTrue(self.server.add_insult("jerk"))
        insults = self.server.get_insults()
        self.assertIn("jerk", insults)
        
        # Verificar que no se añaden duplicados
        self.assertFalse(self.server.add_insult("jerk"))
        self.assertEqual(len(insults), 7)  # 6 iniciales + 1 nuevo

    def test_text_filtering(self):
        """Verifica el filtrado de textos"""
        test_cases = [
            ("You are an idiot", "You are an ***CENSORED***"),
            ("Hello world", "Hello world"),
            ("Don't be stupid", "Don't be ***CENSORED***"),
            ("Complex test: you're a moron and fool", 
             "Complex test: you're a ***CENSORED*** and ***CENSORED***")
        ]
        
        for text, expected in test_cases:
            result = self.server._filter_text(text)
            self.assertEqual(result, expected)

    def test_queue_processing(self):
        """Verifica el procesamiento completo de la cola"""
        # Añadir tareas directamente a Redis
        texts = [
            "First test with idiot",
            "Second test with moron",
            "Clean text"
        ]
        for text in texts:
            self.fake_redis.rpush(self.server.tasks_key, text)
        
        # Procesar manualmente
        for _ in range(len(texts)):
            _, text = self.fake_redis.blpop(self.server.tasks_key)
            filtered = self.server._filter_text(text.decode('utf-8'))
            self.fake_redis.rpush(self.server.results_key, filtered)
        
        # Verificar resultados
        results = self.server.get_filtered_results()
        self.assertEqual(len(results), 3)
        self.assertIn("***CENSORED***", results[0])
        self.assertIn("***CENSORED***", results[1])
        self.assertNotIn("***CENSORED***", results[2])

    def test_concurrent_processing(self):
        """Test de procesamiento concurrente con workers"""
        from concurrent.futures import ThreadPoolExecutor
        
        # Configurar 2 workers
        self.server._start_workers(num_workers=2)
        
        # Añadir múltiples tareas
        texts = [f"Text {i} contains idiot" for i in range(5)]
        with ThreadPoolExecutor(max_workers=3) as executor:
            list(executor.map(
                lambda t: self.fake_redis.rpush(self.server.tasks_key, t),
                texts
            ))
        
        # Esperar a que se procesen
        time.sleep(0.5)  # Pequeña pausa para procesamiento
        
        # Verificar resultados
        results = self.server.get_filtered_results()
        self.assertEqual(len(results), len(texts))
        for res in results:
            self.assertIn("***CENSORED***", res)

if __name__ == '__main__':
    unittest.main()