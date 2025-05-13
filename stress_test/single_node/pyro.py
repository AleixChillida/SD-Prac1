import time
import Pyro4

# Conexión a los servicios Pyro
insult_service = Pyro4.Proxy("PYRONAME:insult.service")
insult_filter = Pyro4.Proxy("PYRONAME:insult.filter.service")

# Número de solicitudes
NUM_REQUESTS = 1000
TEXT = "You are such a moron"

# Medir tiempo para InsultService
start = time.time()
for _ in range(NUM_REQUESTS):
    insult_service.add_insult("dummy")
end = time.time()
insult_service_duration = end - start
insult_service_throughput = NUM_REQUESTS / insult_service_duration

# Medir tiempo para InsultFilterService
start = time.time()
for _ in range(NUM_REQUESTS):
    insult_filter.filter_text(TEXT)
end = time.time()
insult_filter_duration = end - start
insult_filter_throughput = NUM_REQUESTS / insult_filter_duration

print(f"InsultSPyroSN: Tiempo: {insult_service_duration:.2f}s, Throughput: {insult_service_throughput:.2f} req/s")
print(f"InsultFServicePyroSN: Tiempo: {insult_filter_duration:.2f}s, Throughput: {insult_filter_throughput:.2f} req/s")
