import ujson
import time
import ubinascii
from machine import unique_id
from umqtt.simple import MQTTClient

try:
    from secrets import MQTT_BROKER, MQTT_USER, MQTT_PASS
except ImportError:
    print("Error: Could not import 'secrets.py'. Please create it.")
    MQTT_BROKER = None
    MQTT_USER = ""
    MQTT_PASS = ""

class MQTT:
    """
    A wrapper class for the umqtt.simple.MQTTClient.
    Handles connection, publishing, and disconnection.
    Formats and sends sensor data as JSON payloads.
    """
    def __init__(self):
        """
        Initializes the MQTT client.
        """
        if not MQTT_BROKER:
            raise ValueError("MQTT_BROKER is not defined in secrets.py")
            
        self.client_id = ubinascii.hexlify(unique_id())
        self.broker = MQTT_BROKER
        self.user = MQTT_USER
        self.password = MQTT_PASS
        self.client = MQTTClient(self.client_id, self.broker, user=self.user, password=self.password)
        self.is_connected = False

    def connect(self):
        """
        Connects to the MQTT broker.
        Returns True on success, False on failure.
        """
        print(f"Connecting to MQTT broker at {self.broker}...")
        try:
            self.client.connect()
            self.is_connected = True
            print("MQTT connected successfully.")
            return True
        except OSError as e:
            print(f"Failed to connect to MQTT broker: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """
        Disconnects from the MQTT broker.
        """
        if self.is_connected:
            print("Disconnecting from MQTT broker.")
            self.client.disconnect()
            self.is_connected = False

    def publish(self, topic_suffix, sensor_data):
        """
        Publishes a message to a specific MQTT topic.
        
        Args:
            topic_suffix (str): The sensor type or specific identifier for the topic.
            sensor_data (dict): A dictionary containing the sensor reading payload.
                                Example: {"id": "Sensor_ID", "value": 25.5, ...}
        """
        if not self.is_connected:
            print("Cannot publish, MQTT client is not connected.")
            return

        topic = f"Sensor/{topic_suffix}"
        payload = ujson.dumps(sensor_data)
        
        try:
            print(f"Publishing to topic '{topic}': {payload}")
            self.client.publish(topic, payload)
        except Exception as e:
            print(f"Failed to publish message: {e}")
            # In a real-world scenario, you might want to try reconnecting here.
            self.is_connected = False
