import pika
import threading
import logging
import functools
from argparse import ArgumentParser

NO_ACK = True

def gen_msg(configs, count):
    conn = pika.BlockingConnection(configs)
    channel = conn.channel()
    channel.queue_declare(queue='src')
    for i in range(count):
        channel.basic_publish(exchange='',
                      routing_key='src',
                      body=str(i))
    
    logging.info("Publish %d to queue src.", count)
    conn.close()

def thread_task( pika_manager, method_frame, msg):
    logging.info("In thread. msg: %s", msg)
    res = int(msg) + 1
    pika_manager.add_threadsafe_callback(method_frame, method_frame, str(res))


class PikaManager(object):
    def __init__(self, configs):
        self.configs = configs
        self.conn = None
        self.chan_src = None
        self.chan_dst = None

    def connect(self):
        self.conn = pika.BlockingConnection(self.configs)

        self.chan_src = self.conn.channel()
        self.chan_src.queue_declare(queue='src')

        self.chan_dst = self.conn.channel()
        self.chan_dst.queue_declare(queue='dst')
        

    def start_consuming(self):
        try:
            logging.info("Connect to Pika.")
            self.connect()

            self.chan_src.basic_consume(self.on_message, 'src',  no_ack=NO_ACK)
            
            logging.info("start consuming...")
            self.chan_src.start_consuming()  
        except pika.exceptions.ConnectionClosed as err:
            logging.error(err)
        except pika.exceptions.AMQPChannelError as err:
            logging.error(err)
        except pika.exceptions.AMQPConnectionError as err:
            logging.error(err)
        except Exception as err:
            logging.exception(err) 

    def on_message(self, channel, method_frame, header_frame, body):
        logging.info("Get msg %s", body)
        t = threading.Thread(
            target = functools.partial(thread_task, self, method_frame, body))
        t.start()

    def send_result(self, method_frame, msg):
        self.chan_dst.basic_publish(exchange='', routing_key='dst', body=msg)
        logging.info("Send result.")

        if not NO_ACK:
            self.chan_src.basic_ack(delivery_tag=method_frame.delivery_tag)
            logging.info("Send ack.")
        
    def add_threadsafe_callback(self, cb, method_frame, msg):
        self.conn.add_callback_threadsafe(
            functools.partial(self.send_result, method_frame, msg)
        )

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%d-%m-%Y:%H:%M:%S',
        level=logging.WARNING)

    parser = ArgumentParser()
    parser.add_argument("-c", "--count", help="publish message count", default=1000, type=int, dest="count")
    args = parser.parse_args()
    
    configs = (
        pika.ConnectionParameters(host='192.168.37.102'))

    gen_msg(configs, args.count)

    manager = PikaManager(configs)
    manager.start_consuming()
