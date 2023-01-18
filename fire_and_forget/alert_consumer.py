import json, smtplib

import pika

AMQP_SERVER = 'localhost'
AMQP_USER = 'guest'
AMQP_PASS = 'guest'
AMQP_VHOST = '/'
AMQP_EXCHANGE = 'alerts'


def main() -> None:
    creds_broker = pika.PlainCredentials(AMQP_USER, AMQP_PASS)
    conn_params = pika.ConnectionParameters(
        host=AMQP_SERVER,
        virtual_host=AMQP_VHOST,
        credentials=creds_broker,
    )
    conn_broker = pika.BlockingConnection(conn_params)
    channel = conn_broker.channel()
    channel.exchange_declare(
        exchange=AMQP_EXCHANGE,
        exchange_type='topic',
        auto_delete=False,
    )
    channel.queue_declare(queue='critical', auto_delete=False)
    channel.queue_bind(queue='critical', exchange='alerts', routing_key='critical.*')
    channel.queue_declare(queue='rate_limit', auto_delete=False)
    channel.queue_bind(queue='rate_limit', exchange='alerts', routing_key='*.rate_limit')
    channel.basic_consume(
        queue='critical',
        on_message_callback=critical_notify,
        auto_ack=False,
        consumer_tag='critical',
    )
    channel.basic_consume(
        queue='rate_limit',
        on_message_callback=rate_limit_notify,
        auto_ack=False,
        consumer_tag='rate_limit',
    )
    print('Ready for alerts!')
    channel.start_consuming()


def send_mail(recipients: list[str], subject: str, message: str) -> None:
    """E-mail generator for received alerts."""
    headers = f"""
    From: alerts@ourcompany.com
    To:
    Date:
    Subject: {subject}\n
    """
    # smtp_server = smtplib.SMTP()
    # smtp_server.connect('mail.ourcompany.com', 25)
    # smtp_server.sendmail('alerts@ourcompany.com', recipients, headers + str(message))
    # smtp_server.close()
    pass


def critical_notify(
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        header: pika.spec.BasicProperties,
        body: bytes,
) -> None:
    """Sends CRITICAL alerts to administrators via e-mail."""
    EMAIL_RECIPS = ['ops.team@ourcompany.com']
    message = json.loads(body)
    send_mail(EMAIL_RECIPS, 'CRITICAL ALERT', message)
    print(
        f'Sent alert via -email! Alert Text: {message} '
        f'Recipients: {EMAIL_RECIPS}'
    )
    channel.basic_ack(delivery_tag=method.delivery_tag)


def rate_limit_notify(
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        header: pika.spec.BasicProperties,
        body: bytes,
) -> None:
    """Sends the message to the administrators via e-mail."""
    EMAIL_RECIPS = ['api.team@ourcompany.com']
    message = json.loads(body)
    # (f-asc_10) Transmit e-mail to SMTP server
    send_mail(EMAIL_RECIPS, 'RATE LIMIT ALERT!', message)
    print(
        f'Sent alert via e-mail! Alert Text: {message} '
        f'Recipients: {EMAIL_RECIPS}'
    )
    channel.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    main()
