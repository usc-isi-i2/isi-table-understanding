from drepr_wapi.queue import QueueConsumer
from drepr_wapi.config import MSG_QUEUE_HOST
from drepr.message_handler import BasicMsgHandler


def main():

    cname = "table_understanding"
    consumer = QueueConsumer.get_instance(cname)

    msg_handler = BasicMsgHandler()
    consumer.set_callback(msg_handler)

    print(f">>> [{cname}] start consuming message from {MSG_QUEUE_HOST}...")
    consumer.start_consuming()


if __name__ == "__main__":
    main()
