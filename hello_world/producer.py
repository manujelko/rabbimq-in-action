import sys

from pika import BasicProperties, BlockingConnection, ConnectionParameters, PlainCredentials


def main() -> None:
    credentials = PlainCredentials(username='guest', password='guest')
    conn_params = ConnectionParameters(host='localhost', credentials=credentials)
    conn_broker = BlockingConnection(parameters=conn_params)
    channel = conn_broker.channel()
    channel.exchange_declare(
        exchange='hello-exchange',
        exchange_type='direct',
        passive=False,
        durable=True,
        auto_delete=False,
    )
    msg = sys.argv[1].encode('utf-8')
    msg_props = BasicProperties()
    msg_props.content_type = 'text/plain'
    channel.basic_publish(
        body=msg,
        exchange='hello-exchange',
        properties=msg_props,
        routing_key='hola',
    )


if __name__ == '__main__':
    main()
