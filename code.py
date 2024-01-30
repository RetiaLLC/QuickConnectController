import time
import wifi
import socketpool
import ssl
import adafruit_requests
import board
import digitalio
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer
import busio
import displayio
import adafruit_displayio_sh1106
import os

# WiFi credentials
ssid = os.getenv("CIRCUITPY_WIFI_SSID")
passwd = os.getenv("CIRCUITPY_WIFI_PASSWORD")

# Connect to WiFi
wifi.radio.connect(ssid=ssid, password=passwd)
print("Connected with IP:", wifi.radio.ipv4_address)

# Set up display
displayio.release_displays()
WIDTH, HEIGHT = 130, 64  # Display size
i2c = busio.I2C(board.SCL, board.SDA)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
display = adafruit_displayio_sh1106.SH1106(display_bus, width=WIDTH, height=HEIGHT)

# Initialize down button
down_button_pin = DigitalInOut(board.IO18)  # Use the correct pin for your down button
down_button_pin.pull = Pull.UP
down_button = Debouncer(down_button_pin)

# Function to send reboot request
def send_reboot_request():
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())

    # Device info and API endpoint
    device_ip = os.getenv("TARGET_IP")
    device_password = os.getenv("TARGET_PASSWORD")
    url = f"http://{device_ip}/remoteReset"
    data = {'password': device_password}

    # Send POST request
    response = requests.post(url, data=data)
    return response

# Main loop
print("RESTART ROUTER:")
print("PRESS DOWN BUTTON")
while True:
    down_button.update()

    if down_button.fell:
        print("Sending reboot request...")
        response = send_reboot_request()
        print(f"Response: {response.status_code}\n{response.text}")

        print("DONE!")
        time.sleep(10)  # Wait for 10 seconds

    time.sleep(0.1)  # Small delay to reduce CPU usage
