import aiohttp
import asyncio
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse, urlunparse
from cos_dist import cos_dist
from pymongo import MongoClient

client = MongoClient('mooder.f4ck0.com', 27017)
db = client.crawl
db.authenticate("dba", "dba")
handle = db.get_collection("web")

url = "http://www.cnhongke.org/"
conf = urlparse(url)
is_current = True
page = {}
digest = {}
http_200 = {}
http_403 = {}
param = []
url_hash = {}
TOO_LONG = 2 * 1024 * 1024
useragent = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}


class HTTPOKError(Exception):
    """Base class for exceptions in this module."""
    pass


class CONTTOLONGError(Exception):
    """Base class for exceptions in this module."""
    pass


def encodeKey(key):
    return key.replace('\\', "\\\\").replace("\$", "\\u0024").replace(".", "\\u002e")


def parseFromtext(content, task_url, resp_url):
    url_hash[resp_url], url_hash[task_url], http_200[resp_url] = True, True, True
    handle.insert({encodeKey(task_url): content})
    url_list = []
    soup = BeautifulSoup(content, 'html.parser')
    a_list = [tag.get('href') for tag in soup.find_all('a')]
    for tag in a_list:
        result = urlparse(tag)
        if result.scheme != '' and result.scheme != 'http' and result.scheme != 'https': continue
        link = []
        link.append(conf.scheme if result.scheme == '' else result.scheme)
        link.append(conf.netloc if result.netloc == '' else result.netloc)
        if link[1] != conf.netloc and is_current: continue
        link.append(conf.path if result.path == '' else result.path)
        link.extend(result[3:])
        link = urlunparse(link)
        if link not in url_hash.keys(): url_hash[link] = False
        if result.path not in page.keys():
            page[result.path] = link
            url_list.append(link)
        else:
            if cos_dist(link, page[result.path]) < 0.7:
                url_list.append(link)
    return url_list


async def fetch(client, task_url):
    url_list = []
    await asyncio.sleep(0.5)
    try:
        async with client.get(task_url, headers=useragent, timeout=2, allow_redirects=False) as resp:
            try:
                if resp.status != 200: raise HTTPOKError
                if 'content-length' in resp.headers.keys() and int(resp.headers['content-length']) > TOO_LONG:
                    raise CONTTOLONGError
                else:
                    if "text/html" in resp.headers['Content-Type']: pass
                url_list = parseFromtext(await resp.text(), task_url, resp.url)
                print(task_url)
                param.append(task_url)
            except KeyError:
                print('key not in dict')
            except UnicodeDecodeError:
                print("found unsupport character ,closing...")
            except HTTPOKError:
                print("response not 200,closing")
            except CONTTOLONGError:
                print('content-length is too long ,closing...')
            finally:
                resp.close()
    except asyncio.TimeoutError:
        print('timeout,closing...')
    except aiohttp.errors.ClientOSError:
        print("ertificate verify failed")
    finally:
        return url_list


async def main(loop, url):
    task = [url]
    async with aiohttp.ClientSession(loop=loop) as client:
        while len(task) > 0:
            task_url = task.pop()
            if task_url in url_hash.keys() and url_hash.get(task_url): continue
            task.extend(await fetch(client, task_url))


try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop, url))
except KeyboardInterrupt:
    pass
finally:
    print("well done")
    with open('crawl.txt', "w") as f:
        for i in param:
            f.writelines(i + os.linesep)
