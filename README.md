# SD-Prac1

## Descripción del proyecto

Esta práctica tiene como objetivo implementar dos servicios distribuidos escalables: `InsultService` y `InsultFilter`, utilizando cuatro middlewares diferentes de comunicación: **XML-RPC**, **Pyro**, **Redis** y **RabbitMQ**.

Los servicios desarrollados permiten:

* Registrar insultos remotamente si no están ya almacenados
* Recuperar la lista de insultos
* Filtrar mensajes con insultos utilizando una cola de trabajo
* Difundir insultos aleatorios a suscriptores cada 5 segundos (solo `InsultService`)

Se incluye una carpeta de test para comprobar el funcionamiento de los servicios-

Se incluyen pruebas de rendimiento para tres escenarios:

* Escenario single-node
* Escalado estático con 1, 2 y 3 nodos
* Escalado dinámico según carga


## Requisitos

* Python 
* Redis Server
* RabbitMQ Server
* Módulos Python:

  * `xmlrpc`, `Pyro4`, `redis`, `pika`, `matplotlib`

## Ejecución de los servicios

### XML-RPC

python insult_service/xmlrpc_impl/xmlrpc_server.py 
python insult_filter/xmlrpc_impl/xmlrpc_server.py

### Pyro

pyro4-ns
python insult_service/pyro_impl/pyro_server.py 
python insult_filter/pyro_impl/pyro_server.py 

### Redis

python  insult_service/redis_impl/insult_consumer.py 
python  insult_filter/redis_impl/redis_server.py 

### RabbitMQ

python  insult_service/rabbitmq_impl/consumer_rabbitmq.py 
python  insult_filter/rabbitmq_impl/rabbitmq_server.py 

### Ejecución de tests de prueba 

Desde `tests/test_insult_filter` o `tests/test_insult_service`:

python test_xmlrpc.py
python test_pyro.py
python test_redis.py
python test_rabbitmq.py


## Ejecución de los servicios para probar stress test

### XML-RPC

python insult_service/xmlrpc_impl/xmlrpc_server3.py 8000
python insult_service/xmlrpc_impl/xmlrpc_server3.py 8001
python insult_service/xmlrpc_impl/xmlrpc_server3.py 8002

### Pyro

python insult_service/pyro_impl/pyro_server3.py insult.service.1 9090
python insult_service/pyro_impl/pyro_server3.py insult.service.2 9091
python insult_service/pyro_impl/pyro_server3.py insult.service.3 9092

### Redis

python insult_service/redis_impl/insult_consumer3.py insult_queue.0
python insult_service/redis_impl/insult_consumer3.py insult_queue.1
python insult_service/redis_impl/insult_consumer3.py insult_queue.2

### RabbitMQ

python insult_service/rabbitmq_impl/insult_consumer3.py insult_queue.1 insult_queue.2 insult_queue.3

## Ejecución de tests de rendimiento

Desde `stress_test/test`:

python xmlrpc_stest.py
python pyro_stest.py
python redis_stest.py
python rabbitmq_stest.py


Cada script mide:

* Tiempo total de ejecución
* Throughput (peticiones por segundo)
* Speedup comparando número de nodos


## Resultados

Los resultados se guardan y analizan mediante el script de grafico.py que genera la grafica_comparativa.png. 
