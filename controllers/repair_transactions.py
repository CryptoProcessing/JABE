from models import db, Transaction, TxOut, TxIn, Block, block_tx
from .save_to_db import address_solve, TxProcess


def repair_transactions(block_object, height):
    """
    :param block_object:
    :param height: block height
    :return:
    """

    db_block = Block.query.filter_by(height=height).one()

    transaction = Transaction.query.filter(Transaction.block.any(id=db_block.id)).all()

    # process = RepairTransaction(block_object.txs)
    # process.run()

    # db.session.commit()
    #
    if not transaction:
        print('add {}'.format(height))
        address_dict = address_solve(block_object)
        db.session.add_all(list(address_dict.values()))
        process = TxProcess(block_object.txs, db_block, address_dict=address_dict)
        process.run()

        db.session.commit()
        return len(block_object.txs)
    # return len(block_object.txs)


class RepairTransaction:

    def __init__(self, tx_list):
        self.tx_list = tx_list




