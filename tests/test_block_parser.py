import unittest
from controllers.bitcoin import get_block


class TestBlockParser(unittest.TestCase):
    def setUp(self):
        # block, block_height = get_block('000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f') # first block ever
        self.block, self.block_height = get_block('000000000000000000872785e17f233dda3ce3cf0e1c9a80180ab2398fc0206d')

    def test_block(self):

        self.assertEqual(self.block.version, 536870912)
        self.assertEqual(len(self.block.txs), 2137)
        self.assertEqual(self.block_height, 500809)

    def test_tx(self):
        tx = self.block.txs[1]

        self.assertEqual(tx.w_id(), 'a705dac9b33a88d64fbe10f353a20051bdf8a717c84b981cb88591023c3e09ad')