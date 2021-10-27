import os
import re
import requests
from urllib.request import urlopen


def get_urls_ps(html):
    """
    :param html: html of each page to parse.
    :return: all urls and ps(numbers of pictures), both in list.
    """
    pattern = re.compile(r'https://tjg\.gzhuibei\.com/a/1/\d*/0\.jpg.{34,44}P', re.DOTALL)
    urls = []
    ps = []
    strings = pattern.findall(html)
    for string in strings:
        end = string.find('0.jpg')
        urls.append(string[:end] + '{}.jpg')
        start = string.find('liang">')
        ps.append(string[start + 7:-1])
    # print(len(urls), 'urls')
    # print(len(ps), 'ps')
    return urls, ps


def get_album_titles(html, num_plus_model=False):
    """
    :param html: html of each page to parse.
    :param site: old or new site.
    :return: all album titles in list.
    """
    pattern = re.compile(r'"biaoti"><a href="https://www.tujigu.net/.*</a></p>')
    titles = []
    numbers = []
    strings = pattern.findall(html)
    for string in strings:
        start = string.find('blank">')
        end = string.find('</a></p>')
        titles.append(string[start + 7:end])
        num_pattern = re.compile(r'No.{0,3}\d{1,5}', flags=re.I)
        try:
            number = re.search(num_pattern, string).group()
        except:
            number = 'null'
        numbers.append(number)
    # print(len(titles), 'titles')
    if num_plus_model:
        num_names = []
        names = get_model_names(html)
        for name, number in zip(names, numbers):
            num_names.append(number + ' - ' + name)
        return num_names
    else:
        return titles


def get_model_names(html):
    """
    :param html: html of each page to parse.
    :return: all model names in list.
    """
    names = []
    pattern = re.compile(r'模特.*\n.*blank">.*</a>|<p>模特：\n.*</p>')
    strings = pattern.findall(html)
    for string in strings:
        if string.endswith('</p>'):
            start = string.find('\n')
            end = string.find('</p')
            ch = string[start + 1:end]
        elif string.endswith('</a>'):
            start = string.find('blank">')
            end = string.find('</a>')
            ch = string[start + 7:end]
        if len(ch) > 4 and ch[0:4] == '克拉女神':
            ch = ch[4:]
        names.append(''.join(ch))
    # print(len(names), 'names')
    return names


def get_all_info(root_html, s_page, e_page, mode='model', api='requests', num_plus_model=False):
    """
    :param root_html: html of the first page of the photo agency.
    :param s_page: the starting page index to download.
    :param e_page: the ending page index to download.
    :param mode: use model name or album title as folder names.
    :param api: requests or urlopen API.
    :return: info like [(url1, p1, name1),(url2, p2, name2),...](tuple in list).
    """
    urls = []
    ps = []
    names = []
    titles = []
    all_info = []
    for i in range(s_page - 1, e_page):
        if i != 0:
            root_html = os.path.join(root_html, f'index_{i}.html')
        if api == 'requests':
            r = requests.get(root_html)
            r.encoding = 'utf-8'
            html = r.text
        elif api == 'urlopen':
            html = urlopen(root_html).read().decode()
        else:
            raise ValueError
        # f = open('F:\写真\info\question.txt','w')
        # print(html, file=f)
        url, p = get_urls_ps(html)
        name = get_model_names(html)
        title = get_album_titles(html, num_plus_model)
        urls.extend(url)
        ps.extend(p)
        names.extend(name)
        titles.extend(title)
    if mode == 'model':
        for pair in zip(urls, ps, names):
            all_info.append(pair)
    elif mode == 'title':
        for pair in zip(urls, ps, titles):
            all_info.append(pair)
    return all_info
