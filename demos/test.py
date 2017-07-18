from multiprocessing.dummy import Pool as ThreadPool
def aaa(n):
    return n**3
def squareNumber(n):
    numbers = [1, 2, 3, 4, 5]
    squaredNumbers = calculateParallel(aaa,numbers, 4)
    for n in squaredNumbers:
        print(n)
    return n ** 2

# function to be mapped over
def calculateParallel(method,numbers, threads=2):
    pool = ThreadPool(threads)
    results = pool.map(method, numbers)
    pool.close()
    pool.join()
    return results

if __name__ == "__main__":
    numbers = [1, 2, 3, 4, 5]
    squaredNumbers = calculateParallel(squareNumber,numbers, 2)
    for n in squaredNumbers:
        print(n)
