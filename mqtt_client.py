import ubinascii
import ujson
from machine import unique_id
from umqtt.simple import MQTTClient

try:
    # Assume secrets.py contains a top-level 'secrets' dictionary
    from secrets import secrets

    MQTT_BROKER = secrets.get("mqtt_host")
    MQTT_PORT = secrets.get("mqtt_port", 0)  # Default to 0, will be checked
    MQTT_USER = secrets.get("mqtt_user", "")
    MQTT_PASS = secrets.get("mqtt_password", "")
    MQTT_USE_SSL = secrets.get("mqtt_use_ssl", False)  # New: Get SSL flag
except (ImportError, KeyError):
    print("Error: Could not import 'secrets.py' or 'mqtt_host' not found in 'secrets'.")
    print(
        "Please ensure secrets.py contains a 'secrets' dictionary with 'mqtt_host' and 'mqtt_port' keys."
    )
    MQTT_BROKER = None
    MQTT_PORT = 0
    MQTT_USER = ""
    MQTT_PASS = ""
    MQTT_USE_SSL = False


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
        if not MQTT_BROKER or not MQTT_PORT:
            raise ValueError(
                "MQTT_BROKER or MQTT_PORT is not defined or found in secrets.py"
            )

        self.client_id = ubinascii.hexlify(unique_id())
        self.broker = MQTT_BROKER
        self.port = MQTT_PORT
        self.user = MQTT_USER
        self.password = MQTT_PASS
        self.client = MQTTClient(
            self.client_id,
            self.broker,
            port=self.port,
            user=self.user,
            password=self.password,
            ssl=MQTT_USE_SSL,
        )  # Added ssl=MQTT_USE_SSL
        self.is_connected = False

    def connect(self):
        """
        Connects to the MQTT broker.
        Returns True on success, False on failure.
        """
        print(f"Connecting to MQTT broker at {self.broker}:{self.port}...")
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
        payload = ujson.dumps(sensor_data).encode("utf-8")

        try:
            print(f"Publishing to topic '{topic}': {payload}")
            self.client.publish(topic, payload)
        except Exception as e:
            print(f"Failed to publish message: {e}")
            # In a real-world scenario, you might want to try reconnecting here.
            self.is_connected = False
