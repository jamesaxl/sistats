'''example module to listen to mqtt broker for sistats'''

import bson
import mosquitto

import sistats

MQTT_CONNECT_STATUS = {
    0: "Success",
    1: "Refused - unacceptable protocol version",
    2: "Refused - identifier rejected",
    3: "Refused - server unavailable",
    4: "Refused - bad user name or password",
    5: "Refused - not authorised"
}

class Consumer(object):
    '''receives stats from a mqtt broker'''

    STATS = ("cpu", "mem", "net", "disk", "fs")

    def __init__(self, client_id, host="localhost", port=1883,
            topic_template="/ef/machine/%s/stats/%s", keepalive=60,
            topics=STATS):

        self.host = host
        self.port = port
        self.topic_template = topic_template
        self.client_id = client_id

        self.client = mosquitto.Mosquitto(client_id)

        self.client.on_message = on_message
        self.client.on_connect = on_connect

        self.client.connect(host, port, keepalive)

        for name in topics:
            topic = topic_template % (client_id, name)
            topic_diff = topic + "/diff"
            print "subscribing to topic", topic, "and", topic_diff
            self.client.subscribe(topic, 0)
            self.client.subscribe(topic_diff, 0)

def on_message(_mosq, msg):
    '''callback called when a message from the subscriptions is received'''
    data = bson.BSON(msg.payload).decode()
    sistats.pretty_print(msg.topic, data)

def on_connect(_mosq, code):
    '''callback called on connect'''
    print "connection response:", MQTT_CONNECT_STATUS[code]

def main():
    '''main function if this module is called, starts a mqtt listener'''
    import sys

    client_id = sys.argv[1]
    consumer = Consumer(client_id)

    while True:
        consumer.client.loop(-1)

if __name__ == "__main__":
    main()
