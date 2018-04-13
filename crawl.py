import requests
import urllib.parse
#import queue
import multiprocessing
import sys
from bs4 import BeautifulSoup
from bs4.element import Comment

workers = 2
writers = 1
depth = 2


# simple skeleman to show how to get work from the queue
def worker(q_in, s, lock):
    print('worker')
    # Do work while queue has stuff
    while True:
        depth, url = q_in.get(timeout=5)

        if depth == 0:
            continue
        if url is None:
            break

        print('lock')
        lock.acquire()
        stale_url = url in s
        if not stale_url:
            s.add(url)
        lock.release()
        print('unlock')

        if not stale_url:
            s.add(url)
            print(url)
            try:
                page = requests.get(url)
                if page.ok and 'text/html' in page.headers['content-type']:
                    soup = BeautifulSoup(page.content, 'html.parser')
                    page_urls = get_urls(soup, url)
                    [q_in.put((depth - 1, u)) for u in page_urls]
                    page_text = text_from_soup(soup)
                    # TODO save page_urls to file
                    # TODO save text_from_soup


            except Exception as e:
                print('DEBUG exception in request')
                #print('DEBUG exception in request' + e)
        else:
            print('DEBUG duplicate: ' + url)

# Get urls in a page and return it as a list
def get_urls(soup, parent_url):
    urls = list()
    for url in soup.find_all('a', href=True):
        url_str = urllib.parse.urljoin(parent_url, url['href'])
        u_tuple = urllib.parse.urlsplit(url_str)
        url_str = u_tuple.scheme + '://' + u_tuple.netloc + u_tuple.path
        if u_tuple.scheme == 'http' or u_tuple.scheme == 'https':
            #print(url_str)
            urls.append(url_str)

    return urls

#DEBUG https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
# Strips the all the text from the HTML
def text_from_soup(soup):
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)

# Returns if a HTML tag is a visible element
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def main():
    # Initialize synchronization data structures
    q_in = multiprocessing.Queue()
    #q_out = multiprocessing.JoinableQueue()
    lock = multiprocessing.Lock()

    url = 'https://www.cs.utexas.edu/~ans/classes/cs439/schedule.html'
    s = set()
    s.add(url)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    page_urls = get_urls(soup, url)
    [q_in.put((depth, u)) for u in page_urls]
    #print(text_from_soup(soup))

    processes = list()
    for i in range(workers):
        p = multiprocessing.Process(target=worker, args=(q_in, s, lock,))
        processes.append(p)
        processes[i].start()


    # signal all processes to stop and join them
    for i in range(workers):
        print('joined: ' + i)
        processes[i].join()

if __name__ == '__main__':
    main()
