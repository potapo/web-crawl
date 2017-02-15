import aiohttp
import asyncio
from bs4 import BeautifulSoup
import random
import sys
from urllib.parse import urlparse, urlunparse, parse_qs


class HTTPOKError (Exception):
    """Base class for exceptions in this module."""
    pass


class CONTTOLONGError (Exception):
    """Base class for exceptions in this module."""
    pass


class crawl:
    def __init__ (self, target, headers, is_current = True):
        self.target = target
        self.task = []
        self.headers = headers
        self.conf = urlparse (target)
        self.page, self.url_hash = {}, {}
        self.param = []
        self.forbidden = []
        self.TOO_LONG = 2 * 1024 * 1024
        self.task.append (target)
        self.is_current = is_current
        self.loop = asyncio.get_event_loop ()
        self.scan = False
        pass

    def read (self, file):
        with open (file, "r") as f:
            for i in f.readlines ():
                self.task.append (self.target + i)

    def encodeKey (self, key):
        return key.replace ('\\', "\\\\").replace ("\$", "\\u0024").replace (".", "\\u002e")

    @property
    def first_name (self):
        return self._first_name



    def parseFromtext (self, content, task_url, resp_url):
        self.url_hash[resp_url], self.url_hash[task_url] = True, True
        url_list = []
        soup = BeautifulSoup (content, 'html.parser')
        weblist = [tag.get ('href') for tag in soup.find_all ('a')]
        for tag in weblist:
            result = urlparse (tag)
            if result.scheme != '' and result.scheme != 'http' and result.scheme != 'https': continue
            link = []
            link.append (self.conf.scheme if result.scheme == '' else result.scheme)
            link.append (self.conf.netloc if result.netloc == '' else result.netloc)
            if link[1] != self.conf.netloc and self.is_current: continue
            link.append (self.conf.path if result.path == '' else result.path)
            link.extend (result[3:])
            link = urlunparse (link)
            if link not in self.url_hash:
                self.url_hash[link] = False
                self.task.append (link)
            param = parse_qs (result.query).keys ()
            query = ''.join ([i for i in sorted (param)])
            if result.path + query not in self.page.keys ():
                self.page[result.path + query] = link
        return url_list

    async def fetch (self, client, task_url):
        url_list = []
        await asyncio.sleep (random.randrange (0, 4) + random.random ())
        try:
            async with client.get (task_url, compress=True, timeout=5, allow_redirects=False) as resp:
                try:
                    if resp.status != 200:
                        raise HTTPOKError
                    else:
                        if "text/html" in resp.headers['Content-Type']: pass
                    if not self.scan:
                        url_list = self.parseFromtext (await resp.text (), task_url, resp.url)
                except KeyError:
                    print ('key not in dict')
                except UnicodeDecodeError:
                    print ("found unsupport character ,closing...")
                except HTTPOKError:
                    if resp.status == 403: self.forbidden.append (resp.url)
                except CONTTOLONGError:
                    print ('content-length is too long ,closing...')
                else:
                    print (task_url)
                    self.param.append (task_url)
                finally:
                    pass
        except asyncio.TimeoutError:
            print ('timeout,closing...')
        except aiohttp.errors.ClientOSError:
            print ("Certificate verify failed or other error")
        except (ConnectionResetError, aiohttp.errors.ServerDisconnectedError, aiohttp.errors.ClientResponseError):
            print ("Connection reset by peer")
            sys.exit (1)
        finally:
            self.task.extend (url_list)

    def run (self):
        with aiohttp.ClientSession (loop=self.loop, headers=self.headers) as client:
            while len (self.task) > 0:
                u = []
                curr, self.task = self.task[0:1000], self.task[1000:len (self.task)]
                while len (curr) > 0:
                    url = curr.pop ()
                    if url in self.url_hash.keys () and self.url_hash.get (url): continue
                    u.append (self.fetch (client, url))
                if len (u) <= 0: break
                self.loop.run_until_complete (asyncio.wait (u))
        self.loop.close ()
        print ("done")
        return self.param, self.forbidden, self.page

    def webscan (self, file):
        self.read (file)
        self.scan = True
        return self.run ()
