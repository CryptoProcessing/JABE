from models import Block, Transactions, TxOuts, TxIns


def tx_in_to_db(txs_ins, tx_db):
    for itn, txin in enumerate(txs_ins):

        prev_tx = Transactions.query.filter_by(hash=str(txin.previous_hash)).first()
        if prev_tx:
            previous_out = TxOuts.query.filter_by(tx=prev_tx, position=txin.previous_index).first()
        else:
            previous_out=None

        tx_in = TxIns(
            transaction=tx_db,
            position=itn,
            sequence=txin.sequence,
            script=txin.script.hex(),
            previous=previous_out # child
        )
        tx_in.save()


def tx_out_to_db(txs_ins, tx_db):
    for ito, txout in enumerate(txs_ins):
        tx_out = TxOuts(
            transaction=tx_db,
            position=ito,
            coin_value=txout.coin_value,
            script=txout.script.hex()
        )
        tx_out.save()


def tx_to_db(txs, block):
    for itx, tx in enumerate(txs):
        tx_db = Transactions(
            block=block,
            hash=tx.w_id(),
            version=tx.version,
            lock_time=tx.lock_time,
            size=len(tx.as_bin()),
            position=itx
        )
        tx_db.save()

        tx_in_to_db(tx.txs_in, tx_db)
        tx_out_to_db(tx.txs_out, tx_db)


def block_to_db(block_object, height):
    block = Block(
        block_hash=str(block_object.hash()),
        mercle_root=str(block_object.merkle_root),
        difficulty=block_object.difficulty,
        nonce=block_object.nonce,
        prev_block=Block.query.filter_by(block_hash=block_object.previous_block_hash).first(),
        timestamp=block_object.timestamp,
        version=block_object.version,
        tx_count=len(block_object.txs),
        height=height
    )

    block.save()

    tx_to_db(block_object.txs, block)
