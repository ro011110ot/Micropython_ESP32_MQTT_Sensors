import time

import network
from machine import Pin

try:
    # Assume secrets.py contains a top-level 'secrets' dictionary
    from secrets import secrets

    WIFI_CREDENTIALS = secrets.get("wifi_credentials")
    from config import STATUS_LED_PIN
except (ImportError, KeyError):
    print(
        "Error: Could not import 'secrets.py' or 'config.py', or 'wifi_credentials' not found in 'secrets'."
    )
    print(
        "Please ensure secrets.py contains a 'secrets' dictionary with a 'wifi_credentials' list."
    )
    WIFI_CREDENTIALS = None
    STATUS_LED_PIN = None


def connect_wifi():
    """
    Connects the device to the Wi-Fi network using credentials from secrets.py.
    It tries each network in the 'wifi_credentials' list until a connection is established.
    Blinks the status LED while connecting.
    """
    if not all([WIFI_CREDENTIALS, STATUS_LED_PIN is not None]):
        print("Wi-Fi credentials or STATUS_LED_PIN are not configured. Halting.")
        return False

    led = Pin(STATUS_LED_PIN, Pin.OUT)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        print("Wi-Fi already connected.")
        print("Network config:", wlan.ifconfig())
        led.on()
        return True

    for creds in WIFI_CREDENTIALS:
        ssid = creds.get("ssid")
        password = creds.get("password")

        if not ssid:
            continue  # Skip if SSID is missing

        print(f"Connecting to network '{ssid}'...")
        wlan.connect(ssid, password)

        # Wait for connection with a timeout and LED blinking
        max_wait = 15  # seconds
        while max_wait > 0:
            if wlan.isconnected():
                break
            max_wait -= 1
            led.on()
            time.sleep(0.1)
            led.off()
            time.sleep(0.4)

        if wlan.isconnected():
            print("Wi-Fi connected.")
            print("Network config:", wlan.ifconfig())
            led.off()  # Keep LED on to indicate successful connection
            return True
        else:
            print(f"Failed to connect to '{ssid}'. Trying next network...")
            wlan.disconnect()  # Disconnect before trying next
            time.sleep(1)  # Small delay before next attempt

    print("Wi-Fi connection failed for all configured networks.")
    # Fast blink to indicate error
    for _ in range(10):
        led.on()
        time.sleep(0.1)
        led.off()
        time.sleep(0.1)
    return False
