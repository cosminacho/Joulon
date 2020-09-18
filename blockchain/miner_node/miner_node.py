import paho.mqtt.client as mqtt
import sys
import atexit
import ssl
import json
import time
import serial
from block import Block
from blockchain import Blockchain
from transaction import Transaction

from wallet import Wallet
from utility.constants import MQTT, SUN, SERIAL
from utility.verification import Verification

ser = serial.Serial(SERIAL.PORT, SERIAL.BAUDRATE)


first_time = False

try:
    with open("node.txt", mode="r") as f:
        content = f.readlines()
        NODE_ID = content[0][:-1]
        status = content[1]
except(IOError, IndexError):
    print("Failed to load data from file...")
    sys.exit()


wallet = Wallet(NODE_ID)
if status == "no_wallet":
    wallet.create_keys()
    wallet.save_keys()
    try:
        with open("node.txt", mode="w") as f:
            f.write(NODE_ID)
            f.write("\n")
            f.write("has_wallet")

    except (IndexError, IOError):
        print("Failed to save data in node.txt...")
    first_time = True
else:
    wallet.load_keys()


blockchain = Blockchain(wallet.node_id, wallet.public_key)
winner_chain = blockchain.get_chain()


# def on_exit():
#     blockchain.save_data()


# atexit.register(on_exit)


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
    client.publish(f"resolve_conflicts/{payload}", json.dumps(response), qos=2)


def remove_peer_node(client, payload):
    blockchain.remove_peer_node(payload)


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
    if count >= 3 or mine_count >= 3:
        node_id, proof = blockchain.proof_of_stake()
        if node_id == blockchain.public_key:
            mined_block = blockchain.mine_block()
            signature = wallet.sign_block(mined_block)
            mined_block.add_signature(signature)
            mined_block.transactions = [
                tx.__dict__ for tx in mined_block.transactions]
            mined_block = mined_block.__dict__
            client.publish(mined_block)
            client.publish("new_block", json.dumps(mined_block), qos=2)


def new_block(client, payload):
    block = json.loads(payload)
    block = Block.create_object(block)
    blockchain.add_block(block)


def get_balance(client, node_id, public_key):
    amount = blockchain.get_balance(public_key)
    client.publish(f"return_balance/{node_id}", str(amount), qos=2)


def connect_wallet(client, payload):
    old_node = blockchain.node_id
    NODE_ID = payload
    wallet.node_id = NODE_ID
    wallet.save_keys()
    blockchain.node_id = NODE_ID

    client.unsubscribe([
        f"connect_wallet/{old_node}",
        f"get_balance/{old_node}",
        f"resolve_conflicts/{old_node}",
        f"return_keys/{old_node}"
    ])
    client.subscribe([
        (f"get_balance/{NODE_ID}", 2),
        (f"resolve_conflicts/{NODE_ID}", 2)
    ])
    client.user_data_set(NODE_ID)
    try:
        with open("node.txt", mode="w") as f:
            f.write(NODE_ID)
            f.write("\n")
            f.write("has_connected_wallet")

    except(IOError, IndexError):
        print("Couldn't write the file...")


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


def return_keys(client, payload):
    private_key, public_keys = wallet.get_keys()
    response = {
        "private_key": private_key,
        "public_key": public_keys
    }
    client.publish(f"get_keys/{payload}", json.dumps(response), qos=2)


def on_connect(client, userdata, flags, rc):
    print("Connected")

    client.subscribe([
        ("add_peer_node", 2),
        ("remove_peer_node", 2),
        ("new_transaction", 2),
        ("new_block", 2),
        (f"get_balance/{userdata}", 2),
        (f"resolve_conflicts/{userdata}", 2)
    ])

    if status == "no_wallet" or status == "has_wallet":
        client.subscribe([
            (f"connect_wallet/{userdata}", 2),
            (f"return_keys/{userdata}", 2)
        ])

    client.publish("add_peer_node", payload=userdata, qos=2)

    if first_time:
        response = {
            'node_id': userdata,
            'public_key': blockchain.public_key
        }
        client.publish("new_prosumer", payload=json.dumps(response), qos=2)


def on_message(client, userdata, message):
    switcher = {
        "add_peer_node": add_peer_node,
        "remove_peer_node": remove_peer_node,
        "new_transaction": new_transaction,
        "new_block": new_block,
        f"connect_wallet/{blockchain.node_id}": connect_wallet,
        f"resolve_conflicts/{blockchain.node_id}": resolve_conflicts,
        f"return_public_key/{blockchain.node_id}": return_keys
    }
    if (message.topic.split("/")[0] == "get_balance"):
        get_balance(client, message.topic.split(
            "/")[1], message.payload.decode())
    else:
        func = switcher.get(message.topic, lambda: "Invalid topic")
        func(client, message.payload.decode())


def on_disconnect(client, userdata, rc):
    blockchain.save_data()
    client.publish('remove_peer_node', payload=userdata, qos=2)
    client.loop_stop()


client = mqtt.Client()
client.tls_set_context(ssl.create_default_context())
client.username_pw_set(MQTT.USERNAME, MQTT.PASSWORD)
client.user_data_set(NODE_ID)
client.will_set('remove_peer_node', payload=NODE_ID, qos=2)
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.connect(MQTT.SERVER, int(MQTT.SSL_PORT))
client.loop_start()
while True:
    if ser.in_waiting:
        read_data = int(ser.readline().decode().rstrip())
        trans = Transaction(SUN.PUBLIC_KEY, blockchain.public_key, read_data)
        to_send = json.dumps(trans.__dict__)
        client.publish('new_sun_transaction', payload=to_send, qos=2)
