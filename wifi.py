import network
import time
from machine import Pin
try:
    from secrets import WIFI_SSID, WIFI_PASS
    from config import STATUS_LED_PIN
except ImportError:
    print("Error: Could not import 'secrets.py' or 'config.py'.")
    print("Please create these files and define the required variables.")
    WIFI_SSID = None
    WIFI_PASS = None
    STATUS_LED_PIN = None

def connect_wifi():
    """
    Connects the device to the Wi-Fi network using credentials from secrets.py.
    Blinks the status LED while connecting.
    """
    if not all([WIFI_SSID, WIFI_PASS, STATUS_LED_PIN is not None]):
        print("Wi-Fi credentials or STATUS_LED_PIN are not configured. Halting.")
        return False

    led = Pin(STATUS_LED_PIN, Pin.OUT)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print(f"Connecting to network '{WIFI_SSID}'...")
        wlan.connect(WIFI_SSID, WIFI_PASS)

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
            led.on()  # Keep LED on to indicate successful connection
            return True
        else:
            print("Wi-Fi connection failed.")
            # Fast blink to indicate error
            for _ in range(10):
                led.on()
                time.sleep(0.1)
                led.off()
                time.sleep(0.1)
            return False
    else:
        print("Wi-Fi already connected.")
        print("Network config:", wlan.ifconfig())
        led.on()
        return True
