# -*- coding: utf-8 -*-
# Module: webclient
# Author: Roman V.M.
# Created on: 15.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import sys
import os
import codecs
from unittest import TestCase
from mock import MagicMock

cwd = os.path.dirname(os.path.abspath(__file__))
test_data = os.path.join(cwd, 'test_data')
sys.path.append(os.path.join(os.path.dirname(cwd), 'plugin.video.rarbg.tv'))

from libs.exceptions import NoDataError

mock_load_page = MagicMock()
mock_utilities = MagicMock()
mock_utilities.load_page = mock_load_page
sys.modules['libs.utilities'] = mock_utilities

from libs.tvdb import get_series


class TVDBTestCase(TestCase):
    def test_get_series(self):
        with codecs.open(os.path.join(test_data, 'get_series.xml'), encoding='utf-8', mode='rb') as fileobj:
            xml_data = fileobj.read()
        mock_load_page.return_value = xml_data
        result = get_series('82607')
        print result
        self.assertEqual(result['SeriesName'], 'Castle')
