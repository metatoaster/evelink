from evelink import api
from evelink import constants

class Account(object):
    """Wrapper around /account/ of the EVE API.

    Note that a valid API key is required.
    """

    def __init__(self, api):
        self.api = api

    def status(self):
        """Returns the account's subscription status."""
        api_result = self.api.get('account/AccountStatus')

        _str, _int, _float, _bool, _ts = api.elem_getters(
            self.api.result_node(api_result))

        result = {
            'paid_ts': _ts('paidUntil'),
            'create_ts': _ts('createDate'),
            'logins': _int('logonCount'),
            'minutes_played': _int('logonMinutes'),
        }

        return self.api.format_result(api_result, result)

    def key_info(self):
        """Returns the details of the API key being used to auth."""

        raw_api_result = self.api.get('account/APIKeyInfo')
        api_result = self.api.result_node(raw_api_result)

        key = api_result.find('key')
        result = {
            'access_mask': int(key.attrib['accessMask']),
            'type': constants.APIKey.key_types[key.attrib['type']],
            'expire_ts': api.parse_ts(key.attrib['expires']) if key.attrib['expires'] else None,
            'characters': {},
        }

        rowset = key.find('rowset')
        for row in rowset.findall('row'):
            character = {
                'id': int(row.attrib['characterID']),
                'name': row.attrib['characterName'],
                'corp': {
                    'id': int(row.attrib['corporationID']),
                    'name': row.attrib['corporationName'],
                },
            }
            result['characters'][character['id']] = character

        return self.api.format_result(raw_api_result, result)

    def characters(self):
        """Returns all of the characters on an account."""

        raw_api_result = self.api.get('account/Characters')
        api_result = self.api.result_node(raw_api_result)

        rowset = api_result.find('rowset')
        result = {}
        for row in rowset.findall('row'):
            character = {
                'id': int(row.attrib['characterID']),
                'name': row.attrib['name'],
                'corp': {
                    'id': int(row.attrib['corporationID']),
                    'name': row.attrib['corporationName'],
                },
            }
            result[character['id']] = character

        return self.api.format_result(raw_api_result, result)
