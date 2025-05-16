import pika
import threading
import sys
import time

def consume_queue(queue_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=queue_name)

    def callback(ch, method, properties, body):
        insult = body.decode()

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print(f"Waiting for insults on {queue_name}. Press CTRL+C to exit.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"Stopped consumer for {queue_name}")
        channel.stop_consuming()
    finally:
        connection.close()

def main(queues):
    threads = []
    for qname in queues:
        t = threading.Thread(target=consume_queue, args=(qname,), daemon=True)
        t.start()
        threads.append(t)

    print(f"Started consumers for queues: {', '.join(queues)}. Waiting for messages...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping all consumers.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python consumer.py <cola1> [<cola2> ... <colaN>]")
        sys.exit(1)

    queues = sys.argv[1:]
    main(queues)
