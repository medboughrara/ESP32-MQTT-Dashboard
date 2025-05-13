#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// WiFi credentials
const char* ssid = "******";
const char* password = "************";

// MQTT Broker settings
const char* mqttBroker = "*******";
const int mqttPort = 1883;
const char* mqttTopic = "sensors/esp32";

// Define a unique Device ID for this ESP32
// IMPORTANT: Change this for each ESP32 board to ensure uniqueness
const char* DEVICE_ID = "esp32_living_room"; 

// Sensor pins
#define DHTPIN 4        // DHT22 for temperature and humidity
#define DHTTYPE DHT22

// Initialize objects
WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

// Variables for sensor readings
float temperature;
float humidity;
float nh3;
float co2;
float co; // Added CO
float illumination;
float noise;

unsigned long lastMsg = 0;

// Connect to WiFi
void setup_wifi() {
  Serial.println("Connecting to WiFi");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

// Reconnect to MQTT
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);

    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
}

// Generate random float between min and max
float randomFloat(float min, float max) {
  return min + static_cast<float>(random(0, 10001)) / 10000.0 * (max - min);
}

// Read sensors
void readSensors() {
  temperature = randomFloat(20.0, 32.0);     // °C
  humidity = randomFloat(40.0, 70.0);        // %

}

// Publish sensor data to MQTT
void publishData() {
  StaticJsonDocument<400> doc;
  String baseTopic = String("sensors/esp32/") + String(DEVICE_ID);

  // Temperature
  doc.clear();
  doc["device_id"] = DEVICE_ID;
  doc["value"] = temperature;
  doc["unit"] = "°C";
  String jsonString;
  serializeJson(doc, jsonString);
  client.publish((baseTopic + "/temperature").c_str(), jsonString.c_str());

  // Humidity
  doc.clear();
  doc["device_id"] = DEVICE_ID;
  doc["value"] = humidity;
  doc["unit"] = "%";
  jsonString = "";
  serializeJson(doc, jsonString);
  client.publish((baseTopic + "/humidity").c_str(), jsonString.c_str());
  

  // Optional: If you want to log the last published values
  Serial.print("Published - Temp: ");
  Serial.print(temperature);
  Serial.print(", Humidity: ");
  Serial.println(humidity);
}
void setup() {
  Serial.begin(115200);
  dht.begin();
  setup_wifi();
  client.setServer(mqttBroker, mqttPort);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > 5000) {
    lastMsg = now;
    readSensors();
    publishData();
  }
}
