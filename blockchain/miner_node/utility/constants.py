from dotenv import load_dotenv
import os

load_dotenv()

__all__ = ['MQTT', 'SERIAL', 'SUN']


class MQTT:
    SERVER = os.environ.get('MQTT_SERVER')
    USERNAME = os.environ.get('MQTT_USERNAME')
    PASSWORD = os.environ.get('MQTT_PASSWORD')
    PORT = os.environ.get('MQTT_PORT')
    SSL_PORT = os.environ.get('MQTT_SSL_PORT')


class SERIAL:
    PORT = os.environ.get('SERIAL_PORT')
    BAUDRATE = os.environ.get('SERIAL_BAUDRATE')


class SUN:
    ID = os.environ.get('SUN_ID')
    PUBLIC_KEY = os.environ.get('SUN_PUBLIC_KEY')
    PRIVATE_KEY = os.environ.get('SUN_PRIVATE_KEY')
