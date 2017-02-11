# -*- coding: utf-8 -*-
from urlparse import urlparse, urlunparse
from bs4 import BeautifulSoup
import requests
from time import sleep
from threading import Thread
import logging
import os
from cos_dist import cos_dist

# logging.basicConfig(level=logging.INFO)
task = []
url_hash = {}
url = "http://ie.cidp.edu.cn/"
task.append(url)
conf = urlparse(url)
is_current = True
page = {}
digest = {}
http_200 = {}
http_403 = {}
param = []
TOO_LONG = 1024 * 1024
useragent = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}


class URLThread(Thread):
    def __init__(self, ):
        super(URLThread, self).__init__()

    def run(self):
        logging.debug("Thread is start " + self.getName())
        while True:
            if len(task) == 0:
                break
            try:

                task_url = task.pop()
                if task_url in url_hash.keys() and url_hash.get(task_url):
                    continue
                print task_url
                param.append(task_url)
                html_doc = requests.get(task_url, headers=useragent, timeout=5, allow_redirects=False, stream=True)
                if int(html_doc.headers['content-length']) > TOO_LONG:
                    html_doc.close()
                sleep(0.5)
                if html_doc.status_code != 200:
                    if html_doc.status_code == 403:
                        http_403[html_doc.url] = True
                        print "found  403", html_doc.url
                    continue
                url_hash[html_doc.url] = True
                url_hash[task_url] = True
                http_200[html_doc.url] = True
                content = html_doc.content
                html_doc.close()
                soup = BeautifulSoup(content, 'html.parser')
                a_list = [tag.get('href') for tag in soup.find_all('a')]
                for tag in a_list:
                    try:
                        result = urlparse(tag)
                        if result.scheme != '' and result.scheme != 'http' and result.scheme != 'https':
                            continue
                        link = []
                        link.append(conf.scheme if result.scheme == '' else result.scheme)
                        link.append(conf.netloc if result.netloc == '' else result.netloc)
                        if link[1] != conf.netloc and is_current:
                            continue
                        link.append(conf.path if result.path == '' else result.path)
                        [link.append(i) for i in result[3:]]
                        link = urlunparse(link)
                        if link not in url_hash.keys():
                            url_hash[link] = False
                        if result.path not in page.keys():
                            page[result.path] = True
                            # print("[path]\t" + result.path)
                            task.append(link)
                        else:
                            if cos_dist(link, page[link]) < 0.66666:
                                task.append(link)
                    except Exception, e:
                        e.message

            except Exception, e:
                e.message


if __name__ == '__main__':
    threads = [URLThread() for i in xrange(1)]
    for i in threads:
        i.start()
        # logging.warning(" new thread has been successful ")
        sleep(1)

    for i in threads:
        i.join()

    with open("crawl.txt", "w") as f:
        for i in param:
            f.writelines(i.encode('utf-8') + os.linesep)
