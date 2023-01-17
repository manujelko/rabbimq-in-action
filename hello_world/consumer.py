from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika import spec
from pika.adapters.blocking_connection import BlockingChannel


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
    channel.queue_declare(queue='hello-queue')
    channel.queue_bind(
        queue='hello-queue',
        exchange='hello-exchange',
        routing_key='hola',
    )
    channel.basic_consume(
        queue='hello-queue',
        on_message_callback=msg_consumer,
        consumer_tag='hello-consumer',
    )
    channel.start_consuming()


def msg_consumer(
        channel: BlockingChannel,
        method: spec.Basic.Deliver,
        header: spec.BasicProperties,
        body: bytes,
) -> None:
    channel.basic_ack(delivery_tag=method.delivery_tag)
    if body == b'quit':
        channel.basic_cancel(consumer_tag='hello-consumer')
        channel.stop_consuming()
    else:
        print(body)


if __name__ == '__main__':
    main()
