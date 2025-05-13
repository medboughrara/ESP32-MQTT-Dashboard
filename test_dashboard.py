# test_dashboard.py

import paho.mqtt.client as mqtt
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.dates import DateFormatter
import threading
from datetime import datetime
import time  # <-- Added missing import causing NameError
import numpy as np

# MQTT Broker Settings
MQTT_BROKER = "********"  # Replace with your MQTT broker address
MQTT_USERNAME = "********"  # Replace with your MQTT username
MQTT_PASSWORD = "********"  # Replace with your MQTT password
MQTT_PORT = 1883
MQTT_TOPICS = [
    "sensors/esp32/esp32_living_room/temperature",
    "sensors/esp32/esp32_living_room/humidity"
]

# Data storage
sensor_data = {
    'temperature': [],
    'humidity': []
}

# Lock for thread-safe updates
data_lock = threading.Lock()

# MQTT Callbacks
def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected with result code {rc}")
    for topic in MQTT_TOPICS:
        client.subscribe(topic)
        print(f"Subscribed to {topic}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        topic_parts = msg.topic.split('/')
        if len(topic_parts) >= 4:
            sensor_type = topic_parts[3]
            value = float(payload.get('value', 0))
            timestamp = datetime.now()
            with data_lock:
                sensor_data[sensor_type].append((timestamp, value))
                # Keep only last 100 points
                if len(sensor_data[sensor_type]) > 100:
                    sensor_data[sensor_type].pop(0)
    except Exception as e:
        print(f"Error processing message: {e}")

# Setup MQTT Client
mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")
    exit(1)

mqtt_client.loop_start()

# Real-time Plotting
fig, axs = plt.subplots(2, 1, figsize=(10, 6))
plt.subplots_adjust(hspace=0.5)

def update_plot(frame):
    with data_lock:
        temp_data = sensor_data['temperature']
        hum_data = sensor_data['humidity']

    axs[0].clear()
    axs[1].clear()

    if temp_data:
        times, temps = zip(*temp_data)
        axs[0].plot(times, temps, label='Temperature (°C)', color='tab:blue')
        axs[0].set_title("Temperature Over Time")
        axs[0].set_ylabel("°C")
        axs[0].grid(True)
        axs[0].xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
        axs[0].legend()

    if hum_data:
        times, hums = zip(*sensor_data['humidity'])
        axs[1].plot(times, hums, label='Humidity (%)', color='tab:orange')
        axs[1].set_title("Humidity Over Time")
        axs[1].set_ylabel("%")
        axs[1].grid(True)
        axs[1].xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
        axs[1].legend()

    return axs

# Create animation with save_count to suppress warning
ani = animation.FuncAnimation(fig, update_plot, interval=1000, save_count=100)

# Print latest values in terminal
def print_values():
    while True:
        with data_lock:
            temp = sensor_data['temperature'][-1][1] if sensor_data['temperature'] else "N/A"
            hum = sensor_data['humidity'][-1][1] if sensor_data['humidity'] else "N/A"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Temp: {temp} °C | Hum: {hum} %")
        time.sleep(1)

# Start printing in a separate thread
threading.Thread(target=print_values, daemon=True).start()

# Show plot
plt.show()