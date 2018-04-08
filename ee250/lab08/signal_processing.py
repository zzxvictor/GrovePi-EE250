import paho.mqtt.client as mqtt
import time

# MQTT variables
broker_hostname = "eclipse.usc.edu"
broker_port = 11000
ultrasonic_ranger1_topic = "ultrasonic_ranger1"
ultrasonic_ranger2_topic = "ultrasonic_ranger2"

# Lists holding the ultrasonic ranger sensor distance readings. Change the 
# value of MAX_LIST_LENGTH depending on how many distance samples you would 
# like to keep at any point in time.
MAX_LIST_LENGTH = 100
WINDOW = 10
ranger1_dist = []
ranger2_dist = []
ranger1_filter = [0]*10
ranger2_filter = [0]*10
N = 3
def ranger1_callback(client, userdata, msg):
    global ranger1_dist
    ranger1_dist.append(int(msg.payload))
    #truncate list to only have the last MAX_LIST_LENGTH values
    ranger1_dist = ranger1_dist[-MAX_LIST_LENGTH:]
    movingAverage()

def ranger2_callback(client, userdata, msg):
    global ranger2_dist
    ranger2_dist.append(int(msg.payload))
    #truncate list to only have the last MAX_LIST_LENGTH values
    ranger2_dist = ranger2_dist[-MAX_LIST_LENGTH:]
    movingAverage()

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

def isMoving():
    global ranger1_filter
    global ranger2_filter

    #if the person is moving left
    #if the person is moving right
    #if the person is standing still
    if ranger1_filter[-1] == ranger1_filter[-2] and ranger1_filter[-2] == ranger1_filter[-3]:
        print ("still")
    elif ranger1_filter[-1] > ranger1_filter[-2] and ranger1_filter[-2] > ranger1_filter[-3]:
        print ("moving left")
    elif ranger1_filter[-1] < ranger1_filter[-2] and ranger1_filter[-2] < ranger1_filter[-3]:
        print ("moving right")

def movingAverage(input):
    global ranger1_filter
    global ranger2_filter
    global ranger1_dist
    global ranger2_dist
    #get a window 
    if input == 1:
    	ranger1_filter = ranger1_dist[-WINDOW]
    	ranger1_filter[-1] = sum(ranger1_filter)/len(ranger1_filter)
    	print (ranger1_filter)
    else:
		ranger2_filter = ranger2_dist[-WINDOW]
		ranger2_filter[-1] = sum(ranger2_filter)/len(ranger2_filter)
		print (ranger2_filter)


def detectLocation():
	
if __name__ == '__main__':
    # Connect to broker and start loop    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_hostname, broker_port, 60)
    client.loop_start()
    i = 0
    while True:
        """ You have two lists, ranger1_dist and ranger2_dist, which hold a window
        of the past MAX_LIST_LENGTH samples published by ultrasonic ranger 1
        and 2, respectively. The signals are published roughly at intervals of
        200ms, or 5 samples/second (5 Hz). The values published are the 
        distances in centimeters to the closest object. Expect values between 
        0 and 512. However, these rangers do not detect people well beyond 
        ~125cm. """
        
        # TODO: detect movement and/or position
        i += 1
        #print("ranger1: " + str(ranger1_filter[-1:]) + ", ranger2: " + 
        #    str(ranger1_filter[-1:])) 
        #print (len(ranger2_filter))
        if i>5:
            isMoving()

        time.sleep(0.2)