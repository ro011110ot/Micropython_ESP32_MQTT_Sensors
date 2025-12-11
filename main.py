"""
Main script for the ESP32 MQTT Sensor Hub.

This script orchestrates the entire process:
1. Connects to the Wi-Fi network.
2. Synchronizes the real-time clock (RTC) with an NTP server.
3. Initializes and connects the MQTT client.
4. Enters a continuous loop to read all configured sensors and publish
   their data to the MQTT broker.
"""
import time
from machine import Pin

# Import custom modules
import wifi
import ntp
from mqtt_client import MQTT
from sensors import read_all_sensors
try:
    from config import STATUS_LED_PIN
except ImportError:
    STATUS_LED_PIN = None

# --- Configuration ---
# Time to wait between sensor reading cycles (in seconds)
LOOP_INTERVAL_SEC = 60

def main():
    """
    Main execution function.
    """
    # Initialize status LED
    status_led = None
    if STATUS_LED_PIN is not None:
        status_led = Pin(STATUS_LED_PIN, Pin.OUT)
        status_led.off() # Start with LED off

    # --- Step 1: Connect to Wi-Fi ---
    if not wifi.connect_wifi():
        print("Could not connect to Wi-Fi. Halting execution.")
        # Blink LED rapidly to indicate fatal error
        if status_led:
            for _ in range(20):
                status_led.on()
                time.sleep(0.1)
                status_led.off()
                time.sleep(0.1)
        return # Stop everything

    # --- Step 2: Synchronize Time ---
    ntp.sync_time()

    # --- Step 3: Initialize and Connect MQTT Client ---
    mqtt = None
    try:
        mqtt = MQTT()
        if not mqtt.connect():
            print("Could not connect to MQTT. Halting execution.")
            # Consider a retry mechanism for more robustness
            return
            
        # --- Step 4: Main Loop ---
        print("\n--- Starting main sensor loop ---")
        while True:
            # Re-check MQTT connection and reconnect if necessary
            if not mqtt.is_connected:
                print("MQTT disconnected. Attempting to reconnect...")
                if not mqtt.connect():
                    print("Reconnect failed. Waiting before next attempt.")
                    time.sleep(30)
                    continue # Skip this loop iteration

            # Read all sensors
            sensor_readings = read_all_sensors()

            # Publish each reading
            if sensor_readings:
                for reading in sensor_readings:
                    mqtt.publish(reading['type'], reading['data'])
                    time.sleep(0.1) # Small delay between messages
            else:
                print("No sensor readings to publish.")

            # Wait for the next cycle
            print(f"--- Loop finished. Waiting for {LOOP_INTERVAL_SEC} seconds. ---")
            time.sleep(LOOP_INTERVAL_SEC)

    except KeyboardInterrupt:
        print("\nExecution stopped by user (Ctrl+C).")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # --- Cleanup ---
        if mqtt:
            mqtt.disconnect()
        if status_led:
            status_led.off()
        print("Cleanup complete. Device halted.")


if __name__ == "__main__":
    main()
