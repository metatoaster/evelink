import unittest2 as unittest

from evelink.account import Account
from evelink import constants
from tests.utils import TestFileAPITestCase

class AccountTestCase(TestFileAPITestCase):

    test_cls = Account

    def test_status(self):
        self.assertBothCallsEqual(Account.status, result={
                'create_ts': 1072915200,
                'logins': 1234,
                'minutes_played': 9999,
                'paid_ts': 1293840000,
            })

    def test_key_info(self):
        self.assertBothCallsEqual(Account.key_info, result={
                'access_mask': 59760264,
                'type': constants.CHARACTER,
                'expire_ts': 1315699200,
                'characters': {
                    898901870: {
                        'id': 898901870,
                        'name': "Desmont McCallock",
                        'corp': {
                            'id': 1000009,
                            'name': "Caldari Provisions",
                        },
                    },
                },
            })

    def test_characters(self):
        self.assertBothCallsEqual(Account.characters, result={
                1365215823: {
                    'corp': {
                        'id': 238510404,
                        'name': 'Puppies To the Rescue',
                    },
                    'id': 1365215823,
                    'name': 'Alexis Prey',
                },
            })


if __name__ == "__main__":
    unittest.main()
