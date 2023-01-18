import json, time

import pika


def reply_callback(
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        header: pika.spec.BasicProperties,
        body: bytes,
) -> None:
    """Receives RPC server replies."""
    print(f'RPC Reply ---  {body}')
    channel.stop_consuming()


def main() -> None:
    creds_broker = pika.PlainCredentials(username='guest', password='guest')
    conn_params = pika.ConnectionParameters(
        host='localhost',
        virtual_host='/',
        credentials=creds_broker,
    )
    conn_broker = pika.BlockingConnection(conn_params)
    channel = conn_broker.channel()
    msg = json.dumps(
        {
            'client_name': 'RPC Client 1.0',
            'time': time.time(),
        }
    ).encode('utf-8')
    result = channel.queue_declare(queue='', exclusive=True, auto_delete=True)
    msg_props = pika.BasicProperties()
    msg_props.reply_to = result.method.queue
    channel.basic_publish(
        body=msg,
        exchange='rpc',
        properties=msg_props,
        routing_key='ping',
    )
    print('Sent "ping" RPC call. Waiting for reply...')
    channel.basic_consume(
        queue=result.method.queue,
        consumer_tag=result.method.queue,
        on_message_callback=reply_callback,
    )
    channel.start_consuming()


if __name__ == '__main__':
    main()
