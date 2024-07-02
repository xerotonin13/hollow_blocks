import sys

import hashlib
import json

from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

import requests
from urllib.parse import urlparse

class Blockchain(object):

    difficulty_target = "0000"

    def hash_block(self, block):
        block_encoded = json.dumps(block,
            sort_keys=True).encode()
        return hashlib.sha256(block_encoded).hexdigest()
    
    def _init_(self):
        self.chain = []
        self.current_transactions = []
    
    #Finding the nonce
    def proof_of_work(self, index, hash_of_previous_block, transactions):
        nonce = 0
        while self.valid_proof(index, hash_of_previous_block, transactions, nonce)is False: 
            nonce += 1
        return nonce 
    
    def valid_proof(self, index, hash_of_previous_block, transactions, nonce):
        content = f'{index}{hash_of_previous_block}{transactions}{nonce}'.encode()
        content_hash = hashlib.sha256(content).hexdigest()
        return content_hash[:len(self.difficulty_target)] == self.difficulty_target
    @property
    def last_block(self):
        return self.chain[-1]
    
#Exposing the Blockchain class as a REST API
app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', "")
    
blockchain = Blockchain()

#Obtaining the Full Blockchain
@app.route('/blockchain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
        }
    return jsonify(response), 200

#Adding Transactions
@app.route('/transactions/new', methods=['POST'])
def new_transaction():

    values = request.get_json()

    required_fields = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required_fields):
        return ('Missing fields', 400)
    
    index = blockchain.add_transaction(
    values['sender'],
    values['recipient'],
    values['amount']
    )

    response = {'message':
        f'Transaction will be added to Block {index}'}
    return (jsonify(response), 201)