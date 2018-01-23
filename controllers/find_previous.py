from models import db, Transaction, TxOut, TxIn


def find_previous_in_block(block_object):
    """
    :param block_object:
    :param height: block height
    :return:
    """

    process = FindProcess(block_object.txs)
    process.run()

    db.session.commit()

    return len(block_object.txs)


class FindProcess:

    def __init__(self, tx_list):
        self.tx_list = tx_list

    def find_all_prev(self, txs):
        """
        Add all transaction outs to DB
        :param txs:
        :param block:
        :return:
        """

        for tx in txs:
            tx_obj = Transaction.query.filter_by(hash=str(tx.hash())).first()
            for ix, txin in enumerate(tx.txs_in):
                if str(txin.previous_hash) == '0000000000000000000000000000000000000000000000000000000000000000':
                    continue

                previous_out = TxOut.query.join(Transaction).filter(
                    Transaction.hash == str(txin.previous_hash),
                    TxOut.position == txin.previous_index) \
                    .first()

                if previous_out:
                    in_obj = TxIn.query.filter(TxIn.tx_id == tx_obj.id, TxIn.position == ix).first()
                    in_obj.previous = previous_out
                    # db.session.commit()
                    # print(tx_obj.id, ix)

    def run(self):
        self.find_all_prev(txs=self.tx_list)


