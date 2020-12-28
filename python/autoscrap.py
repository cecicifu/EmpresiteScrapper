#!/usr/bin/python3
# coding: utf-8

import requests
import signal
import threading
import sys
import bs4
from time import sleep

# GLOBAL VARS
url = "https://empresite.eleconomista.es/Actividad/"
search = None
timeout = 2

parent_element_filter = "li.resultado_pagina"
page_number_element_filter = "ul.pagination01 li"
href_element_filter = ".article03-content a"
name_element_filter = "#datos-externos1 p.title02b"
email_element_filter = "span.email"
phone_element_filter = "span.tel"

s = requests.Session()
s.headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 "
                  "Safari/537.36",
}
# FREE SSL PROXIES https://www.sslproxies.org/
s.proxies = {
    "https://185.110.96.11:3128",
    "https://185.110.96.12:3128",
    "https://78.46.81.7:1080",
    "https://51.255.103.170:3129",
    "https://188.40.183.189:1080",
    "https://188.165.141.114:3129",
}


class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


if len(sys.argv) != 2:
    print("\n" + Colors.OKGREEN + "[" + Colors.ENDC + Colors.OKBLUE + "*" + Colors.OKGREEN +
          "] Usage:" + Colors.ENDC + " py " + sys.argv[0] + " <search>")
    sys.exit(0)
else:
    search = sys.argv[1].upper()
    url = url + search + "/"


def signal_handler():
    print("\n" + Colors.OKGREEN + "[" + Colors.ENDC + Colors.OKBLUE + "*" + Colors.OKGREEN +
          "] Exiting...\n")
    exit(1)


signal.signal(signal.SIGINT, signal_handler)


def execute():
    try:
        pages = get_num_pages()

        print(Colors.OKGREEN +
              "\n" + Colors.OKGREEN + "[" + Colors.ENDC + Colors.OKBLUE + "*" + Colors.OKGREEN +
              "] Total number of pages:" + Colors.ENDC, len(pages[1:]))

        hrefs = get_hrefs(pages)

        print(Colors.OKGREEN +
              "\n" + Colors.OKGREEN + "[" + Colors.ENDC + Colors.OKBLUE + "*" + Colors.OKGREEN +
              "] Total of pages:" + Colors.ENDC, len(hrefs))

        data = get_filtered_data(hrefs)

        print("\n" + Colors.OKGREEN + "\n" + Colors.OKGREEN + "[" + Colors.ENDC + Colors.OKBLUE + "*" +
              Colors.OKGREEN + "] DATA:\n" + Colors.ENDC, data)

    except requests.exceptions.Timeout:
        print("\n" + Colors.OKGREEN + "[" + Colors.ENDC + Colors.OKBLUE + "*" + Colors.OKGREEN +
              "] Timeout exception\n")
    except requests.exceptions.TooManyRedirects:
        print("\n" + Colors.OKGREEN + "[" + Colors.ENDC + Colors.OKBLUE + "*" + Colors.OKGREEN +
              "] Too many redirects exception\n")
    except Exception as err:
        print("\n" + Colors.OKGREEN + "[" + Colors.ENDC + Colors.OKBLUE + "*" + Colors.OKGREEN +
              "]", str(err), "\n")


def get_filtered_data(hrefs):
    data = []
    for href in hrefs:
        r = s.get(href)
        content = bs4.BeautifulSoup(r.content, "html.parser")

        d = dict()
        if content.select_one(name_element_filter) is not None:
            d["name"] = content.select_one(name_element_filter).text
        else:
            d["name"] = "null"

        if content.select_one(email_element_filter) is not None:
            d["email"] = content.select_one(email_element_filter).text
        else:
            d["email"] = "null"

        if content.select_one(phone_element_filter) is not None:
            d["phone"] = content.select_one(phone_element_filter).text
        else:
            d["phone"] = "null"

        data.append(d)
        sleep(timeout)

    return data


def get_hrefs(pages):
    hrefs = []
    for page in pages:
        r = s.get(page)

        content = bs4.BeautifulSoup(r.content, "html.parser")
        rows = content.select(parent_element_filter)

        for row in rows:
            hrefs.append(row.select_one(href_element_filter)["href"])

    return hrefs


def get_num_pages():
    r = s.get(url)

    content = bs4.BeautifulSoup(r.content, "html.parser")

    page_nums = content.select(page_number_element_filter)

    pages = [url]
    for page_num in page_nums[1:]:
        pages.append(page_num.select_one("a")["href"])

    return pages


if __name__ == "__main__":
    try:
        threading.Thread(target=execute).start()
    except Exception as e:
        print("\n" + Colors.OKGREEN + "[" + Colors.ENDC + Colors.OKBLUE + "*" + Colors.OKGREEN +
              "]", str(e), "\n")
