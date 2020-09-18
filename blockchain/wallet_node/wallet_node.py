from flask import Flask, jsonify, request
from flask_cors import CORS

from transaction import Transaction
from wallet import Wallet

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def blank_page():
    return "Joulon Wallet API", 200


@app.route('/new_wallet', methods=['POST'])
def new_wallet():
    private_key, public_key = Wallet.generate_keys()
    response = {
        'private_key': private_key,
        'public_key': public_key
    }
    return jsonify(response), 200


@app.route('/sign_transaction', methods=['POST'])
def sign_transaction():
    requested_object = request.get_json()

    wall = requested_object['wallet']
    wallet_id = wall['wallet_id']
    private_key = wall['private_key']
    public_key = wall['public_key']
    wallet = Wallet(wallet_id, private_key, public_key)

    trans = requested_object['transaction']
    sender = trans['sender']
    recipient = trans['recipient']
    amount = trans['amount']
    description = trans['description']
    transaction = Transaction(sender, recipient, amount, description)

    signature = wallet.sign_transaction(transaction)
    transaction.add_signature(signature)

    response = transaction.__dict__
    return jsonify(response), 200


if __name__ == '__main__':
    app.run()
