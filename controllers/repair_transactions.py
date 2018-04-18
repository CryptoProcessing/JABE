from models import db, Transaction, TxOut, TxIn, Block, block_tx


def repair_transactions(block_object, height):
    """
    :param block_object:
    :param height: block height
    :return:
    """

    db_block = Block.query.filter_by(height=height).one()

    transaction = Transaction.query.filter(Transaction.block.any(Transaction.block.any(id=db_block.id))).all()

    # process = RepairTransaction(block_object.txs)
    # process.run()

    # db.session.commit()
    #
    if not transaction:
        print(height)
    # return len(block_object.txs)


class RepairTransaction:

    def __init__(self, tx_list):
        self.tx_list = tx_list




