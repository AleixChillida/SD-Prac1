import time
import multiprocessing
import Pyro4

NUM_PROCESSES = 8
REQUESTS_PER_PROCESS = 100

def stress_test_process():
    ns = Pyro4.locateNS()
    uri = ns.lookup("insult.service")
    service = Pyro4.Proxy(uri)

    for i in range(REQUESTS_PER_PROCESS):
        insult = f"You are a fool #{i}!"
        service.add_insult(insult)

def main():
    print(f"Starting stress test with {NUM_PROCESSES} processes, {REQUESTS_PER_PROCESS} requests each...\n")

    start_time = time.time()

    processes = []
    for _ in range(NUM_PROCESSES):
        p = multiprocessing.Process(target=stress_test_process)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    end_time = time.time()
    total_time = end_time - start_time

    total_requests = NUM_PROCESSES * REQUESTS_PER_PROCESS
    throughput = total_requests / total_time

    print(f"Total requests: {total_requests}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time per process: {total_time:.2f} seconds")
    print(f"Requests per second (throughput): {throughput:.2f} req/s")

if __name__ == "__main__":
    main()
