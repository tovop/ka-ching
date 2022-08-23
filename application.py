"""
Web application hosting core API.
"""
from flask import Flask, jsonify
from core.chain import Blockchain


blockchain = Blockchain()
app = Flask(__name__)


@app.route("/transactions", methods=["GET"])
def get_transactions():
    return jsonify(blockchain.unconfirmed_transactions), 200


@app.route("/chain", methods=["GET"])
def get_chain():
    chain_data = [block.__dict__ for block in blockchain.blocks]
    data = dict(length=len(chain_data), chain=chain_data)
    return jsonify(data), 200


@app.route("/verify", methods=["GET"])
def verify_chain():
    valid, details = blockchain.verify()

    if valid:
        response = dict(message="The Blockchain is valid")
    else:
        response = dict(message="The Blockchain is not valid", details=details)
    return jsonify(response), 200


app.run(debug=True, port=5000)
