import paho.mqtt.client as mqtt
import broker_config
import json
import mysql.connector
import time;


def on_connect(client, userdata, flags, rc):
    try:
        print("Connected with result code " + str(rc))
        client.subscribe(broker_config.channelName1)
    except Exception as e:
        print("Exception in Subscriber block",e)

def on_message(client, userdata, msg):
    try:
        print(msg.topic + " " + str(msg.payload))
        print("data recieved",msg.payload.decode())

        data_cleaning = msg.payload.decode()
        data_in_json_format = json.loads(data_cleaning)
        print(type(msg.payload.decode()))

        t = time.localtime()
        temperature_data = data_in_json_format["temperature"]
        humidity_data = data_in_json_format["humidity"]
        gas_data = data_in_json_format["Gas"]
        current_time = time.strftime("%H:%M:%S", t)

        
        print(temperature_data)
        print(humidity_data)
        print(gas_data)
        print(current_time)
        cnx = mysql.connector.connect(
            user = "",
            passwd = "",
            host = "localhost",
            database = "sensor"
        )

        cur = cnx.cursor()
        val = (temperature_data, humidity_data, gas_data, current_time)
        cur.execute("insert into sensorData values (%s, %s, %s, %s);", val)


        cnx.commit()

    except Exception as e:
        print("Exception in on message block",e)

def main_handler():
    try:
        client = mqtt.Client()
        client.username_pw_set(username="")

        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(broker_config.broker_host, broker_config.port_name, broker_config.keep_alive)

        client.loop_forever()
    except Exception as e:
        print("Exception in main",e)    

main_handler()
