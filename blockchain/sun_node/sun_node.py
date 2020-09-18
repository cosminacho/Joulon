import paho.mqtt.client as mqtt

import atexit
import ssl
import json

from block import Block
from blockchain import Blockchain
from transaction import Transaction

from wallet import Wallet
from utility.constants import MQTT, SUN
from utility.verification import Verification

wallet = Wallet(SUN.ID, SUN.PRIVATE_KEY, SUN.PUBLIC_KEY)
blockchain = Blockchain(SUN.ID, SUN.PUBLIC_KEY)
winner_chain = blockchain.get_chain()


# def on_exit():
#     blockchain.save_data()


# atexit.register(on_exit)


def connect_wallet(client, old_node, payload):
    try:
        with open("registered_prosumers.txt", mode="a+") as f:
            prosumers = f.readlines()
            for prosumer in prosumers:
                if old_node == prosumer[:-1]:
                    f.write(payload)
                    f.write("\n")
                    break
    except (IOError, IndexError):
        print("Failed to open file...")


def resolve_conflicts(client, payload):
    data = json.loads(payload)
    if data['node_id'] == blockchain.node_id:
        pass
    else:
        blockchain.add_peer_node(data['node_id'])
        chain = [Block.create_object(block) for block in data['chain']]
        if len(chain) >= len(winner_chain) and Verification.verify_chain(chain):
            winner_chain = chain
            blockchain.set_chain(winner_chain)
            open_transactions = [Transaction.create_object(
                tx) for tx in data['transactions']]
            blockchain.set_open_transactions(open_transactions)
            blockchain.save_data()


def get_balance(client, node_id, public_key):
    try:
        with open("prosumers.txt", mode="r") as f:
            prosumers = f.readlines()
            peer_nodes = blockchain.get_set_peer_nodes()
            for prosumer in prosumers:
                if public_key == prosumer[:-1] and public_key in peer_nodes:
                    return
    except (IOError, IndexError):
        print("Failed to load data from a file...")
    amount = blockchain.get_balance(public_key)
    client.publish(f"return_balance/{node_id}", str(amount), qos=2)


def add_peer_node(client, payload):
    blockchain.add_peer_node(payload)

    chain = blockchain.get_chain()
    open_transactions = blockchain.get_open_transactions()
    transformed_transactions = [tx.__dict__ for tx in open_transactions]
    transformed_chain = []
    for block in chain:
        block.transactions = [tx.__dict__ for tx in block.transactions]
        transformed_chain.append(block.__dict__)
    response = {
        "chain": transformed_chain,
        "transactions": transformed_transactions,
        "node_id": blockchain.node_id
    }
    client.publish(f"resolve_conflics/{payload}", json.dumps(response), qos=2)


def remove_peer_node(client, payload):
    blockchain.remove_peer_node(payload)


def new_prosumer(client, payload):

    data = json.loads(payload)
    found = False
    try:
        with open("registered_prosumers.txt", mode="r") as f:
            prosumers = f.readlines()
            for prosumer in prosumers:
                if prosumer[:-1] == data['node_id']:
                    found = True
                    break
    except (IOError, IndexError):
        print("Failed to load data from a file...")
    if found:
        try:
            with open("prosumers.txt", mode="a") as f:
                f.write(data['public_key'])
                f.write("\n")
        except (IOError, IndexError):
            print("Failed to write data to file...")
    else:
        print("Failed to add new prosumer.")


def new_transaction(client, payload):
    transaction = json.loads(payload)
    transaction = Transaction.create_object(transaction)
    blockchain.add_transaction(transaction)
    count = 0
    mine_count = 0
    for tx in blockchain.get_open_transactions():
        if tx.sender != SUN.PUBLIC_KEY:
            count += 1
        else:
            mine_count += 1
    if count >= 3 or mine_count >= 10:
        node_id, proof = blockchain.proof_of_stake()
        if node_id == blockchain.public_key:
            mined_block = blockchain.mine_block()
            signature = wallet.sign_block(mined_block)
            mined_block.add_signature(signature)
            mined_block.transactions = [
                tx.__dict__ for tx in mined_block.transactions]
            mined_block = mined_block.__dict__
            client.publish("new_block", json.dumps(mined_block), qos=2)
    if count >= 5 or mine_count >= 15:
        proof += 100
        helper_trans = Transaction(
            SUN.PUBLIC_KEY, SUN.PUBLIC_KEY, proof, "MINING FIX")
        signature = wallet.sign_transaction(helper_trans)
        helper_trans.add_signature(signature)
        client.publish("new_transaction", json.dumps(helper_trans), qos=2)


def new_sun_transaction(client, payload):
    transaction = json.loads(payload)
    transaction = Transaction.create_object(transaction)
    found = False
    try:
        with open("prosumers.txt", mode="r") as f:
            prosumers = f.readlines()
            for prosumer in prosumers:
                if prosumer[:-1] == transaction.recipient:
                    found = True
                    break
    except (IOError, IndexError):
        print("Failed to load data from a file...")
    if found:
        signature = wallet.sign_transaction(transaction)
        transaction.add_signature(signature)
        ready_transaction = json.dumps(transaction.__dict__)
        client.publish("new_transaction", ready_transaction, qos=2)
    else:
        print("Failed to sign new sun transaction.")


def new_block(client, payload):
    block = json.loads(payload)
    block = Block.create_object(block)
    blockchain.add_block(block)


def on_connect(client, userdata, flags, rc):
    print("Connected")
    client.subscribe([
        ("new_transaction", 2),
        ("new_block", 2),
        ("new_sun_transaction", 2),
        ("add_peer_node", 2),
        ("remove_peer_node", 2),
        ("new_prosumer", 2),
        ("get_balance/#", 2),
        ("connect_wallet/#", 2),
        (f"resolve_conflicts/{SUN.ID}", 2)
    ])
    client.publish('add_peer_node', payload=SUN.ID, qos=2)


def on_disconnect(client, userdata, rc):
    blockchain.save_data()
    client.publish('remove_peer_node', payload=SUN.ID, qos=2)


def on_message(client, userdata, message):
    switcher = {
        "add_peer_node": add_peer_node,
        "remove_peer_node": remove_peer_node,
        "new_transaction": new_transaction,
        "new_block": new_block,
        "new_sun_transaction": new_sun_transaction,
        "new_prosumer": new_prosumer,
        f"resolve_conflics/{SUN.ID}": resolve_conflicts
    }
    if (message.topic.split("/")[0] == "get_balance"):
        get_balance(client, message.topic.split(
            "/")[1], message.payload.decode())
    elif (message.topic.split("/")[0] == "connect_wallet"):
        connect_wallet(client, message.topic.split("/")
                       [1], message.payload.decode())
    else:
        func = switcher.get(message.topic, lambda: "Invalid topic")
        func(client, message.payload.decode())


client = mqtt.Client()
client.tls_set_context(ssl.create_default_context())
client.username_pw_set(MQTT.USERNAME, MQTT.PASSWORD)
client.will_set('remove_peer_node', payload=SUN.ID, qos=2)
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.connect(MQTT.SERVER, int(MQTT.SSL_PORT))
client.loop_forever()
