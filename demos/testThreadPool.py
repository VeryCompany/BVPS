import urllib2
from multiprocessing.dummy import Pool as ThreadPool

urls = [
  'http://www.baidu.com',
  'http://www.sina.com.cn'
  # etc..
  ]

# Make the Pool of workers
pool = ThreadPool(4)
# Open the urls in their own threads
# and return the results
results = pool.map(urllib2.urlopen, urls)
#close the pool and wait for the work to finish
pool.close()
pool.join()


print results
