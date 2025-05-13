import time
import Pyro4

# Conectar a varios servidores Pyro (supongamos que tienes 3 servidores ejecutándose)
insult_service_1 = Pyro4.Proxy("PYRONAME:insult.service.1")
insult_service_2 = Pyro4.Proxy("PYRONAME:insult.service.2")
insult_service_3 = Pyro4.Proxy("PYRONAME:insult.service.3")

insult_filter_1 = Pyro4.Proxy("PYRONAME:insult.filter.service.1")
insult_filter_2 = Pyro4.Proxy("PYRONAME:insult.filter.service.2")
insult_filter_3 = Pyro4.Proxy("PYRONAME:insult.filter.service.3")

# Número de solicitudes
NUM_REQUESTS = 1000
TEXT = "You are such a moron"

# Medir tiempo para InsultService (distribuido en 3 nodos)
start = time.time()
for i in range(NUM_REQUESTS):
    if i % 3 == 0:
        insult_service_1.add_insult("dummy")
    elif i % 3 == 1:
        insult_service_2.add_insult("dummy")
    else:
        insult_service_3.add_insult("dummy")
end = time.time()
insult_service_duration = end - start
insult_service_throughput = NUM_REQUESTS / insult_service_duration

# Medir tiempo para InsultFilterService (distribuido en 3 nodos)
start = time.time()
for i in range(NUM_REQUESTS):
    if i % 3 == 0:
        insult_filter_1.filter_text(TEXT)
    elif i % 3 == 1:
        insult_filter_2.filter_text(TEXT)
    else:
        insult_filter_3.filter_text(TEXT)
end = time.time()
insult_filter_duration = end - start
insult_filter_throughput = NUM_REQUESTS / insult_filter_duration

# Mostrar resultados
print(f"InsultService 3 Nodes: Tiempo: {insult_service_duration:.2f}s, Throughput: {insult_service_throughput:.2f} req/s")
print(f"InsultFilterService 3 Nodes: Tiempo: {insult_filter_duration:.2f}s, Throughput: {insult_filter_throughput:.2f} req/s")
