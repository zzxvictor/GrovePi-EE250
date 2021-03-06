import paho.mqtt.client as mqtt
import time
import requests
import json
from datetime import datetime

# MQTT variables
broker_hostname = "eclipse.usc.edu"
broker_port = 11000
ultrasonic_ranger1_topic = "ultrasonic_ranger1"
ultrasonic_ranger2_topic = "ultrasonic_ranger2"
#variables for signal processing
MAX_LIST_LENGTH = 100
WINDOW = 20
ranger1_dist = []
ranger2_dist = []
ranger1_filtered = []
ranger2_filtered = []
event = "NULL"

def ranger1_callback(client, userdata, msg):
    global ranger1_dist
    global ranger1_filtered
    ranger1_dist.append(int(msg.payload))
    #truncate list to only have the last MAX_LIST_LENGTH values
    ranger1_dist = ranger1_dist[-MAX_LIST_LENGTH:]
    ranger1_filtered = movingAverage(ranger1_dist)

def ranger2_callback(client, userdata, msg):
    global ranger2_dist
    global ranger2_filtered
    ranger2_dist.append(int(msg.payload))
    #truncate list to only have the last MAX_LIST_LENGTH values
    ranger2_dist = ranger2_dist[-MAX_LIST_LENGTH:]
    ranger2_filtered = movingAverage(ranger2_dist)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(ultrasonic_ranger1_topic)
    client.message_callback_add(ultrasonic_ranger1_topic, ranger1_callback)
    client.subscribe(ultrasonic_ranger2_topic)
    client.message_callback_add(ultrasonic_ranger2_topic, ranger2_callback)

# The callback for when a PUBLISH message is received from the server.
# This should not be called.
def on_message(client, userdata, msg): 
    print(msg.topic + " " + str(msg.payload))


#   moving average function, the window length is determined by the macro: WINDOW
def movingAverage(distance):
    filtered = distance[-1*WINDOW:]
    #print (len(filtered))
    filtered[-1] = sum(filtered)/len(filtered)
    return filtered



#   detect motions and make classfication
def motionDection():
    global ranger1_filtered
    global ranger2_filtered
    global event
    ##potential bugs
    sum1 = sum(ranger1_filtered[-1:])
    sum2 = sum(ranger1_filtered[-2:-1])
    sum3 = sum(ranger1_filtered[-3:-2])

    sumr1 = sum(ranger2_filtered[-1:])
    sumr2 = sum(ranger2_filtered[-2:-1])
    sumr3 = sum(ranger2_filtered[-3:-2])
    print (sum1)
    print (sumr1)
    if (sum1 <490 or sum1 > 530) and (sumr1 <300 or sumr1 > 340):
        if (sum1 > sum2 and sum2 > sum3) or (sumr1 < sumr2 and sumr2 < sumr3):
            print ("moving left")
            event = "moving left"
        elif (sum1 < sum2 and sum2 < sum3) or (sumr1 > sumr2 and sumr2 > sumr3):
            print ("moving right")
            event = "moving right"
        else:
            print ("----------------")
            print (" still")
            ranger1Sum = sum(ranger1_filtered)/(len(ranger1_filtered)+1)
            ranger2Sum = sum(ranger2_filtered)/(len(ranger2_filtered)+1)
            if ranger1Sum < ranger2Sum - 100 :
                print ("right")
                event = "still right"
            elif ranger2Sum < ranger1Sum - 100:
                print ("left")
                event = "still left"
            else:
                print ("middle")
                event = "still middle"
            print ("---------------")
    else:
        print ("no one is there")
        event = "No one is there"

if __name__ == '__main__':

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_hostname, broker_port, 60)
    client.loop_start()
    # Connect to broker and start loop 
    hdr = {
        'Content-Type': 'application/json',
        'Authorization': None #not using HTTP secure
    }

    
    while True:
        #refresh the event 
        payload = {
            'time': str(datetime.now()),
            'event': event
        }  
        response = requests.post("http://0.0.0.0:5000/post-event", headers = hdr,data = json.dumps(payload))
        #send the updated event
        print(response.json())
        motionDection()
        time.sleep(0.2)