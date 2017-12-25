import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError


def init_db(db):
    """Add a save() function to db.Model"""
    def save(model):
        db.session.add(model)
        db.session.commit()

    db.Model.save = save


db = SQLAlchemy()
init_db(db)


class Block(db.Model):
    """ Block Model """
    __tablename__ = "blocks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    block_hash = db.Column(db.String(64), nullable=False)
    mercle_root = db.Column(db.String(64), nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    nonce = db.Column(db.Integer, nullable=False)
    # previous_block_hash = db.Column(db.String(64), nullable=False)

    parent_id = db.Column(db.Integer, db.ForeignKey(id))
    next_block = db.relationship(
        'Block', backref=db.backref('prev_block', remote_side=[id]),
        lazy='dynamic')

    timestamp = db.Column(db.Integer, nullable=False)
    version = db.Column(db.Integer, nullable=False)
    tx_count = db.Column(db.Integer, nullable=False)
    transactions = db.relationship('Transactions', backref='block', lazy=True)
    height = db.Column(db.Integer, nullable=False)


class Transactions(db.Model):
    """ Transactions Model """
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hash = db.Column(db.String(64), nullable=False, index=True)
    version = db.Column(db.Integer, nullable=False)
    lock_time = db.Column(db.Integer, nullable=False)
    size = db.Column(db.Integer, nullable=False)  # len(tx.as_bin())
    position = db.Column(db.Integer, nullable=False)

    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'), nullable=False)

    tx_ins = db.relationship('TxIns', backref='transaction', lazy=True)
    tx_outs = db.relationship('TxOuts', backref='transaction', lazy=True)


class TxIns(db.Model):
    """ Incoming tx Model """
    __tablename__ = "tx_ins"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tx_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    sequence = db.Column(db.String(12), nullable=False)
    script = db.Column(db.Text, nullable=False)
    previous_id = db.Column(db.Integer, db.ForeignKey('tx_outs.id'))  # child
    ins = db.relationship('TxOuts', backref='tx_ins', lazy=True)


class TxOuts(db.Model):
    """ Outgoing tx Model """
    __tablename__ = "tx_outs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tx_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    outs = db.relationship('TxIns', backref='previous', lazy=True, uselist=False) # parent
    coin_value = db.Column(db.Numeric(30), nullable=False)
    script = db.Column(db.Text, nullable=False)