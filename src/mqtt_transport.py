'''implement mqtt transport for stats'''
import bson
import mosquitto

import transport

class Checker(transport.Checker):
    '''checker class that sends the stats to a mqtt broker'''

    def __init__(self, client_id, host="localhost", port=1883,
            topic_template="/ef/machine/%s/stats/%s", keepalive=60):
        transport.Checker.__init__(self)

        self.host = host
        self.port = port
        self.topic_template = topic_template
        self.client_id = client_id
        self.client = mosquitto.Mosquitto(client_id + "client")
        self.client.connect(host, port, keepalive)

    def send_stats(self, name, data):
        '''send stats somewhere'''
        topic = self.topic_template % (self.client_id, name)
        bson_data = bson.BSON.encode(data)
        self.client.publish(topic, bson_data, 1)

    def send_delta_stats(self, name, data):
        '''send delta stats somewhere'''
        topic = self.topic_template % (self.client_id, name) + "/diff"
        bson_data = bson.BSON.encode(data)
        self.client.publish(topic, bson_data, 1)

    def check(self):
        '''check for stats'''
        transport.Checker.check(self)
        self.client.loop(-1)

    def on_exit(self):
        '''cleanup resources'''
        self.client.disconnect()

def main():
    '''main function if this module is called, starts a mqtt listener'''
    import sys

    client_id = sys.argv[1]
    checker = Checker(client_id)
    print "run 'python mqtt_listener.py", client_id, "' to see the output"
    transport.main_loop(checker)

if __name__ == "__main__":
    main()

