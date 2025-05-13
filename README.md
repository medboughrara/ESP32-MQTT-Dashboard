# ESP32 MQTT Dashboard

This project demonstrates a simple dashboard for visualizing sensor data from an ESP32 microcontroller via MQTT. The ESP32 publishes simulated sensor readings (temperature and humidity) to an MQTT broker, and a Python script subscribes to these topics to display the data in real-time using Matplotlib.

## Project Structure

```
esp32_mqtt_dashboard/
├── esp32_random_mqtt/
│   └── esp32_random_mqtt.ino       # Arduino code for ESP32 to send MQTT data
├── mosquitto/
│   ├── config/                     # Mosquitto MQTT broker configuration (if customized)
│   ├── data/                       # Mosquitto data persistence
│   └── log/                        # Mosquitto logs
├── test_dashboard.py               # Python script for visualizing data
├── docker-compose.yml              # Docker Compose for running MQTT broker
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── .gitignore                      # Git ignore file
```

## Features

*   **ESP32 Sensor Simulation**: The `esp32_random_mqtt.ino` sketch simulates temperature and humidity readings and publishes them to MQTT topics.
*   **MQTT Communication**: Uses the MQTT protocol for message queuing between the ESP32 and the Python dashboard.
*   **Real-time Data Visualization**: The `test_dashboard.py` script subscribes to MQTT topics and plots the data in real-time using Matplotlib.
*   **Dockerized MQTT Broker**: Includes a `docker-compose.yml` file to easily set up an Eclipse Mosquitto MQTT broker.
*   **Terminal Output**: The Python script also prints the latest sensor values to the terminal.

## Prerequisites

*   **Hardware**:
    *   ESP32 development board
*   **Software**:
    *   Arduino IDE or PlatformIO for flashing the ESP32.
    *   Python 3.x
    *   Docker and Docker Compose (for running the MQTT broker)
    *   Git (for version control)

## Setup and Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd esp32_mqtt_dashboard
```

### 2. Set up MQTT Broker

You can use the provided Docker Compose file to run a Mosquitto MQTT broker.

```bash
docker-compose up -d
```

This will start the Mosquitto broker. The necessary `mosquitto/config`, `mosquitto/data`, and `mosquitto/log` directories will be created if they don't exist. You might need to create a basic `mosquitto.conf` file inside `mosquitto/config` if you need specific configurations (e.g., user authentication). For a simple setup without authentication, an empty `mosquitto.conf` or no file initially might work, but it's good practice to define one.

**Example `mosquitto/config/mosquitto.conf` (for anonymous access):**
```conf
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
allow_anonymous true
listener 1883
```

### 3. Configure ESP32 Sketch

*   Open `esp32_random_mqtt/esp32_random_mqtt.ino` in your Arduino IDE or PlatformIO.
*   Update the following variables with your credentials and settings:
    *   `ssid`: Your WiFi network name.
    *   `password`: Your WiFi password.
    *   `mqttBroker`: The IP address or hostname of your MQTT broker. If running Docker on the same machine, this will typically be your machine's local IP address or `host.docker.internal` (if your Docker version supports it from the container to the host). If your Python script and ESP32 are on the same network, you can use the local IP of the machine running the broker.
    *   `DEVICE_ID`: A unique ID for your ESP32 (e.g., "esp32_living_room").

*   Install the required Arduino libraries:
    *   `WiFi`
    *   `PubSubClient` by Nick O'Leary
    *   `ArduinoJson` by Benoit Blanchon
    *   `DHT sensor library` by Adafruit (even though we simulate, it's included)

*   Upload the sketch to your ESP32.

### 4. Set up Python Environment

*   Navigate to the project's root directory.
*   It's recommended to use a virtual environment:

    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

*   Install the Python dependencies:

    ```bash
    pip install -r requirements.txt
    ```

### 5. Configure Python Dashboard Script

*   Open `test_dashboard.py`.
*   Update the MQTT broker settings if they differ from the defaults:
    *   `MQTT_BROKER`: Address of your MQTT broker.
    *   `MQTT_USERNAME` and `MQTT_PASSWORD`: If your broker requires authentication.
    *   `MQTT_PORT`: Typically 1883.
    *   `MQTT_TOPICS`: Ensure these match the topics your ESP32 is publishing to (e.g., `"sensors/esp32/YOUR_DEVICE_ID/temperature"`).

## Running the Project

1.  **Start the MQTT Broker**:
    If not already running:
    ```bash
    docker-compose up -d
    ```

2.  **Power on and Run the ESP32**:
    Ensure the ESP32 is powered on and connected to your WiFi network. It should start publishing data to the MQTT broker. You can monitor its output via the Arduino Serial Monitor.

3.  **Run the Python Dashboard**:
    Execute the Python script:
    ```bash
    python test_dashboard.py
    ```
    This will open a Matplotlib window showing real-time plots for temperature and humidity. The latest values will also be printed in the terminal.

## MQTT Topics

The ESP32 publishes data to the following topic structure:

*   `sensors/esp32/<DEVICE_ID>/temperature`
*   `sensors/esp32/<DEVICE_ID>/humidity`

The Python script subscribes to these topics. Make sure `DEVICE_ID` in the Python script's `MQTT_TOPICS` list matches the `DEVICE_ID` set in the ESP32 sketch.

## Customization

*   **Adding More Sensors**:
    1.  Modify the ESP32 sketch (`esp32_random_mqtt.ino`) to read/simulate additional sensor data and publish it to new MQTT topics.
    2.  Update `MQTT_TOPICS` in `test_dashboard.py` to include the new topics.
    3.  Expand the `sensor_data` dictionary in `test_dashboard.py` to store data for new sensors.
    4.  Modify the `update_plot` function in `test_dashboard.py` to create new subplots or update existing ones for the new sensor data.

*   **Using Real Sensors**:
    Replace the `randomFloat()` calls in `readSensors()` in the ESP32 sketch with actual sensor reading code (e.g., using the DHT library for temperature/humidity).

*   **MQTT Broker Authentication**:
    If you configure your Mosquitto broker for authentication:
    1.  Update `mosquitto/config/mosquitto.conf` to set up users and passwords.
    2.  Provide `MQTT_USERNAME` and `MQTT_PASSWORD` in `test_dashboard.py`.
    3.  Modify the `client.connect()` call in `esp32_random_mqtt.ino` to include username and password if `PubSubClient` supports it directly or if your broker configuration requires it for client connections.

## Troubleshooting

*   **Connection Issues (ESP32)**:
    *   Verify WiFi credentials.
    *   Check MQTT broker address and port.
    *   Ensure the MQTT broker is running and accessible from the ESP32's network.
    *   Use the Serial Monitor in Arduino IDE to check for error messages.
*   **Connection Issues (Python)**:
    *   Verify `MQTT_BROKER`, `MQTT_PORT`, `MQTT_USERNAME`, and `MQTT_PASSWORD` in `test_dashboard.py`.
    *   Ensure the MQTT broker is running and accessible from the machine running the Python script.
    *   Check for firewall rules blocking connections.
*   **No Data on Dashboard**:
    *   Confirm the ESP32 is publishing data (check Serial Monitor).
    *   Ensure MQTT topics in the ESP32 sketch and Python script match exactly.
    *   Use an MQTT client tool (e.g., MQTT Explorer) to inspect messages on the broker.

## Contributing

Feel free to fork this repository, make improvements, and submit pull requests.

## License

This project is open-source. Specify a license if desired (e.g., MIT License).
