import threading
import datetime
from models import db, Block, Transaction, TxOut, TxIn, Address, get_one_or_create
from sqlalchemy.sql import func
from controllers.utils import split_list


def get_max_height():
    """
    Return Max block height value from db
    :return:
    """
    max = Block.query.with_entities(func.max(Block.height).label('max')).first().max

    if max == None:
        max = -1
    return max


def get_address_name(txout):
    try:
        address = txout.address()
    except:
        address = 'bad script'

    return address


def block_to_db(block_object, height):
    """
    Save block info to DB
    :param block_object:
    :param height: block height
    :return:
    """
    previous_block_obj = Block.query.filter_by(block_hash=str(block_object.previous_block_hash)).first()
    block = Block(
        block_hash=str(block_object.hash()),
        mercle_root=str(block_object.merkle_root),
        difficulty=block_object.difficulty,
        nonce=block_object.nonce,
        prev_block=previous_block_obj,
        timestamp=block_object.timestamp,
        version=block_object.version,
        tx_count=len(block_object.txs),
        height=height
    )
    db.session.add(block)

    # create all block address
    list_of_lists = [tx.txs_out for tx in block_object.txs]
    address_set = set([get_address_name(item) for l in list_of_lists for item in l])
    address_list = [get_one_or_create(db.session, Address, bitcoin_address=item)[0] for item in address_set]
    db.session.add_all(address_list)

    print('address list created  {}'.format(datetime.datetime.now()))

    db.session.commit()

    splitted_list = split_list(block_object.txs)

    processes = []

    for i in range(len(splitted_list)):
        process = TxProcess(splitted_list[i][0], block.id, splitted_list[i][1])
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    db.session.commit()

    return len(block_object.txs)


class TxProcess(threading.Thread):

    def __init__(self, tx_list, block, numerate_start):
        self.tx_list = tx_list,
        self.block = block
        self.numerate_start = numerate_start

        super(TxProcess, self).__init__()

    def tx_in_to_db(self, txs_ins, tx_db):
        """
        Add all transaction ins to DB
        :param txs_ins:
        :param tx_db:
        :return:
        """

        tx_ins = [self.save_tx_in_db(itn, tx_db, txin) for itn, txin in enumerate(txs_ins)]
        db.session.add_all(tx_ins)

    def save_tx_in_db(self, itn, tx_db, txin):
        """
        Add transaction in to DB
        :param itn:
        :param tx_db:
        :param txin:
        :return:
        """
        previous_out = TxOut.query.join(Transaction).filter(
            Transaction.hash == str(txin.previous_hash),
            TxOut.position == txin.previous_index)\
            .first()

        tx_in = TxIn(
            transaction=tx_db,
            position=itn,
            sequence=txin.sequence,
            script=txin.script.hex(),
            previous=previous_out  # child
        )

        return tx_in

    def tx_out_to_db(self, txs_ins, tx_db):
        """
        Add transaction out to DB
        :param txs_ins:
        :param tx_db:
        :return:
        # """
        # txouts = []
        txouts = [
            TxOut(
                transaction=tx_db,
                position=ito,
                coin_value=txout.coin_value,
                script=txout.script.hex(),
                address=Address.query.filter_by(bitcoin_address=get_address_name(txout)).one()
            ) for ito, txout in enumerate(txs_ins)
        ]

        db.session.add_all(txouts)

    def tx_to_db(self, txs, block, numerate_start=0):
        """
        Add all transaction outs to DB
        :param txs:
        :param block:
        :return:
        """
        block = Block.query.get(block)

        list_txs = [self.save_tx_to_db(block, itx + numerate_start, tx) for itx, tx in enumerate(txs[0])]

        db.session.add_all(list_txs)
        db.session.commit()

    def save_tx_to_db(self, block, itx, tx):
        """
        Save transaction to DB
        :param block_id:
        :param itx: tx count
        :param tx:
        :return:
        """
        tx_db = Transaction(
            hash=tx.w_id(),
            version=tx.version,
            lock_time=tx.lock_time,
            size=len(tx.as_bin()),
            position=itx
        )

        block.transactions.append(tx_db)

        self.tx_in_to_db(tx.txs_in, tx_db)
        self.tx_out_to_db(tx.txs_out, tx_db)

        return tx_db

    def run(self):
        self.tx_to_db(txs=self.tx_list, block=self.block, numerate_start=self.numerate_start)

