import sys

from pika import BasicProperties, BlockingConnection, ConnectionParameters, DeliveryMode, PlainCredentials
from pika.exceptions import UnroutableError, NackError


def main() -> None:
    credentials = PlainCredentials(username='guest', password='guest')
    conn_params = ConnectionParameters(host='localhost', credentials=credentials)
    conn_broker = BlockingConnection(parameters=conn_params)
    channel = conn_broker.channel()
    channel.confirm_delivery()
    msg = sys.argv[1].encode('utf-8')

    msg_props = BasicProperties(
        content_type='text/plain',
        delivery_mode=DeliveryMode.Transient.value,
    )
    msg_props.content_type = 'text/plain'

    try:
        channel.basic_publish(
            body=msg,
            exchange='hello-exchange',
            properties=msg_props,
            routing_key='hola',
        )
        print('Message publish was confirmed')
    except UnroutableError:
        print('Message could not be confirmed')
    except NackError:
        print("Message was not acknowledge by the broker")


if __name__ == '__main__':
    main()
