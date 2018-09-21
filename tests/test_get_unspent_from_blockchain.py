import unittest
import json
from models import db, Block, Transaction, TxIn, TxOut, Address, get_one_or_create
from tests.base import BaseTestCase
from controllers.api_controller import UnspentApi


class TestUnspentFromBlockchain(BaseTestCase):

    def setUp(self):
        super(TestUnspentFromBlockchain, self).setUp()

        self.test_address = '16UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM'

        prev_block = Block.query.filter_by(block_hash='000000000000000000008d511a269a69381e3c7ad1749cf2573d538f745d3f30').first()

        self.block = Block(
            block_hash='000000000000000000872785e17f233dda3ce3cf0e1c9a80180ab2398fc0206d',
            mercle_root='49b2c5a39b328adca6b8b1d22239fc7d3161dff2ad3fbfc70c6782f7dd777067',
            difficulty=402691653,
            nonce=1778502501,
            prev_block=prev_block,
            timestamp=1514107322,
            version=536870912,
            tx_count=2,
            height=1
        )

        self.tx = Transaction(
            hash='tx_hash_1',
            version=1,
            lock_time=0,
            size=289,
            position=150
        )

        self.tx.save()

        self.tx_in = TxIn(
            transaction=self.tx,
            position=10,
            sequence='4294967295',
            script='script in 1',
            previous_id=None # child
        )
        self.tx_in.save()

        self.tx_out = TxOut(
            transaction=self.tx,
            position=15,
            coin_value=5000000000,
            script='script out 1',
            address=get_one_or_create(db.session, Address, bitcoin_address=self.test_address)[0]
        )
        self.tx_out.save()

        # add second transaction in block

        self.tx2 = Transaction(
            hash='tx_hash_1',
            version=1,
            lock_time=0,
            size=289,
            position=150
        )

        self.tx2.save()

        self.tx_in2 = TxIn(
            transaction=self.tx2,
            position=11,
            sequence='4294967295',
            script='script in 2',
            previous_id=None  # child
        )
        self.tx_in.save()

        self.tx_out2 = TxOut(
            transaction=self.tx2,
            position=16,
            coin_value=2500000000,
            script='script out 2',
            address=get_one_or_create(db.session, Address, bitcoin_address=self.test_address)[0]
        )
        self.tx_out2.save()

        self.block.transactions.append(self.tx2)
        self.block.transactions.append(self.tx)
        self.block.save()

    def test_unspent(self):

        tx_out = TxOut()
        unspent = tx_out.get_unspents(self.test_address)

        self.assertEqual(len(unspent), 2)
        self.assertIsInstance(unspent[0], TxOut)
        self.assertIsInstance(unspent[1], TxOut)

    def test_unspent_not_system_address(self):

        tx_out = TxOut()
        unspent = tx_out.get_unspents('non_')

        self.assertEqual(len(unspent), 0)

    def test_unspent_with_used_tx(self):
        # create new block
        block2 = Block(
            block_hash='000000000000000000872785e17f233dda3ce3cf0e1c9a80180ab2398fc0206d',
            mercle_root='49b2c5a39b328adca6b8b1d22239fc7d3161dff2ad3fbfc70c6782f7dd777067',
            difficulty=402691653,
            nonce=1778502501,
            prev_block=self.block,
            timestamp=1514107322,
            version=536870912,
            tx_count=1,
            height=2
        )

        tx = Transaction(
            hash='tx_hash_3',
            version=1,
            lock_time=0,
            size=289,
            position=150
        )

        tx.save()

        tx_in = TxIn(
            transaction=tx,
            position=10,
            sequence='4294967295',
            script='script 3',
            previous=self.tx_out  # child
        )
        tx_in.save()

        tx_out = TxOut(
            transaction=self.tx,
            position=15,
            coin_value=5000000000,
            script='script out 3',
            address=get_one_or_create(db.session, Address, bitcoin_address='just another address')[0]
        )
        tx_out.save()
        block2.transactions.append(self.tx)
        block2.save()

        # get unspents
        tx_out = TxOut()
        unspent = tx_out.get_unspents(self.test_address)

        self.assertEqual(len(unspent), 1)
        self.assertEqual(unspent[0].coin_value, 2500000000)
        self.assertEqual(unspent[0].script, 'script out 2')
        self.assertEqual(unspent[0].transaction.hash, 'tx_hash_1')

    def test_unspent_api(self):
        response = self.client.get(
            '/api/v1/unspent',
            query_string=dict(address=self.test_address),
        )

        data = json.loads(response.data.decode())
        self.assertEqual(len(data['unspent_outputs']), 2)
        self.assertEqual(response.status_code, 200)

    def test_unspent_to_json(self):
        unspent_api = UnspentApi()
        jsonunspent = unspent_api.json_unspent([self.tx_out, self.tx_out2])

        self.assertEqual(len(jsonunspent['unspent_outputs']), 2)
        self.assertEqual(jsonunspent, {'unspent_outputs': [
            {'script': 'script out 1',
             'tx_output_n': 15,
             'tx_hash_big_endian': 'tx_hash_1',
             'value': 5000000000},
            {'script': 'script out 2',
             'tx_output_n': 16,
             'tx_hash_big_endian': 'tx_hash_1',
             'value': 2500000000}
        ]})
