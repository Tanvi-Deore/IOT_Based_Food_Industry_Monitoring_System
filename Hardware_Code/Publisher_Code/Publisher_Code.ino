#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include "MQ135.h"

// WiFi credentials
const char* ssid = "";
const char* password = "";

// ThingsBoard MQTT parameters
const char* mqttServer = "mqtt.thingsboard.cloud"; 
const int mqttPort = 1883;
const char* mqttUsername = "";

const char* mqttServer1 = ""; 
const int mqttPort1 = 1883;
const char* mqttClientID = "";

// DHT parameters
#define DHTPIN 4        // Digital pin connected to the DHT sensor
#define DHTTYPE DHT22    // DHT 22

//const int Sensor_input = 32;
const int ANALOGPIN=32;
MQ135 gasSensor = MQ135(ANALOGPIN);

DHT dht(DHTPIN, DHTTYPE);

WiFiClient espClient;
WiFiClient espClient1;
PubSubClient client(espClient);
PubSubClient client1(espClient1);

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  
  Serial.println("Connected to WiFi");

  client.setServer(mqttServer, mqttPort);
  client1.setServer(mqttServer1, mqttPort1);
  dht.begin();
}

void loop() {
  if (!client.connected() && !client1.connected()) {
    reconnect();
  }
  client.loop();

  // Reading temperature or humidity takes about 250 milliseconds!
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature(); // Celsius
  int sensor_Aout = gasSensor.getPPM();  /*Analog value read function*/
  

  // Check if any reads failed and exit early (to try again).
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    delay(2000);
    return;
  }

  // Publish temperature and humidity data to ThingsBoard
  String payload = "{\"temperature\": " + String(temperature) + ", \"humidity\": " + String(humidity) + ", \"Gas\": " + String(sensor_Aout) + "}";

  if(temperature > 30 || humidity > 50 || sensor_Aout > 50)
  {
    client.publish("v1/devices/me/telemetry", payload.c_str());
    client1.publish("topic", payload.c_str());    
  }
  else
  {
    client1.publish("topic", payload.c_str());  
  }

  Serial.println("Temperature: " + String(temperature) + " °C, Humidity: " + String(humidity) + " %" + " Gas: " + String(sensor_Aout));

  delay(2000); // Adjust delay as needed
}

void reconnect() {
  while (!client.connected() && !client1.connected()) {
    Serial.println("Connecting to MQTT broker...");
    if (client.connect("ESP32Client", mqttUsername, NULL) && client1.connect("ESP32Client", mqttUsername, NULL)) {
      Serial.println("Connected to MQTT broker");
      client.subscribe("v1/devices/me/rpc/request/+");
      client1.subscribe("cdac/diot");
    } else {
      Serial.print("Failed to connect to MQTT broker, rc=");
      Serial.print(client.state());
      Serial.print(client1.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}
