# coding=utf-8

# Module for work with mysql database
import MySQLdb

# The urllib2 module defines functions and classes which help in opening URLs (mostly HTTP)
# in a complex world a basic and digest authentication, redirections, cookies and more.
import urllib2

# Import BeautifulSoup for parse html data
from bs4 import BeautifulSoup

# Import time to know time spent
import time

import sys

reload(sys)

# Link base to make the webcrawler
link_base = 'http://www9.prefeitura.sp.gov.br'
link_page = link_base + '/secretarias/smads/estouaqui/pessoas/todos/page:'

# Headers for browser
headers = {'User-Agent': 'GoogleBot'}


def run_request(link):
    """
    Iterate the next 10 pages to get the links and call the function to
    get the data child

    :param link:
    :return:
    """

    global link_page

    if link is None:
        return

    for i in xrange(1, 11):
        soup = get_html(link_page + str(i))

        if soup is None:
            return

        people_list = soup.find(attrs={'id': 'lista_pessoas'})

        for people in people_list.findAll(attrs={'class': 'pessoa'}):
            if people is None:
                continue

            people_data = people.find(attrs={'class': 'pessoa_dados'})

            if people_data is None:
                return

            link = people_data.h3.a.get('href')

            get_data_child(link_base + link)


def get_data_child(link):
    """
    Get the data of link

    :param link:
    :return:
    """

    soup = get_html(link)

    if soup is None:
        return

    data = soup.find(attrs={'id': 'conteudo'})
    name = data.h2.text
    address = ''
    district = ''
    phone = ''
    email = ''

    count = 1

    # Conection with database
    conn = connect_db()
    conn.autocommit(False)
    cur = conn.cursor()

    # String for insert into database webcrawler_python, table people, the data crawled from the link
    insert = "INSERT INTO people (name, address, district, phone, email) VALUES ('%s', '%s','%s', '%s', '%s')"

    for p in data.find(attrs={'class': 'entidade_dados'}).findAll('p'):

        if count == 1:
            address = p.text.split(':')[1][1:]
        elif count == 2:
            district = p.text.split(':')[1][1:]
        elif count == 3:
            phone = p.text.split(':')[1][1:]
        elif count == 5:
            email = p.text.split(':')[1][1:]

        count += 1

    # Bind the parameters and make the insert
    insert %= (name, address, district, phone, email)
    cur.execute(insert)
    conn.commit()

    print name


def connect_db():
    """
    Settings for connect to the database
    :return:
    """

    return MySQLdb.connect(host='localhost', user='root', passwd='', db='webcrawler_python')


def get_html(link):
    """
    Make the web request for parsing data
    :param link:
    :return:
    """

    request = urllib2.Request(link, headers=headers)
    return BeautifulSoup(urllib2.urlopen(request), 'html.parser')


if __name__ == '__main__':
    begin = time.time()
    run_request(link_base + '/secretarias/smads/estouaqui/pessoas/todos')
    end = time.time()
    print '\nTotal: ', (end - begin)
