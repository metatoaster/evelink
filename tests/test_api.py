import unittest2 as unittest

from xml.etree import ElementTree

import evelink.api as evelink_api

class HelperTestCase(unittest.TestCase):

    def test_parse_ts(self):
        self.assertEqual(
            evelink_api.parse_ts("2012-06-12 12:04:33"),
            1339502673,
        )

class CacheTestCase(unittest.TestCase):

    def setUp(self):
        self.cache = evelink_api.APICache()

    def test_cache(self):
        self.cache.put('foo', 'bar', 3600)
        self.assertEqual(self.cache.get('foo'), 'bar')

    def test_expire(self):
        self.cache.put('baz', 'qux', -1)
        self.assertEqual(self.cache.get('baz'), None)


class DefaultResultFormatterTestCase(unittest.TestCase):

    def setUp(self):
        self.test_xml = r"""
                <?xml version='1.0' encoding='UTF-8'?>
                <eveapi version="2">
                    <currentTime>2009-10-18 17:05:31</currentTime>
                    <result>
                        <rowset>
                            <row foo="bar" />
                            <row foo="baz" />
                        </rowset>
                    </result>
                    <cachedUntil>2009-11-18 17:05:31</cachedUntil>
                </eveapi>
            """.strip()
        self.tree = ElementTree.fromstring(self.test_xml)

    def test_format_tree(self):
        r = 'bar'
        result = evelink_api.default_result_formatter(self.tree, r)
        answer = {
            'result': 'bar',
            'current_time': 1255885531,
            'cached_until': 1258563931,
        }

        self.assertEqual(result, answer)
        result1, reform = evelink_api.default_result_formatter.unformat(result)
        self.assertEqual('bar', result1)
        result2 = reform(result1)
        self.assertEqual(result2, answer)
        result3 = reform('something else')
        self.assertEqual(result3['result'], 'something else')

    def test_format_result(self):
        r = 'bar'
        result_tree = self.tree.find('result')
        result = evelink_api.default_result_formatter(result_tree, r)
        self.assertEqual(result, 'bar')
        result1, reform = evelink_api.default_result_formatter.unformat(result)
        self.assertEqual(result1, 'bar')

    def test_format_result_bad_tree(self):
        r = 'bar'
        result = evelink_api.default_result_formatter(None, r)
        self.assertEqual(result, 'bar')
        result1, reform = evelink_api.default_result_formatter.unformat(result)
        self.assertEqual(result1, 'bar')


if __name__ == "__main__":
    unittest.main()
