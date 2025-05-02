import unittest
from insult_service.pyro_impl.pyro_server import InsultService  # Importamos directamente la clase

class TestInsultService(unittest.TestCase):
    
    def setUp(self):
        """Configura una nueva instancia del servicio PyRO para cada test."""
        self.insult_service = InsultService()

    def test_add_insult(self):
        """Prueba agregar insultos al servicio PyRO."""
        self.assertTrue(self.insult_service.add_insult("You are a fool!"))
        self.assertFalse(self.insult_service.add_insult("You are a fool!"))  # No debe agregar duplicados
        self.assertTrue(self.insult_service.add_insult("You are an idiot!"))

    def test_get_insults(self):
        """Prueba obtener la lista de insultos en PyRO."""
        insults = ["You are a fool!", "You are an idiot!", "You are a nincompoop!"]
        for insult in insults:
            self.insult_service.add_insult(insult)
        
        result = self.insult_service.get_insults()
        self.assertEqual(set(result), set(insults))  # Convertimos a set para evitar problemas de orden

    def test_get_random_insult(self):
        """Prueba obtener un insulto aleatorio en PyRO."""
        insults = ["You are a fool!", "You are an idiot!", "You are a nincompoop!"]
        for insult in insults:
            self.insult_service.add_insult(insult)
        
        random_insult = self.insult_service.get_random_insult()
        self.assertIn(random_insult, insults)  # Debe devolver un insulto de la lista

    def test_get_random_insult_empty(self):
        """Prueba obtener un insulto cuando la lista está vacía en PyRO."""
        self.assertEqual(self.insult_service.get_random_insult(), "")  # Si no hay insultos, devuelve cadena vacía

if __name__ == "__main__":
    unittest.main()
