"""EE 250L Lab 07 Skeleton Code

Run rpi_pub_and_sub.py on your Raspberry Pi."""
import sys
import paho.mqtt.client as mqtt
import time
import grovepi 
import grove_rgb_lcd 
#import grove_i2c_temp_hum_mini

dht_sensor_port = 7

state = 0

def lcdCallBack(client, userdata, message):
   grove_rgb_lcd.setText(str(message.payload,"utf-8"))

def ledCallBack(client, userdata, message):

    led = 2
    global state 
    msg = str(message.payload, "utf-8")
    if msg == "LED_toggle":
        if state == 1:
            grovepi.digitalWrite(led, 1)
            state = 0
        elif state == 0:
            grovepi.digitalWrite(led, 0)
            state = 1
        else:
            state = state


def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))
    client.subscribe("anrg-pi1/led")
    client.message_callback_add("anrg-pi1/led", ledCallBack)
    client.subscribe("anrg-pi1/lcd")
    client.message_callback_add("anrg-pi1/lcd", lcdCallBack)
    #client.subscribe("anrg-pi1/temperature")
   # client.subscribe("anrg-pi1/humidity")

def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload))

if __name__ == '__main__':
    #this section is covered in publisher_and_subscriber_example.py
    grove_rgb_lcd.setRGB(0,64,128)
    #t= grove_i2c_temp_hum_mini.th02()
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()

    while True:
        #read tempreture sensor
        #publish it 

        #read humidity sensor
        #publish it 
        #print (t.getTemperature())
        [temp, hum] = grovepi.dht(dht_sensor_port,1)
        print ("temp=", temp, " hum =", hum, "%")
        client.publish("anrg-pi1/humidity", "hello")
        time.sleep(1)
