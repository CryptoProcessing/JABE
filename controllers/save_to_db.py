from models import db, Block, Transaction, TxOut, TxIn, Address, get_one_or_create, get_or_create_address
from sqlalchemy.sql import func
from sqlalchemy import and_, or_
import datetime

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

    # build dict of outs
    # print('transaction to dict start {}'.format(datetime.datetime.now()))
    # outs_dict = transaction_out_to_dict(block_object)
    # print('address start {}'.format(datetime.datetime.now()))
    # create all block address
    address_dict = address_solve(block_object)
    # print('address finish {}'.format(datetime.datetime.now()))
    db.session.add_all(list(address_dict.values()))
    # print('TX process start {}'.format(datetime.datetime.now()))
    process = TxProcess(block_object.txs, block, numerate_start=0, address_dict=address_dict) #, outs_dict=outs_dict)
    process.run()

    db.session.commit()

    return len(block_object.txs)


def transaction_out_to_dict(block_object):
    # list of transaction ins from block
    list_ins = [tx.txs_in for tx in block_object.txs]
    # condition for query
    cond = or_(*[and_(Transaction.hash == str(item.previous_hash), TxOut.position == item.previous_index)
                 for l in list_ins for item in l])
    query_result = TxOut.query.join(Transaction).filter(cond)
    # build dictionary of db Outs
    # outs_dict = {'{}_{}'.format(f.position, f.transaction.hash): f for f in query_result}

    return query_result


def address_solve(block_object):

    # all outs
    list_of_lists = [tx.txs_out for tx in block_object.txs]
    # set of addresses
    address_set = set([get_address_name(item) for l in list_of_lists for item in l])
    # check addres in db
    # address_dict = {item: get_one_or_create(db.session, Address, bitcoin_address=item)[0] for item in address_set}
    address_dict = {item: get_or_create_address(bitcoin_address=item) for item in address_set}

    return address_dict


class TxProcess:

    def __init__(self, tx_list, block, numerate_start, address_dict): #, outs_dict):
        self.tx_list = tx_list
        self.block = block
        self.numerate_start = numerate_start
        self.address_dict = address_dict
        # self.outs_dict = outs_dict

    def tx_in_to_db(self, txs_ins, tx_db):
        """
        Add all transaction ins to DB
        :param txs_ins:
        :param tx_db:
        :return:
        """

        tx_ins = [self.save_tx_in_db(itn, tx_db, txin) for itn, txin in enumerate(txs_ins)]
        # db.session.add_all(tx_ins)
        return tx_ins

    def save_tx_in_db(self, itn, tx_db, txin):
        """
        Add transaction in to DB
        :param itn:
        :param tx_db:
        :param txin:
        :return:
        """
        # previous_out = self.get_previous_out(txin)
        previous_out = None
        tx_in = TxIn(
            transaction=tx_db,
            position=itn,
            sequence=txin.sequence,
            script=txin.script.hex(),
            previous=previous_out  # child
        )

        return tx_in

    def get_previous_out(self, txin):
        """
        return previous out
        :param txin:
        :return:
        """
        # coinbase transaction
        # if str(txin.previous_hash) == '0000000000000000000000000000000000000000000000000000000000000000':
        #     print('coinbase')
        #     return None

        # 1. search in dict
        # previous_out = self.outs_dict.get('{}_{}'.format(txin.previous_index, str(txin.previous_hash)))

        # if not find, search in db, maybe txin in the same block
        # if not previous_out:
        previous_out = TxOut.query.join(Transaction).filter(
            Transaction.hash == str(txin.previous_hash),
            TxOut.position == txin.previous_index) \
            .first()

        return previous_out

    def _get_address_from_dict(self,txout):
        # return get_or_create_address(bitcoin_address=get_address_name(txout))
        return self.address_dict[get_address_name(txout)]

    def tx_out_to_db(self, txs_ins, tx_db):
        """
        Add transaction out to DB
        :param txs_ins:
        :param tx_db:
        :return:
        # """
        txouts = [
            TxOut(
                transaction=tx_db,
                position=ito,
                coin_value=txout.coin_value,
                script=txout.script.hex(),
                address=self._get_address_from_dict(txout)
            ) for ito, txout in enumerate(txs_ins)
        ]

        return txouts

    def tx_to_db(self, txs, block, numerate_start=0):
        """
        Add all transaction outs to DB
        :param txs:
        :param block:
        :return:
        """

        list_txs = [self.save_tx_to_db(block, itx, tx) for itx, tx in enumerate(txs)]

        db.session.add_all([item for l in list_txs for item in l])
        db.session.commit()

    def save_tx_to_db(self, block, itx, tx):
        """
        Save transaction to DB
        :param block_id:
        :param itx: tx count
        :param tx:
        :return:
        """

        db_obj = []

        tx_db = Transaction(
            hash=tx.w_id(),
            version=tx.version,
            lock_time=tx.lock_time,
            size=len(tx.as_bin()),
            position=itx
        )

        block.transactions.append(tx_db)

        db_obj.extend(self.tx_in_to_db(tx.txs_in, tx_db))
        db_obj.extend(self.tx_out_to_db(tx.txs_out, tx_db))
        db_obj.append(tx_db)
        return db_obj

    def run(self):
        self.tx_to_db(txs=self.tx_list, block=self.block, numerate_start=self.numerate_start)

