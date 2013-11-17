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

    def make_api_result(self, xml_path):
        return make_api_result(xml_path)


class _TestFileAPI(evelink_api.API):

    _result_set = 'raw-1'

    def __init__(self, *a, **kw):
        super(_TestFileAPI, self).__init__(*a, **kw)
        self.get_params = []

    def _get(self, path, params=None):
        self.get_params.append(params)
        xml_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'xml', self._result_set)
        with open(os.path.join(xml_dir, path + '.xml')) as f:
            return ElementTree.parse(f)


class TestFileAPITestCase(unittest.TestCase):

    test_cls_a = ()
    test_cls_kw = {}

    default_get_params = None

    def setUp(self):
        super(TestFileAPITestCase, self).setUp()
        self.api_old = _TestFileAPI(default_result_key='result')
        self.api = _TestFileAPI(default_result_key=None)

        self.instance_old = self.test_cls(api=self.api_old,
            *self.test_cls_a, **self.test_cls_kw)
        self.instance = self.test_cls(api=self.api,
            *self.test_cls_a, **self.test_cls_kw)

    def assertBothCallsEqual(self,
            unbound_test_cls_method, a=(), kw={}, result=None):
        self.assertEqual(
            unbound_test_cls_method(self.instance_old, *a, **kw),
            result)
        self.assertEqual(
            unbound_test_cls_method(self.instance, *a, **kw).get('result'),
            result)

    def assertGetBoth(self, unbound_test_cls_method, *a, **kw):
        old = unbound_test_cls_method(self.instance_old, *a, **kw)
        new = unbound_test_cls_method(self.instance, *a, **kw)
        self.assertEqual(old, new.get('result'))
        self.assertIn('current_time', new)
        self.assertIn('cached_until', new)

        if self.default_get_params and not (a or kw):
            self.assertIn(self.default_get_params, self.api_old.get_params)
            self.assertIn(self.default_get_params, self.api.get_params)

        return old
