# -*- coding: utf-8 -*-
# Module: parser
# Author: Roman V.M.
# Created on: 15.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import re
# Additional modules
from bs4 import BeautifulSoup
# Custom modules
from webclient import load_page
from addon import Addon, cached
from anticaptcha import anticaptcha


__addon__ = Addon()

_LINKS = {'episodes': 'https://www.rarbg.to/torrents.php?{0}&page={1}',
          'imdb_view': 'https://www.rarbg.to/torrents.php?imdb={0}&page={1}',  # Recent episodes for a TV show
          'tv_view': 'https://www.rarbg.to/tv/{0}/'}  # All seasons of a TV show


@anticaptcha
def _load_page(url, method='get', data=None):
    """
    Load web-page
    :param url: str - URL
    :return:
    """
    return load_page(url, method, data)


@cached(15)
def load_episodes(page, search_query, imdb):
    """
    Load recent episodes page and return a parsed list of episodes
    :return: dict
    """
    if imdb:
        url = _LINKS['imdb_view'].format(imdb, page)
    else:
        url = _LINKS['episodes'].format(__addon__.quality, page)
        if search_query:
            url += '&search={0}'.format(search_query)
    return _parse_episodes(_load_page(url))


def _parse_episodes(html):
    """
    Parse the list of episodes
    :param html: str
    :return: dict
    """
    soup = BeautifulSoup(html)
    episode_rows = soup.find_all('tr', {'class': 'lista2'})
    listing = []
    for row in episode_rows:
        imdb_tag = row.find('a', {'href': re.compile(r'/tv/tt(\d+?)')})
        if imdb_tag is not None:
            imdb = imdb_tag['href'][4:-1]
        else:
            continue
        title_tag = row.find('a', {'onmouseover': True, 'onmouseout': True})
        title = title_tag.text
        link = 'http://www.rarbg.to' + title_tag['href']
        thumb = 'http:' + re.search(r'<img src=\\\'(.+?)\\\'', title_tag['onmouseover']).group(1)
        extra_info_tag = row.find('span', {'style': 'color:DarkSlateGray'})
        if extra_info_tag is not None:
            extra_info = extra_info_tag.text.split(' IMDB: ')
            genre = extra_info[0]
            rating = re.search(r'(\d\.\d)/10', extra_info[1]).group(1)
        else:
            genre = rating = ''
        listing.append({'title': title, 'link': link, 'thumb': thumb,
                        'info': {'genre': genre, 'rating': float(rating), 'imdb': imdb}})
    episodes = {'episodes': listing}
    prev_page_tag = soup.find('a', {'title': 'previous page'})
    if prev_page_tag is not None:
        prev_page = re.search(r'page=(\d+)', prev_page_tag['href']).group(1)
    else:
        prev_page = ''
    episodes['prev'] = prev_page
    next_page_tag = soup.find('a', {'title': 'next page'})
    if next_page_tag is not None:
        next_page = re.search(r'page=(\d+)', next_page_tag['href']).group(1)
    else:
        next_page = ''
    episodes['next'] = next_page
    return episodes


@cached(60)
def load_episode_page(url):
    """
    Load episode page and return parsed data
    :param url:
    :return: dict
    """
    return _parse_episode_page(_load_page(url))


def _parse_episode_page(html):
    """
    Parse episode page
    :param html: str
    :return: dict
    """
    soup = BeautifulSoup(html)
    filename = soup.h1.text
    ep_info_match = re.search(r'[Ss](\d+)[Ee](\d+)', soup.h1.text)
    if ep_info_match is not None:
        season = ep_info_match.group(1)
        episode = ep_info_match.group(2)
    else:
        season = ''
        episode = ''
    torrent_tag = soup.find('a', {'onmouseover': re.compile(r'Click here to download torrent')})
    torrent = 'https://www.rarbg.to'+ torrent_tag['href']
    magnet_tag = soup.find('a', {'href': re.compile(r'magnet')})
    magnet = magnet_tag['href']
    poster_tag = soup.find('img', {'itemprop': 'image', 'border': '0'})
    poster = 'http:' + poster_tag['src']
    title_tag = soup.find(text='Title:')
    title = re.sub(r' \(TV Series.+?\)', '', title_tag.next.text)
    rating_tag = soup.find(text='IMDB Rating:')
    rating = re.search(r'(\d\.\d)/10', rating_tag.next.text).group(1)
    genres_tag = soup.find(text='Genres:')
    genres = genres_tag.next.text.replace(' ,', ',')
    actors_tag = soup.find(text='Actors:')
    actors = actors_tag.next.text.replace(' ,', ',')
    plot_tag = soup.find(text='Plot:')
    plot = plot_tag.next.text.replace('|', '')
    imdb_tag = soup.find('a', text=re.compile(r'imdb.com'))
    imdb = re.search(r'/(tt\d+?)/', imdb_tag.text).group(1)
    episode_data = {'filename': filename,
                    'torrent': torrent,
                    'magnet': magnet,
                    'poster': poster,
                    'imdb': imdb,
                    'info': {'title': title,
                             'rating': float(rating),
                             'genre': genres,
                             'cast': actors.split(', '),
                             'plot': plot}}
    if season:
        episode_data['info']['season'] = int(season)
    if episode:
        episode_data['info']['episode'] = int(episode)
    return episode_data
