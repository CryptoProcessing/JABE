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


def get_one_or_create(session,
                      model,
                      create_method='',
                      create_method_kwargs=None,
                      **kwargs):
    try:
        return session.query(model).filter_by(**kwargs).one(), True
    except NoResultFound:
        kwargs.update(create_method_kwargs or {})
        try:
            with session.begin_nested():
                created = getattr(model, create_method, model)(**kwargs)
                session.add(created)
            return created, False
        except IntegrityError:
            return session.query(model).filter_by(**kwargs).one(), True


block_tx = db.Table('block_tx',
    db.Column('transaction_id', db.Integer, db.ForeignKey('transactions.id'), primary_key=True),
    db.Column('block_id', db.Integer, db.ForeignKey('blocks.id'), primary_key=True)
)


class Block(db.Model):
    """ Block Model """
    __tablename__ = "blocks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    block_hash = db.Column(db.String(64), nullable=False, index=True)
    mercle_root = db.Column(db.String(64), nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    nonce = db.Column(db.Numeric(12), nullable=False)
    # previous_block_hash = db.Column(db.String(64), nullable=False)

    parent_id = db.Column(db.Integer, db.ForeignKey(id))
    next_block = db.relationship(
        'Block', backref=db.backref('prev_block', remote_side=[id]),
        lazy='dynamic')

    timestamp = db.Column(db.Integer, nullable=False)
    version = db.Column(db.Integer, nullable=False)
    tx_count = db.Column(db.Integer, nullable=False)
    transactions = db.relationship('Transaction', secondary=block_tx,
                                   backref=db.backref('block', lazy=True), lazy='subquery')
    height = db.Column(db.Integer, nullable=False, index=True)


# TODO: many-to-many relationship with block
class Transaction(db.Model):
    """ Transactions Model """
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hash = db.Column(db.String(64), nullable=False, index=True)
    version = db.Column(db.Integer, nullable=False)
    lock_time = db.Column(db.Integer, nullable=False)
    size = db.Column(db.Integer, nullable=False)  # len(tx.as_bin())
    position = db.Column(db.Integer, nullable=False)

    # block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'), nullable=False)

    tx_ins = db.relationship('TxIn', backref='transaction', lazy=True)
    tx_outs = db.relationship('TxOut', backref='transaction', lazy=True)


class TxIn(db.Model):
    """ Incoming tx Model """
    __tablename__ = "tx_ins"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tx_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    sequence = db.Column(db.String(12), nullable=False)
    script = db.Column(db.Text, nullable=False)
    previous_id = db.Column(db.Integer, db.ForeignKey('tx_outs.id'))  # child
    ins = db.relationship('TxOut', backref='tx_ins', lazy=True)


class TxOut(db.Model):
    """ Outgoing tx Model """
    __tablename__ = "tx_outs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tx_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    outs = db.relationship('TxIn', backref='previous', lazy=True, uselist=False) # parent
    coin_value = db.Column(db.Numeric(30), nullable=False)
    script = db.Column(db.Text, nullable=False)


class Lock(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lock = db.Column(db.Boolean)


class Address(db.Model):
    """ Public keys Model """
    __tablename__ = "addresses"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bitcoin_address = db.Column(db.String(100), nullable=False, index=True)
    tx_outs = db.relationship('TxOut', backref='address', lazy=True)