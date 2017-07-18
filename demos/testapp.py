from multiprocessing.dummy import Pool as ThreadPool
from collections import deque
def aaa(n):
    return [n**2]
def squareNumber(n):
    numbers = [1, 2, 3, 4, 5]
    squaredNumbers = calculateParallel(aaa,numbers, 4)
    squaredNumbers2 = calculateParallel(aaa,numbers*5, 4)
    for n in squaredNumbers:
        print(n[0])
    for n in squaredNumbers2:
        print(n[0])
    return squaredNumbers

# function to be mapped over
def calculateParallel(method,numbers, threads=2):
    pool = ThreadPool(threads)
    results = pool.map(method, numbers)
    pool.close()
    pool.join()
    return results

if __name__ == "__main__":
    tn=4
    pool = ThreadPool(processes=tn)
    pending = deque()
    num=0
    while True:
        while len(pending) > 0 and pending[0].ready():
            a = pending.popleft().get()
        if len(pending) < tn and num < 10:
            task = pool.apply_async(squareNumber,[num])
            pending.append(task)
        if num > 10:
            pool.close()
            pool.join()
            break
        num +=1
