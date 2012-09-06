'''implement mqtt transport for stats'''
import bson
import mosquitto

import transport

from optparse import OptionParser

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

def base_option_parser():
    '''create a parser for the basic options and return it, used to extend
    the command line parsing with custom options for other agents
    '''
    parser = OptionParser()

    parser.add_option("-v", action="store_true", dest="verbose", default=False,
        help="be verbose")
    parser.add_option("-c", "--clientid", dest="clientid", default=None,
        help="generate event for clientid", metavar="ID")

    parser.add_option("-H", "--host", dest="host", default="localhost",
        help="send events to HOST", metavar="HOST")
    parser.add_option("-P", "--port", dest="port", default=1883,
        type="int", help="send events to PORT", metavar="PORT")

    parser.add_option("-u", "--username", dest="username", default=None,
        help="authenticate using USERNAME", metavar="USERNAME")
    parser.add_option("-p", "--password", dest="password", default=None,
        help="authenticate using PASSWORD, if not provided ask for it",
        metavar="PASSWORD")

    parser.add_option("-C", "--checkinterval", dest="checkinterval",
            default=10, type="int",
            help="check for new values every SEC seconds", metavar="SEC")

    return parser
def main():
    '''main function if this module is called, starts a mqtt listener'''
    parser = base_option_parser()
    opts, _args = parser.parse_args()

    checker = Checker(opts.clientid, opts.host, opts.port)
    print "run 'python mqtt_listener.py", opts.clientid, "' to see the output"
    transport.main_loop(checker, opts.checkinterval)

if __name__ == "__main__":
    main()

