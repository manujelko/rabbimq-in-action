import json

import pika


def main() -> None:
    creds_broker = pika.PlainCredentials('guest', 'guest')
    conn_params = pika.ConnectionParameters(
        host='localhost',
        virtual_host='/',
        credentials=creds_broker,
    )
    conn_broker = pika.BlockingConnection(conn_params)
    channel = conn_broker.channel()
    channel.exchange_declare(
        exchange='rpc',
        exchange_type='direct',
        auto_delete=False,
    )
    channel.queue_declare(queue='ping', auto_delete=False)
    channel.queue_bind(queue='ping', exchange='rpc', routing_key='ping')
    channel.basic_consume(queue='ping', consumer_tag='ping', on_message_callback=api_ping)
    print('Waiting for RPC calls...')
    channel.start_consuming()


def api_ping(
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        header: pika.spec.BasicProperties,
        body: bytes,
) -> None:
    """ping API call."""
    channel.basic_ack(delivery_tag=method.delivery_tag)
    msg_dict = json.loads(body)
    print('Received API call...replying...')
    channel.basic_publish(
        body=b'Pong! ' + str(msg_dict['time']).encode('utf-8'),
        exchange='',
        routing_key=header.reply_to,
    )


if __name__ == '__main__':
    main()
