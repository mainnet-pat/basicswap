# -*- coding: utf-8 -*-

# Copyright (c) 2019 tecnovert
# Distributed under the MIT software license, see the accompanying
# file LICENSE.txt or http://www.opensource.org/licenses/mit-license.php.

import struct
import time
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

CURRENT_DB_VERSION = 1

Base = declarative_base()


class DBKVInt(Base):
    __tablename__ = 'kv_int'
    key = sa.Column(sa.String, primary_key=True)
    value = sa.Column(sa.Integer)


class DBKVString(Base):
    __tablename__ = 'kv_string'
    key = sa.Column(sa.String, primary_key=True)
    value = sa.Column(sa.String)


class Offer(Base):
    __tablename__ = 'offers'

    offer_id = sa.Column(sa.LargeBinary, primary_key=True)

    coin_from = sa.Column(sa.Integer)
    coin_to = sa.Column(sa.Integer)
    amount_from = sa.Column(sa.BigInteger)
    rate = sa.Column(sa.BigInteger)
    min_bid_amount = sa.Column(sa.BigInteger)
    time_valid = sa.Column(sa.BigInteger)
    lock_type = sa.Column(sa.Integer)
    lock_value = sa.Column(sa.Integer)
    swap_type = sa.Column(sa.Integer)

    proof_address = sa.Column(sa.String)
    proof_signature = sa.Column(sa.LargeBinary)
    pkhash_seller = sa.Column(sa.LargeBinary)
    secret_hash = sa.Column(sa.LargeBinary)

    addr_from = sa.Column(sa.String)
    created_at = sa.Column(sa.BigInteger)
    expire_at = sa.Column(sa.BigInteger)
    was_sent = sa.Column(sa.Boolean)

    auto_accept_bids = sa.Column(sa.Boolean)

    state = sa.Column(sa.Integer)
    states = sa.Column(sa.LargeBinary)  # Packed states and times

    def setState(self, new_state):
        now = int(time.time())
        self.state = new_state
        if self.states is None:
            self.states = struct.pack('<iq', new_state, now)
        else:
            self.states += struct.pack('<iq', new_state, now)


class Bid(Base):
    __tablename__ = 'bids'

    bid_id = sa.Column(sa.LargeBinary, primary_key=True)
    offer_id = sa.Column(sa.LargeBinary, sa.ForeignKey('offers.offer_id'))

    was_sent = sa.Column(sa.Boolean)
    was_received = sa.Column(sa.Boolean)
    contract_count = sa.Column(sa.Integer)
    created_at = sa.Column(sa.BigInteger)
    expire_at = sa.Column(sa.BigInteger)
    bid_addr = sa.Column(sa.String)
    proof_address = sa.Column(sa.String)

    recovered_secret = sa.Column(sa.LargeBinary)
    amount_to = sa.Column(sa.BigInteger)  # amount * offer.rate

    pkhash_buyer = sa.Column(sa.LargeBinary)
    amount = sa.Column(sa.BigInteger)

    accept_msg_id = sa.Column(sa.LargeBinary)
    pkhash_seller = sa.Column(sa.LargeBinary)

    #initiate_script = sa.Column(sa.LargeBinary)  # contract_script
    initiate_txid = sa.Column(sa.LargeBinary)
    initiate_txn_n = sa.Column(sa.Integer)
    initiate_txn_conf = sa.Column(sa.Integer)
    initiate_txn_refund = sa.Column(sa.LargeBinary)

    initiate_spend_txid = sa.Column(sa.LargeBinary)
    initiate_spend_n = sa.Column(sa.Integer)

    initiate_txn_height = sa.Column(sa.Integer)
    initiate_txn_state = sa.Column(sa.Integer)
    initiate_txn_states = sa.Column(sa.LargeBinary)  # Packed states and times

    participate_script = sa.Column(sa.LargeBinary)
    participate_txid = sa.Column(sa.LargeBinary)
    participate_txn_n = sa.Column(sa.Integer)
    participate_txn_conf = sa.Column(sa.Integer)
    participate_txn_redeem = sa.Column(sa.LargeBinary)
    participate_txn_refund = sa.Column(sa.LargeBinary)

    participate_spend_txid = sa.Column(sa.LargeBinary)
    participate_spend_n = sa.Column(sa.Integer)

    participate_txn_height = sa.Column(sa.Integer)
    participate_txn_state = sa.Column(sa.Integer)
    participate_txn_states = sa.Column(sa.LargeBinary)  # Packed states and times

    state = sa.Column(sa.Integer)
    state_time = sa.Column(sa.BigInteger)  # timestamp of last state change
    states = sa.Column(sa.LargeBinary)  # Packed states and times

    state_note = sa.Column(sa.String)

    initiate_tx = None
    participate_tx = None

    def setITXState(self, new_state):
        if self.initiate_tx is not None:
            self.initiate_tx.state = new_state
            self.initiate_tx.states = (self.initiate_tx.states if self.initiate_tx.states is not None else bytes()) + struct.pack('<iq', new_state, int(time.time()))

        self.initiate_txn_state = new_state
        if self.initiate_txn_states is None:
            self.initiate_txn_states = struct.pack('<iq', new_state, int(time.time()))
        else:
            self.initiate_txn_states += struct.pack('<iq', new_state, int(time.time()))

    def setPTXState(self, new_state):
        if self.participate_tx is not None:
            self.participate_tx.state = new_state
            self.participate_tx.states = (self.participate_tx.states if self.participate_tx.states is not None else bytes()) + struct.pack('<iq', new_state, int(time.time()))

        self.participate_txn_state = new_state
        if self.participate_txn_states is None:
            self.participate_txn_states = struct.pack('<iq', new_state, int(time.time()))
        else:
            self.participate_txn_states += struct.pack('<iq', new_state, int(time.time()))

    def setState(self, new_state):
        now = int(time.time())
        self.state = new_state
        self.state_time = now
        if self.states is None:
            self.states = struct.pack('<iq', new_state, now)
        else:
            self.states += struct.pack('<iq', new_state, now)


class SwapTx(Base):
    __tablename__ = 'transactions'

    bid_id = sa.Column(sa.LargeBinary, sa.ForeignKey('bids.bid_id'))
    tx_type = sa.Column(sa.Integer)  # TxTypes
    __table_args__ = (
        sa.PrimaryKeyConstraint('bid_id', 'tx_type'),
        {},
    )

    txid = sa.Column(sa.LargeBinary)
    vout = sa.Column(sa.Integer)

    script = sa.Column(sa.LargeBinary)

    tx_fee = sa.Column(sa.BigInteger)
    conf = sa.Column(sa.Integer)

    state = sa.Column(sa.Integer)
    states = sa.Column(sa.LargeBinary)  # Packed states and times


class PooledAddress(Base):
    __tablename__ = 'addresspool'

    addr_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    coin_type = sa.Column(sa.Integer)
    addr = sa.Column(sa.String)
    bid_id = sa.Column(sa.LargeBinary)
    tx_type = sa.Column(sa.Integer)


class SentOffer(Base):
    __tablename__ = 'sentoffers'

    offer_id = sa.Column(sa.LargeBinary, primary_key=True)

