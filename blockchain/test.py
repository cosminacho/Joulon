from transaction import Transaction
from block import Block
from wallet import Wallet
import json
import paho.mqtt.client as mqtt
from utility.constants import SUN, MQTT
import ssl


wallet1 = Wallet("Nacho")
wallet2 = Wallet("Mada")
wallet3 = Wallet("Mihai")

wallet1.create_keys()
wallet2.create_keys()
wallet3.create_keys()


client = mqtt.Client()
client.tls_set_context(ssl.create_default_context())
client.username_pw_set(MQTT.USERNAME, MQTT.PASSWORD)
# client.will_set('remove_peer_node', payload=SUN.ID, qos=2)
client.on_connect = on_connect
#client.on_message = on_message
#client.on_disconnect = on_disconnect
client.connect(MQTT.SERVER, int(MQTT.SSL_PORT))
# client.loop_forever()


def on_connect(client, userdata, flags, rc):
    client.publish("new_transaction", )


t2 = Transaction(SUN.PUBLIC_KEY, wallet1.public_key, 50)

t1 = Transaction(wallet1.public_key, wallet2.public_key, 20, "Ceva")
signature = wallet1.sign_transaction(t1)
t1.add_signature(signature)


t1 = Transaction("Eu", "tu", 200)
t2 = Transaction("El", "ea", 100)
t3 = Transaction("EU", "mie", 50)
b1 = Block(1, "eu", 100, [t1, t2], 'ceva')
b2 = Block(1, "EU", 50, [t3], 'cevass')
chain = [b1, b2]


# # print(json.dumps(b1.__dict__))
# [block.__dict__ for block in chain]
# block.transactions = [tx.__dict__ for tx in block.transactions] for block
# b1.transactions = [tx.__dict__ for tx in b1.transactions]
# print(json.dumps(b1.__dict__))

new_chain = []
for block in chain:
    block.transactions = [tx.__dict__ for tx in block.transactions]
    new_chain.append(block.__dict__)
print(json.dumps(new_chain))


# print(json.dumps([t1.__dict__, t2.__dict__, t3.__dict__]))
# print("\n\n\n")
# print(json.dumps([]))
