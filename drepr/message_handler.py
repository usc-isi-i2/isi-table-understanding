from drepr_wapi.event import Event, ResourceCreateEvent
from drepr_wapi.queue import MsgHandler
import time

from drepr.event_handlers import ResourceCreateEventHandler


class BasicMsgHandler(MsgHandler):

    def __init__(self):
        pass

    def handle_resource_create_event(self, event):
        event_handler = ResourceCreateEventHandler(event)
        event_handler.handle_event()

    def handle(self, channel, method, properties, body):
        print(" [x] Received %r" % body)
        event = Event.deserialize4str(body)
        print(event)

        if isinstance(event, ResourceCreateEvent):
            self.handle_resource_create_event(event)


if __name__ == "__main__":
    handler = BasicMsgHandler()

    event = Event("access_token", "dataset_id", 60, time.time())
    handler.handle_resource_create_event(event)

    event = Event("access_token_1", "dataset_id_1", 60, time.time())
    handler.handle_resource_create_event(event)

    event = Event("access_token_2", "dataset_id_2", 60, time.time())
    handler.handle_resource_create_event(event)

    event = Event("access_token_3", "dataset_id_3", 60, time.time())
    handler.handle_resource_create_event(event)
