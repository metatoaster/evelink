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
        api = evelink_api.API(default_result_key='result')
        self.api = mock.MagicMock(spec=evelink_api.API)
        self.api.format_result = evelink_api.default_result_formatter
        self.api.result_node = api.result_node

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
        self.api_old = _TestFileAPI(default_result_key='result')
        self.api = _TestFileAPI(default_result_key=None)

        self.instance_old = self.test_cls(self.api_old)
        self.instance = self.test_cls(self.api)

    def assertBothCallsEqual(self,
            unbound_test_cls_method, a=(), kw={}, result=None):
        self.assertEqual(
            unbound_test_cls_method(self.instance_old, *a, **kw),
            result)
        self.assertEqual(
            unbound_test_cls_method(self.instance, *a, **kw).get('result'),
            result)
