
import time
from client import Client

FILE_PATH = "C:\\Users\inbal\Desktop\semester 2\security_course\in.txt"

def benchmarks(client, req_num):
    """
    throughput = requests/sec
    latency = time to complete a request
    """
    # calculate throughput
    start = time.time()
    for i in range(req_num // 3):
        client.upload_file(FILE_PATH, 'file')
        file, real_size = client.get_file('file')
        client.delete_file('file')
    end = time.time()
    throughput = req_num / (end - start)

    # calculate latency
    start = time.time()
    client.upload_file(FILE_PATH, 'file')
    end = time.time()
    latency = end - start
    client.delete_file('file')

    return throughput, latency

if __name__ == '__main__':
    with open('benchmarks2.txt', 'w') as f:
        pass

    req_num_arr = [15, 30, 60, 150, 210]
    N = 128  # 2, 4, 8, 16, 32, 64  # N is the number of leaves (files)
    throughput_arr = []
    latency_arr = []

    client = Client(N)
    for r in req_num_arr:
        throughput, latency = benchmarks(client, r)
        throughput_arr.append(throughput)
        latency_arr.append(latency)
        # download the current data
        with open('benchmarks.txt', 'a') as f:
            f.write(f'throughput = {throughput}, latency = {latency}, N = {N}, req_num = {r}\n')
        print("--------------------------------------------------------------------------------------")
    client.close_connection()




