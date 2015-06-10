# -*- coding: utf-8 -*-
# Module: main
# Author: Roman V.M.
# Created on: 13.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from simpleplugin import Plugin
from libs import actions

plugin = Plugin()
plugin.actions['root'] = actions.root
plugin.actions['episode_list'] = actions.episode_list
plugin.actions['search_episodes'] = actions.search_episodes
plugin.actions['episode'] = actions.episode
plugin.actions['my_shows'] = actions.my_shows
if __name__ == '__main__':
    plugin.run(content='tvshows')
