import unittest

from models import db, Block, Transactions, TxIns, TxOuts
from tests.base import BaseTestCase


class TestBlockModel(BaseTestCase):

    def setUp(self):
        super(TestBlockModel, self).setUp()

        self.block = Block(
            block_hash='000000000000000000872785e17f233dda3ce3cf0e1c9a80180ab2398fc0206d',
            mercle_root='49b2c5a39b328adca6b8b1d22239fc7d3161dff2ad3fbfc70c6782f7dd777067',
            difficulty=402691653,
            nonce=1778502501,
            previous_block_hash='000000000000000000008d511a269a69381e3c7ad1749cf2573d538f745d3f30',
            timestamp=1514107322,
            version=536870912,
            tx_count=2137
        )
        self.block.save()

        self.tx = Transactions(
            block=self.block,
            hash='a705dac9b33a88d64fbe10f353a20051bdf8a717c84b981cb88591023c3e09ad',
            version=1,
            lock_time=0,
            size=289,
            position=150
        )
        self.tx.save()

        self.tx_in = TxIns(
            transaction=self.tx,
            position=10,
            sequence='4294967295',
            script='04ffff001d0104455468652054696d65732030332f4a616e2f32303039204368616e63656c6c6f72206f6e206272696e6b206f66207365636f6e64206261696c6f757420666f722062616e6b73',
            previous_id=None # child
        )
        self.tx_in.save()

        self.tx_out = TxOuts(
            transaction=self.tx,
            position=15,
            coin_value=5000000000,
            script='4104678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5fac'
        )
        self.tx_out.save()

    def test_block(self):

        self.assertEqual(self.block.block_hash, '000000000000000000872785e17f233dda3ce3cf0e1c9a80180ab2398fc0206d')
        self.assertEqual(self.block.mercle_root, '49b2c5a39b328adca6b8b1d22239fc7d3161dff2ad3fbfc70c6782f7dd777067')
        self.assertEqual(self.block.difficulty, 402691653)
        self.assertEqual(self.block.nonce, 1778502501)
        self.assertEqual(self.block.previous_block_hash,
                         '000000000000000000008d511a269a69381e3c7ad1749cf2573d538f745d3f30')
        self.assertEqual(self.block.timestamp, 1514107322)
        self.assertEqual(self.block.version, 536870912)
        self.assertEqual(self.block.tx_count, 2137)

    def test_tx(self):

        self.assertEqual(self.tx.hash, 'a705dac9b33a88d64fbe10f353a20051bdf8a717c84b981cb88591023c3e09ad')
        self.assertEqual(self.tx.version, 1)
        self.assertEqual(self.tx.lock_time, 0)
        self.assertEqual(self.tx.block, self.block)
        self.assertEqual(self.tx.size, 289)
        self.assertEqual(self.tx.position, 150)

    def test_tx_in(self):
        self.assertEqual(self.tx_in.transaction, self.tx)
        self.assertEqual(self.tx_in.position, 10)
        self.assertEqual(self.tx_in.sequence, '4294967295')
        self.assertEqual(self.tx_in.script, '04ffff001d0104455468652054696d65732030332f4a616e2f32303039204368616e63656c6c6f72206f6e206272696e6b206f66207365636f6e64206261696c6f757420666f722062616e6b73')
        self.assertEqual(self.tx_in.previous_id, None)

    def test_tx_out(self):
        self.assertEqual(self.tx_out.transaction, self.tx)
        self.assertEqual(self.tx_out.position, 15)
        self.assertEqual(self.tx_out.coin_value, 5000000000)
        self.assertEqual(self.tx_out.script, '4104678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5fac')

    def test_tx_in_with_link_on_out(self):

        tx_in_with_link_on_out = TxIns(
            transaction=self.tx,
            position=11,
            sequence='4294967295',
            script='script',
            previous=self.tx_out # child
        )

        tx_in_with_link_on_out.save()

        self.assertEqual(tx_in_with_link_on_out.transaction, self.tx)
        self.assertEqual(tx_in_with_link_on_out.position, 11)
        self.assertEqual(tx_in_with_link_on_out.sequence, '4294967295')
        self.assertEqual(tx_in_with_link_on_out.script, 'script')
        self.assertEqual(tx_in_with_link_on_out.previous_id, 1)
        self.assertEqual(tx_in_with_link_on_out.previous, self.tx_out)


if __name__ == '__main__':
    unittest.main()