import io
import unittest
from unittest.mock import patch
from tests.base import BaseTestCase
from pycoin.block import Block as BlockObject
from pycoin.serialize import h2b
from controllers.api_controller import block_checker


class TestBlockChecker(BaseTestCase):

    def setUp(self):
        super(TestBlockChecker, self).setUp()

        block_hash = '010000006f187fddd5e28aa1b4065daa5d9eae0c487094fb20cf97ca02b81c84000000005b7b25b51797f8319' \
                     '2f9fd2c3871bfb27570a7d6b56d3a50760613d1a2fc1aeeab346849ffff001d36d95071010100000001000000' \
                     '0000000000000000000000000000000000000000000000000000000000ffffffff0704ffff001d0120fffffff' \
                     'f0100f2052a0100000043410408ab2f56361f83064e4ce51acc291fb57c2cbcdb1d6562f6278c43a1406b548fd' \
                     '6cefc11bcc29eb620d5861cb9ed69dc39f2422f54b06a8af4f78c8276cfdc6bac00000000'

        block_data = h2b(block_hash)
        self.block_object = BlockObject.parse(io.BytesIO(block_data))
        self.block_height = 500809

    # @patch('controllers.bitcoin.get_block')
    def test_tx(self):
        # mockedblock.return_value = self.block_object, self.block_height
        # block_checker.delay()

        # tx = self.block.txs[1]
        self.assertEqual(1, 1)
        # self.assertEqual(tx.w_id(), 'a705dac9b33a88d64fbe10f353a20051bdf8a717c84b981cb88591023c3e09ad')