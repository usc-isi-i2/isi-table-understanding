from drepr_wapi.api import WebappAPI
from abc import abstractmethod
from threading import BoundedSemaphore, Thread

from drepr.resource_adapter import ResourceAdapter
from drepr_wapi.event import Event


class EventHandler:
    def __init__(self, event):
        self.api = WebappAPI.get_instance()
        self.event = event
        # Q: Is this sent with every event?
        self.dataset_info = self.api.get_dataset(event)
        # TODO: Enable ack
        # self.api.ack(event)  # Acknowledge that we will handle this event.

    @abstractmethod
    def handle_event(self):
        pass


class ResourceCreateEventHandler(EventHandler):
    max_threads = 2
    semaphore = BoundedSemaphore(value=max_threads)

    def __init__(self, event):
        super().__init__(event)
        self.resource_info = self.dataset_info['resources'][event.resource_id]
        self.resource_data = self.api.get_resource_data(event, event.resource_id, self.resource_info['dimension'])

        print(self.resource_data)
        print(self.dataset_info, self.resource_info)

    def handle_event(self):
        t = Thread(target=ResourceCreateEventHandler.worker, args=(self.api, self.event, self.resource_data,))
        t.start()

    @staticmethod
    def worker(api: WebappAPI, event: Event, resource_data):
        # This method has the drawback of creating as many threads as there are calls to worker.
        # Would it be better to put all requests in a queue and use a thread pool?
        with ResourceCreateEventHandler.semaphore:
            print(event.resource_id)
            resource_adapter = ResourceAdapter(resource_data, event.resource_id)
            variables = resource_adapter.get_variables()
            print("Variables")
            print(variables)
            # call webapi - register_variables/register_alignments
            print("Calling api") # TODO
            # for variable in variables:
            #     api.register_variables(event, variable)

