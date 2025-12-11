# ESP32 MQTT Multi-Sensor Hub

This MicroPython project provides a flexible and extensible framework for reading data from a wide variety of sensors on an ESP32 and publishing it to an MQTT broker. The system is designed to be modular, making it easy to configure, extend, and maintain.

## Features

- **Modular Design**: Code is split into logical modules for Wi-Fi, NTP, MQTT, sensor configuration, and sensor reading.
- **Centralized Configuration**: All sensor pins and metadata are defined in a single `config.py` file.
- **Extensible Sensor Support**: A clear structure is provided to add new sensor types.
- **Robust Operation**: Includes basic error handling and reconnection logic for Wi-Fi and MQTT.
- **Standard Data Format**: Publishes data in a clean JSON format, ready for consumption by other services (e.g., storing in a database).

## Project Structure

```
.
├── main.py           # Main script, orchestrates everything
├── config.py         # Sensor GPIOs, IDs, and metadata configuration
├── secrets.py        # (You must create this) Wi-Fi and MQTT credentials
├── wifi.py           # Handles Wi-Fi connection
├── ntp.py            # Handles RTC time synchronization
├── mqtt_client.py    # Handles MQTT connection and publishing
├── sensors.py        # Logic for reading all hardware sensors
└── README.md         # This file
```

---

## Getting Started

Follow these steps to get the project running on your ESP32.

### 1. Prerequisites

- An ESP32 board flashed with a recent version of MicroPython.
- A tool to upload files to your ESP32 (e.g., `ampy`, `rshell`, or the Thonny IDE).

### 2. Install Dependencies

This project requires a few external libraries. Connect your ESP32 to a network with internet access, then open a REPL (e.g., in Thonny or via `screen`/`picocom`) and run the following commands to install them using `mip` (MicroPython Install Package):

```python
import mip

# For MQTT communication
mip.install('umqtt.simple')

# For the DHT11/DHT22 sensor
mip.install('dht')

# For the DS18B20 1-Wire temperature sensor
mip.install('ds18x20')
```
*Note: The `onewire` library is built-in with the `ds18x20` library.*

### 3. Create `secrets.py`

You must create a file named `secrets.py` in the root directory. This file stores your sensitive credentials and is ignored by Git (you should add it to your `.gitignore` file if it's not already there).

Copy the following content into your `secrets.py` and fill in your details:

```python
# secrets.py

# Wi-Fi Credentials
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASS = "YOUR_WIFI_PASSWORD"

# MQTT Broker Credentials
MQTT_BROKER = "YOUR_BROKER_IP_ADDRESS"  # e.g., "192.168.1.100"
MQTT_USER = "YOUR_MQTT_USERNAME"        # Leave as "" if no user
MQTT_PASS = "YOUR_MQTT_PASSWORD"        # Leave as "" if no password
```

### 4. Configure Your Sensors in `config.py`

Open the `config.py` file. This is where you define which sensors are connected to which GPIO pins. The file is pre-populated with examples (DHT11, DS18B20, Button, LDR, GY-521).

- **Adjust Pins**: Change the `pin`, `scl_pin`, and `sda_pin` values to match your hardware wiring.
- **Set Metadata**: Update the `id`, `location`, and `unit` for each sensor to match your setup.
- **Activate/Deactivate**: Set `"active": True` for sensors you want to read, and `"active": False` for those you want to ignore.
- **Add New Sensors**: Add new entries to the `SENSORS` dictionary for other sensors.

### 5. Upload Files

Upload all the project files (`main.py`, `config.py`, `secrets.py`, `wifi.py`, `ntp.py`, `mqtt_client.py`, `sensors.py`) to the root directory of your ESP32.

### 6. Run

The script is designed to run automatically on boot if you rename `main.py` to `boot.py`. However, for testing, it's best to run it manually from the REPL first:

```python
import main
main.main()
```

You should see log messages in your REPL showing the Wi-Fi connection, NTP sync, MQTT connection, and finally the sensor reading loop.

---

## How to Add a New Sensor

Let's say you want to add a Soil Moisture sensor, which is a simple analog sensor.

1.  **Update `config.py`**:
    Add a new entry to the `SENSORS` dictionary.

    ```python
    # In config.py
    SENSORS = {
        # ... other sensors
        "soil_moisture": {
            "pin": 35,  # Choose an ADC-capable pin
            "type": "SoilMoisture",
            "location": "Garden",
            "active": True,
            "provides": {
                "moisture": {"id": "Sensor_Soil_Moisture", "unit": "%"}
            }
        }
    }
    ```

2.  **Update `sensors.py`**:
    a. Create a new reader function, for example `_read_soil_moisture`. You can copy `_read_ldr` as a template.

    ```python
    # In sensors.py
    def _read_soil_moisture(config):
        try:
            adc = ADC(Pin(config['pin']))
            adc.atten(ADC.ATTN_11DB)
            raw_value = adc.read()
            # You might want to convert the raw value to a percentage here
            # This depends on your sensor's characteristics (min/max values)
            # For now, we'll just use the raw value.
            percent_value = (raw_value / 4095) * 100
            
            return [{
                'type': config['type'],
                'data': {
                    'id': config['provides']['moisture']['id'],
                    'value': round(100 - percent_value, 2), # Often these sensors are inverted
                    'unit': config['provides']['moisture']['unit'],
                    'location': config['location'],
                    'active': config['active']
                }
            }]
        except Exception as e:
            print(f"Error reading Soil Moisture sensor: {e}")
            return []
    ```

    b. Add a call to this new function in the `read_all_sensors` main loop.

    ```python
    # In sensors.py, inside read_all_sensors()
    # ...
    elif config['type'] == 'GY521':
        all_readings.extend(_read_gy521(config))
    elif config['type'] == 'SoilMoisture': # Add this block
        all_readings.extend(_read_soil_moisture(config))
    else:
        print(f"Warning: No reader function for type '{config['type']}'")
    ```

By following this pattern, you can integrate all 45 of your sensors into the framework.