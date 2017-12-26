import unittest
import io
from pycoin.block import Block as BlockObject
from pycoin.serialize import h2b


from models import db, Block, Transaction, TxIn, TxOut
from tests.base import BaseTestCase
from controllers.save_to_db import block_to_db, get_max_height


class TestBlockToDb(BaseTestCase):
    block_hash = '0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e677' \
                 '68f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c01010000000100000000000000000000000000' \
                 '00000000000000000000000000000000000000ffffffff4d04ffff001d0104455468652054696d65732030332f4a616e2f3' \
                 '2303039204368616e63656c6c6f72206f6e206272696e6b206f66207365636f6e64206261696c6f757420666f722062616e' \
                 '6b73ffffffff0100f2052a01000000434104678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb' \
                 '649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5fac00000000'

    def setUp(self):
        super(TestBlockToDb, self).setUp()

        block_data = h2b(self.block_hash)
        self.block_object = BlockObject.parse(io.BytesIO(block_data))
        block_to_db(self.block_object, 500000)

    def test_block(self):
        blocks = Block.query.all()

        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].block_hash, '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f')

    def test_transaction(self):
        txs = Transaction.query.all()

        self.assertEqual(len(txs), 1)
        self.assertEqual(txs[0].hash, '4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b')

    def test_ins(self):
        txs = TxIn.query.all()

        self.assertEqual(len(txs), 1)
        self.assertEqual(txs[0].script, '04ffff001d0104455468652054696d65732030332f4a616e2f32303039204368616e63656c6c6f72206f6e206272696e6b206f66207365636f6e64206261696c6f757420666f722062616e6b73')

    def test_outs(self):
        txs = TxOut.query.all()

        self.assertEqual(len(txs), 1)
        self.assertEqual(txs[0].coin_value, 5000000000)

    def test_max_height(self):
        max = get_max_height()

        self.assertEqual(max, 500000)