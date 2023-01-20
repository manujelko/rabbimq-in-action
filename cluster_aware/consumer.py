import json
import sys
import time

import pika

AMQP_SERVER = sys.argv[1]
AMQP_PORT = int(sys.argv[2])


def msg_rcvd(
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        header: pika.BasicProperties,
        body: bytes,
) -> None:
    message = json.loads(body)
    print(f'Received: {message}/{time}')
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main() -> None:
    creds_broker = pika.PlainCredentials(username='guest', password='guest')
    conn_params = pika.ConnectionParameters(
        host=AMQP_SERVER,
        port=AMQP_PORT,
        virtual_host='/',
        credentials=creds_broker,
    )

    while True:
        try:
            conn_broker = pika.BlockingConnection(conn_params)
            channel = conn_broker.channel()
            channel.exchange_declare(
                exchange='cluster_test',
                exchange_type='direct',
                auto_delete=False,
            )
            channel.queue_declare(
                queue='cluster_test',
                auto_delete=False,
            )
            channel.queue_bind(
                queue='cluster_test',
                exchange='cluster_test',
                routing_key='cluster_test',
            )
            print('Ready for testing!')
            channel.basic_consume(
                queue='cluster_test',
                on_message_callback=msg_rcvd,
                auto_ack=False,
                consumer_tag='cluster_test',
            )
            channel.start_consuming()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
