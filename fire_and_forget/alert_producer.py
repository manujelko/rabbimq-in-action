import json
from optparse import OptionParser

import pika


def main() -> None:
    opt_parser = OptionParser()
    opt_parser.add_option(
        '-r',
        '--routing-key',
        dest='routing_key',
        help='Routing key for message (e.g. myalert.im)'
    )
    opt_parser.add_option(
        '-m',
        '--message',
        dest='message',
        help='Message text for alert.',
    )
    args = opt_parser.parse_args()[0]
    creds_broker = pika.PlainCredentials(username='guest', password='guest')
    conn_params = pika.ConnectionParameters(
        host='localhost',
        virtual_host='/',
        credentials=creds_broker,
    )
    conn_broker = pika.BlockingConnection(conn_params)
    channel = conn_broker.channel()

    msg = json.dumps(args.message)
    msg_props = pika.BasicProperties()
    msg_props.content_type = 'application/json'
    msg_props.durable = False

    channel.basic_publish(
        body=msg.encode('utf-8'),
        exchange='alerts',
        properties=msg_props,
        routing_key=args.routing_key,
    )
    print(f'Sent message {json.dumps(args.message)} tagged with routing key "{args.routing_key}" to exchange')


if __name__ == '__main__':
    main()
