# redis_consumer_worker.py
import redis
import time
import sys

def redis_consumer_worker():
    try:
        redis_client = redis.StrictRedis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True,
            socket_timeout=10,
            socket_keepalive=True
        )

        queue_name = "insult_queue"

        print(f"[Consumer] Started consuming from '{queue_name}'")

        while True:
            # BLPOP bloquea hasta que haya un mensaje o timeout
            result = redis_client.blpop(queue_name, timeout=5)
            if result is None:
                time.sleep(0.05)
                continue

            _, insult = result
            # procesamiento simulado
            # print(f"Consumed: {insult}")

    except KeyboardInterrupt:
        print("[Consumer] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"[Consumer ERROR] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    redis_consumer_worker()
