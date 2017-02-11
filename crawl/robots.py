import robotparser
from  urlparse import urlparse, urlunparse


def praser_robots(site):
    result = urlparse(site)
    if result.path != "robots.txt":
        result = list(result)
        result[2] = "/robots.txt"
        site = urlunparse(result)
    rp = robotparser.RobotFileParser()
    rp.set_url(site)
    rp.read()
    url = [j.path for i in rp.entries for j in i.rulelines]
    return list(set(url))


print praser_robots("http://www.cnhongke.org/robots.txt")
