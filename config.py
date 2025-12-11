"""
This file contains the configuration for all sensors.

It defines the GPIO pins and metadata for each sensor, such as its ID,
type, location, and measurement unit. This makes the main script cleaner
and the overall system easier to configure.

To add a new sensor, simply add a new entry to the SENSORS dictionary.
The key should be a unique identifier for the sensor (e.g., 'dht11_living_room'),
and the value should be a dictionary containing its configuration.
"""
from machine import Pin

# Pin for the onboard status LED (if available, e.g., on GPIO 2 for many ESP32 boards)
STATUS_LED_PIN = 2

# Main sensor configuration dictionary
SENSORS = {
    # Example 1: DHT11 Temperature and Humidity Sensor
    "dht11": {
        "pin": 14,
        "type": "DHT11",
        "location": "Living Room",
        "active": True,
        # DHT11 provides two values, so we define them here
        "provides": {
            "temperature": {"id": "Sensor_DHT11_Temp", "unit": "°C"},
            "humidity": {"id": "Sensor_DHT11_Hum", "unit": "%"}
        }
    },

    # Example 2: DS18B20 Temperature Sensor (1-Wire Bus)
    # Multiple DS18B20 sensors can be connected to the same pin.
    # The `sensors.py` script will discover them automatically.
    "ds18b20_bus": {
        "pin": 27,
        "type": "DS18B20",
        "location": "Basement",
        "active": True,
        "provides": {
            "temperature": {"id_prefix": "Sensor_DS18B20", "unit": "°C"}
        }
    },

    # Example 3: Simple Button
    "button": {
        "pin": 13,
        "type": "Button",
        "location": "Workshop",
        "active": True,
        "provides": {
            "state": {"id": "Sensor_Button_State", "unit": "boolean"}
        }
    },

    # Example 4: LDR (Light Dependent Resistor) - Analog Sensor
    "ldr": {
        "pin": 34,  # Use an ADC-capable pin
        "type": "LDR",
        "location": "Greenhouse",
        "active": True,
        "provides": {
            "light": {"id": "Sensor_LDR_Light", "unit": "raw"}
        }
    },
    
    # Example 5: GY-521 MPU6050 Gyro/Accelerometer (I2C)
    # The pins for I2C are often fixed on boards, but can be configured.
    "gy521": {
        "scl_pin": 22,
        "sda_pin": 21,
        "type": "GY521",
        "location": "Drone",
        "active": True,
        "provides": {
            "accel_x": {"id": "Sensor_GY521_AccelX", "unit": "g"},
            "accel_y": {"id": "Sensor_GY521_AccelY", "unit": "g"},
            "accel_z": {"id": "Sensor_GY521_AccelZ", "unit": "g"},
            "gyro_x": {"id": "Sensor_GY521_GyroX", "unit": "°/s"},
            "gyro_y": {"id": "Sensor_GY521_GyroY", "unit": "°/s"},
            "gyro_z": {"id": "Sensor_GY521_GyroZ", "unit": "°/s"},
            "temp": {"id": "Sensor_GY521_Temp", "unit": "°C"}
        }
    }
    
    # Add other sensors from your list here following the same structure.
    # For example, for a Soil Moisture Sensor (analog):
    # "soil_moisture": {
    #     "pin": 35,
    #     "type": "SoilMoisture",
    #     "location": "Garden",
    #     "active": True,
    #     "provides": {
    #         "moisture": {"id": "Sensor_Soil_Moisture", "unit": "%"}
    #     }
    # }
}
