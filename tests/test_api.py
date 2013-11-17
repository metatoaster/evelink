from StringIO import StringIO
import unittest2 as unittest

import mock

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

class APITestCase(unittest.TestCase):

    def setUp(self):
        self.cache = mock.MagicMock(spec=evelink_api.APICache)
        self.api = evelink_api.API(cache=self.cache)
        # force disable requests if enabled.
        self._has_requests = evelink_api._has_requests
        evelink_api._has_requests = False

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

        self.error_xml = r"""
                <?xml version='1.0' encoding='UTF-8'?>
                <eveapi version="2">
                    <currentTime>2009-10-18 17:05:31</currentTime>
                    <error code="123">
                        Test error message.
                    </error>
                    <cachedUntil>2009-11-18 19:05:31</cachedUntil>
                </eveapi>
            """.strip()

    def tearDown(self):
        evelink_api._has_requests = self._has_requests

    def test_cache_key(self):
        assert self.api._cache_key('foo/bar', {})
        assert self.api._cache_key('foo/bar', {'baz': 'qux'})

        self.assertEqual(
            self.api._cache_key('foo/bar', {'a':1, 'b':2}),
            self.api._cache_key('foo/bar', {'b':2, 'a':1}),
        )

    def test_cache_key_variance(self):
        """Make sure that things which shouldn't have the same cache key don't."""
        self.assertNotEqual(
            self.api._cache_key('foo/bar', {'a':1}),
            self.api._cache_key('foo/bar', {'a':2}),
        )

        self.assertNotEqual(
            self.api._cache_key('foo/bar', {'a':1}),
            self.api._cache_key('foo/bar', {'b':1}),
        )

        self.assertNotEqual(
            self.api._cache_key('foo/bar', {}),
            self.api._cache_key('foo/baz', {}),
        )

    @mock.patch('urllib2.urlopen')
    def test_get(self, mock_urlopen):
        # mock up an urlopen compatible response object and pretend to have no
        # cached results; similar pattern for all test_get_* methods below.
        mock_urlopen.return_value = StringIO(self.test_xml)
        self.cache.get.return_value = None

        result = self.api.get('foo/Bar', {'a':[1,2,3]})

        rowset = result.find('rowset')
        rows = rowset.findall('row')
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].attrib['foo'], 'bar')
        self.assertEqual(self.api.last_timestamps, {
            'current_time': 1255885531,
            'cached_until': 1258563931,
        })

    @mock.patch('urllib2.urlopen')
    def test_get_result_key(self, mock_urlopen):
        # mock up an urlopen compatible response object and pretend to have no
        # cached results; similar pattern for all test_get_* methods below.
        mock_urlopen.return_value = StringIO(self.test_xml)
        self.cache.get.return_value = None

        tree = self.api.get('foo/Bar', {'a':[1,2,3]}, result_key='')
        result = tree.find('result')
        rowset = result.find('rowset')
        rows = rowset.findall('row')
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].attrib['foo'], 'bar')

    @mock.patch('urllib2.urlopen')
    def test_get_default_result_key(self, mock_urlopen):
        # mock up an urlopen compatible response object and pretend to have no
        # cached results; similar pattern for all test_get_* methods below.
        mock_urlopen.return_value = StringIO(self.test_xml)
        self.cache.get.return_value = None

        api = evelink_api.API(cache=self.cache, default_result_key=None)
        tree = api.get('foo/Bar', {'a':[1,2,3]})
        self.assertEqual(len(tree.findall('result')), 1)

        mock_urlopen.return_value = StringIO(self.test_xml)
        self.cache.get.return_value = None

        result = api.get('foo/Bar', {'a':[1,2,3]}, result_key='result')
        self.assertEqual(len(result.findall('result')), 0)
        self.assertEqual(len(result.findall('rowset')), 1)

    @mock.patch('urllib2.urlopen')
    def test_cached_get(self, mock_urlopen):
        """Make sure that we don't try to call the API if the result is cached."""
        # mock up a urlopen compatible error response, and pretend to have a
        # good test response cached.
        mock_urlopen.return_value = StringIO(self.error_xml)
        self.cache.get.return_value = self.test_xml

        result = self.api.get('foo/Bar', {'a':[1,2,3]})

        # Ensure this is really not called.
        self.assertFalse(mock_urlopen.called)

        rowset = result.find('rowset')
        rows = rowset.findall('row')
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].attrib['foo'], 'bar')

        # timestamp attempted to be extracted.
        self.assertEqual(self.api.last_timestamps, {
            'current_time': 1255885531,
            'cached_until': 1258563931,
        })

    @mock.patch('urllib2.urlopen')
    def test_get_with_apikey(self, mock_urlopen):
        mock_urlopen.return_value = StringIO(self.test_xml)
        self.cache.get.return_value = None

        api_key = (1, 'code')
        api = evelink_api.API(cache=self.cache, api_key=api_key)

        api.get('foo', {'a':[2,3,4]})

        # Make sure the api key id and verification code were passed
        self.assertEqual(mock_urlopen.mock_calls, [
                mock.call(
                    'https://api.eveonline.com/foo.xml.aspx',
                    'a=2%2C3%2C4&vCode=code&keyID=1',
                ),
            ])

    @mock.patch('urllib2.urlopen')
    def test_get_with_error(self, mock_urlopen):
        mock_urlopen.return_value = StringIO(self.error_xml)
        self.cache.get.return_value = None

        self.assertRaises(evelink_api.APIError,
            self.api.get, 'eve/Error')
        self.assertEqual(self.api.last_timestamps, {
            'current_time': 1255885531,
            'cached_until': 1258571131,
        })

    @mock.patch('urllib2.urlopen')
    def test_cached_get_with_error(self, mock_urlopen):
        """Make sure that we don't try to call the API if the result is cached."""
        # mocked response is good now, with the error response cached.
        mock_urlopen.return_value = StringIO(self.test_xml)
        self.cache.get.return_value = self.error_xml

        self.assertRaises(evelink_api.APIError,
            self.api.get, 'foo/Bar', {'a':[1,2,3]})

        self.assertFalse(mock_urlopen.called)
        self.assertEqual(self.api.last_timestamps, {
            'current_time': 1255885531,
            'cached_until': 1258571131,
        })


if __name__ == "__main__":
    unittest.main()
