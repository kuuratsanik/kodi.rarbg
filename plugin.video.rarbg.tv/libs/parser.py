# -*- coding: utf-8 -*-
# Module: parser
# Author: Roman V.M.
# Created on: 15.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import re
# Additional modules
from bs4 import BeautifulSoup
# Custom modules
from webclient import anti_captcha
from addon import Addon, cached


__addon__ = Addon()

_LINKS = {'torrents': 'https://www.rarbg.to/torrents.php?',
          'tv_view': 'https://www.rarbg.to/tv/{0}/'}  # All seasons of a TV show


def _load_page(url, method='get', data=None):
    """
    Load web-page
    :param url: str - URL
    :return:
    """
    return anti_captcha(url, method, data)


@cached(15)
def load_episodes(page, search_query, imdb, quality=__addon__.quality):
    """
    Load recent episodes page and return a parsed list of episodes
    :return: dict
    """
    data = {'page': page}
    if imdb:
        data['imdb'] = imdb
    else:
        data['category[]'] = quality
        if search_query:
            data['search'] = search_query
    return _parse_episodes(_load_page(_LINKS['torrents'], data=data))


def _parse_episodes(html):
    """
    Parse the list of episodes
    :param html: str - html page
    :return: dict - episodes
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
            try:
                rating = re.search(r'(\d\.\d)/10', extra_info[1]).group(1)
            except IndexError:
                rating = None
        else:
            genre = rating = ''
        size = row.contents[-5].text
        seeders = row.contents[-4].text
        leechers = row.contents[-3].text
        episode_data = {'title': title, 'link': link, 'thumb': thumb, 'imdb': imdb, 'size': size, 'seeders': seeders,
                        'leechers': leechers,
                        'info': {'genre': genre}}
        if rating is not None:
            episode_data['info']['rating'] = float(rating)
        listing.append(episode_data)
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
    :param url: str - URL
    :return: dict - episode data
    """
    return _parse_episode_page(_load_page(url))


def _parse_episode_page(html):
    """
    Parse episode page
    :param html: str - html page
    :return: dict - episode data
    """
    soup = BeautifulSoup(html)
    filename = soup.h1.text
    ep_info_match = re.search(r'[Ss](\d+)[Ee](\d+)', soup.h1.text)
    if ep_info_match is None:
        ep_info_match = re.search(r'(\d+)[Xx](\d+)', soup.h1.text)
    season = ep_info_match.group(1) if ep_info_match is not None else None
    episode = ep_info_match.group(2) if ep_info_match is not None else None
    torrent_tag = soup.find('a', {'onmouseover': re.compile(r'Click here to download torrent')})
    torrent = 'https://www.rarbg.to'+ torrent_tag['href']
    magnet_tag = soup.find('a', {'href': re.compile(r'magnet')})
    magnet = magnet_tag['href']
    poster_tag = soup.find('img', {'itemprop': 'image', 'border': '0'})
    poster = 'http:' + poster_tag['src']
    title_tag = soup.find(text='Title:')
    title = re.sub(r' \(TV Series.+?\)', '', title_tag.next.text)
    rating_tag = soup.find(text='IMDB Rating:')
    rating = re.search(r'(\d\.\d)/10', rating_tag.next.text).group(1) if rating_tag is not None else None
    genres_tag = soup.find(text='Genres:')
    genres = genres_tag.next.text.replace(' ,', ',')
    actors_tag = soup.find(text='Actors:')
    actors = actors_tag.next.text.replace(' ,', ',')
    plot_tag = soup.find(text='Plot:')
    plot = plot_tag.next.text.replace('|', '')
    imdb_tag = soup.find('a', text=re.compile(r'imdb.com'))
    imdb = re.search(r'/(tt\d+?)/', imdb_tag.text).group(1)
    size_tag = soup.find(text=' Size:')
    size = size_tag.next.text
    peers_tag = soup.find(text='Peers:')
    peers_match = re.search('Seeders : (\d+) , Leechers : (\d+)', peers_tag.next.text)
    seeders = peers_match.group(1)
    leechers = peers_match.group(2)
    episode_data = {'filename': filename,
                    'torrent': torrent,
                    'magnet': magnet,
                    'poster': poster,
                    'imdb': imdb,
                    'size': size,
                    'seeders': seeders,
                    'leechers': leechers,
                    'info': {'title': title,
                             'genre': genres,
                             'cast': actors.split(', '),
                             'plot': plot}}
    if season is not None:
        episode_data['info']['season'] = int(season)
    if episode is not None:
        episode_data['info']['episode'] = int(episode)
    if rating is not None:
        episode_data['info']['rating'] = float(rating)
    return episode_data
