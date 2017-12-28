from models import db, Block, Transaction, TxOut, TxIn, Address, get_one_or_create
from sqlalchemy.sql import func


def get_max_height():
    """
    Return Max block height value from db
    :return:
    """
    max = Block.query.with_entities(func.max(Block.height).label('max')).first().max

    if max == None:
        max = -1
    return max


def tx_in_to_db(txs_ins, tx_db):
    """
    Add all transaction ins to DB
    :param txs_ins:
    :param tx_db:
    :return:
    """

    tx_ins = [save_tx_in_db(itn, tx_db, txin) for itn, txin in enumerate(txs_ins)]
    db.session.add_all(tx_ins)


def save_tx_in_db(itn, tx_db, txin):
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

    # previous_out =

    tx_in = TxIn(
        transaction=tx_db,
        position=itn,
        sequence=txin.sequence,
        script=txin.script.hex(),
        previous=previous_out  # child
    )

    return tx_in


def tx_out_to_db(txs_ins, tx_db):
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
            address=get_one_or_create(
                db.session,
                Address,
                bitcoin_address=txout.address()
                    if ('nulldata' not in txout.address()) else "(unknown)")[0]
        ) for ito, txout in enumerate(txs_ins)
    ]

    db.session.add_all(txouts)


def tx_to_db(txs, block):
    """
    Add all transaction outs to DB
    :param txs:
    :param block:
    :return:
    """
    list_txs = [save_tx_to_db(block, itx, tx) for itx, tx in enumerate(txs)]

    db.session.add_all(list_txs)


def save_tx_to_db(block, itx, tx):
    """
    Save transaction to DB
    :param block:
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
    tx_in_to_db(tx.txs_in, tx_db)
    tx_out_to_db(tx.txs_out, tx_db)

    return tx_db


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

    tx_to_db(block_object.txs, block)

    db.session.commit()

    return len(block_object.txs)
