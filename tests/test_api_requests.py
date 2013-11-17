from StringIO import StringIO
import unittest2 as unittest

import mock

import evelink.api as evelink_api


class DummyResponse(object):
    def __init__(self, content):
        self.content = content


@unittest.skipIf(not evelink_api._has_requests, '`requests` not available')
class RequestsAPITestCase(unittest.TestCase):

    def setUp(self):
        self.cache = mock.MagicMock(spec=evelink_api.APICache)
        self.api = evelink_api.API(cache=self.cache)

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

        requests_patcher = mock.patch('requests.Session')
        requests_patcher.start()
        import requests
        self.mock_sessions = requests.Session()
        self.requests_patcher = requests_patcher

    def tearDown(self):
        self.requests_patcher.stop()

    def test_get(self):
        # mock up a sessions compatible response object and pretend to have
        # nothing chached; similar pattern below for all test_get_* methods
        self.mock_sessions.post.return_value = DummyResponse(self.test_xml)
        self.cache.get.return_value = None

        tree = self.api.get('foo/Bar', {'a':[1,2,3]})

        rowset = tree.find('rowset')
        rows = rowset.findall('row')
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].attrib['foo'], 'bar')
        self.assertEqual(self.api.last_timestamps, {
            'current_time': 1255885531,
            'cached_until': 1258563931,
        })

    def test_get_result_key(self):
        # mock up a sessions compatible response object and pretend to have
        # nothing chached; similar pattern below for all test_get_* methods
        self.mock_sessions.post.return_value = DummyResponse(self.test_xml)
        self.cache.get.return_value = None

        tree = self.api.get('foo/Bar', {'a':[1,2,3]}, result_key='')
        result = tree.find('result')

        rowset = result.find('rowset')
        rows = rowset.findall('row')
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].attrib['foo'], 'bar')
        self.assertEqual(self.api.last_timestamps, {
            'current_time': 1255885531,
            'cached_until': 1258563931,
        })

    def test_get_default_result_key(self):
        # mock up a sessions compatible response object and pretend to have
        # nothing chached; similar pattern below for all test_get_* methods
        self.mock_sessions.post.return_value = DummyResponse(self.test_xml)
        self.cache.get.return_value = None

        api = evelink_api.API(cache=self.cache, default_result_key=None)
        tree = api.get('foo/Bar', {'a':[1,2,3]})
        self.assertEqual(len(tree.findall('result')), 1)

        result = api.get('foo/Bar', {'a':[1,2,3]}, result_key='result')
        self.assertEqual(len(result.findall('result')), 0)
        self.assertEqual(len(result.findall('rowset')), 1)

    def test_cached_get(self):
        """Make sure that we don't try to call the API if the result is cached."""
        # mock up a sessions compatible error response, and pretend to have a
        # good test response cached.
        self.mock_sessions.post.return_value = DummyResponse(self.error_xml)
        self.cache.get.return_value = self.test_xml

        result = self.api.get('foo/Bar', {'a':[1,2,3]})

        rowset = result.find('rowset')
        rows = rowset.findall('row')
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].attrib['foo'], 'bar')

        self.assertFalse(self.mock_sessions.post.called)
        # timestamp attempted to be extracted.
        self.assertEqual(self.api.last_timestamps, {
            'current_time': 1255885531,
            'cached_until': 1258563931,
        })

    def test_get_with_apikey(self):
        self.mock_sessions.post.return_value = DummyResponse(self.test_xml)
        self.cache.get.return_value = None

        api_key = (1, 'code')
        api = evelink_api.API(cache=self.cache, api_key=api_key)

        api.get('foo', {'a':[2,3,4]})

        # Make sure the api key id and verification code were passed
        self.assertEqual(self.mock_sessions.post.mock_calls, [
                mock.call(
                    'https://api.eveonline.com/foo.xml.aspx',
                    params='a=2%2C3%2C4&vCode=code&keyID=1',
                ),
            ])

    def test_get_with_error(self):
        self.mock_sessions.get.return_value = DummyResponse(self.error_xml)
        self.cache.get.return_value = None

        self.assertRaises(evelink_api.APIError,
            self.api.get, 'eve/Error')
        self.assertEqual(self.api.last_timestamps, {
            'current_time': 1255885531,
            'cached_until': 1258571131,
        })

    def test_cached_get_with_error(self):
        """Make sure that we don't try to call the API if the result is cached."""
        # mocked response is good now, with the error response cached.
        self.mock_sessions.post.return_value = DummyResponse(self.test_xml)
        self.cache.get.return_value = self.error_xml
        self.assertRaises(evelink_api.APIError,
            self.api.get, 'foo/Bar', {'a':[1,2,3]})

        self.assertFalse(self.mock_sessions.post.called)
        self.assertEqual(self.api.last_timestamps, {
            'current_time': 1255885531,
            'cached_until': 1258571131,
        })


if __name__ == "__main__":
    unittest.main()
