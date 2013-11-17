import os
import unittest
from xml.etree import ElementTree

import mock

import evelink.api as evelink_api


def make_api_result(xml_path):
    xml_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xml')
    with open(os.path.join(xml_dir, xml_path)) as f:
        return ElementTree.parse(f)


class APITestCase(unittest.TestCase):
    def setUp(self):
        super(APITestCase, self).setUp()
        self.api = mock.MagicMock(spec=evelink_api.API)
        self.api.format_result = evelink_api.default_result_formatter

    def make_api_result(self, xml_path):
        return make_api_result(xml_path)


class _TestFileAPI(evelink_api.API):

    _result_set = 'raw-1'

    def _get(self, path, params=None):
        xml_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'xml', self._result_set)
        with open(os.path.join(xml_dir, path + '.xml')) as f:
            return ElementTree.parse(f)


class TestFileAPITestCase(unittest.TestCase):
    def setUp(self):
        super(TestFileAPITestCase, self).setUp()
        self.api = _TestFileAPI()

    def make_api_result(self, xml_path):
        return make_api_result(xml_path)
