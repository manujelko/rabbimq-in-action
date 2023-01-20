import json
import sys
import time

import pika


AMQP_HOST = sys.argv[1]
AMQP_PORT = sys.argv[2]


def main() -> None:
    creds_broker = pika.PlainCredentials(username='guest', password='guest')
    conn_params = pika.ConnectionParameters(
        host=AMQP_HOST,
        port=AMQP_PORT,
        virtual_host='/',
        credentials=creds_broker,
    )
    conn_broker = pika.BlockingConnection(conn_params)
    channel = conn_broker.channel()
    msg = json.dumps({'content': 'Cluster Test!', 'time': time.time()}).encode('utf-8')
    msg_props = pika.BasicProperties(content_type='application/json')
    channel.basic_publish(
        body=msg,
        exchange='cluster_test',
        properties=msg_props,
        routing_key='cluster_test',
    )
    print('Sent cluster test message')


if __name__ == '__main__':
    main()
