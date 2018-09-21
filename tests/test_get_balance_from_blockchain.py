import unittest
import json
from models import db, Block, Transaction, TxIn, TxOut, Address, get_one_or_create
from tests.base import BaseTestCase
from controllers.api_controller import UnspentApi, BalanceApi


class TestBalanceFromBlockchain(BaseTestCase):

    def setUp(self):
        super(TestBalanceFromBlockchain, self).setUp()

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

    def test_balance(self):

        addr_obj = Address()
        balance, count_tx = addr_obj.get_balance(self.test_address)

        self.assertEqual(balance, 7500000000)
        self.assertEqual(count_tx, 2)

    def test_balance_not_system_address(self):
        addr_obj = Address()
        balance, _ = addr_obj.get_balance('non_')

        self.assertEqual(balance, 0)

    def test_balance_with_used_tx(self):
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
            coin_value=4000000000,
            script='script out 3',
            address=get_one_or_create(db.session, Address, bitcoin_address='just another address')[0]
        )
        tx_out.save()
        block2.transactions.append(self.tx)
        block2.save()

        # get balance
        addr_obj = Address()
        balance, count_tx = addr_obj.get_balance(self.test_address)

        self.assertEqual(balance, 2500000000)
        self.assertEqual(count_tx, 1)

    def test_balance_with_used_return_cash_tx(self):
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
            coin_value=4000000000,
            script='script out 3',
            address=get_one_or_create(db.session, Address, bitcoin_address='just another address')[0]
        )
        tx_out.save()

        tx_out2 = TxOut(
            transaction=self.tx,
            position=15,
            coin_value=500000000,
            script='script out 4 return cash',
            address=get_one_or_create(db.session, Address, bitcoin_address=self.test_address)[0]
        )
        tx_out2.save()
        block2.transactions.append(self.tx)
        block2.save()

        # get balance
        addr_obj = Address()
        balance, count_tx = addr_obj.get_balance(self.test_address)

        self.assertEqual(balance, 3000000000)
        self.assertEqual(count_tx, 2)

    def test_balance_api(self):
        response = self.client.get(
            '/api/v1/balance',
            query_string=dict(address=self.test_address),
        )

        data = json.loads(response.data.decode())
        self.assertEqual(len(data[self.test_address]), 1)
        self.assertEqual(response.status_code, 200)

    def test_balance_to_json(self):
        balance_api =BalanceApi()
        jsonunspent = balance_api.json_balance(1000000, 10)

        self.assertEqual(jsonunspent, {'balance': 1000000, 'n_tx': 10})
