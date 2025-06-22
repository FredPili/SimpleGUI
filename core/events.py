from enum import IntEnum


class Events(IntEnum) :
    PARAM_CHANGE = 1
    DISPLAY_CHANGE = 2


class EventBus :
    # Simple event bus class, no payload in the publish, only for triggering callbacks
    def __init__(self) :
        self.subscribers = {}

    def subscribe(self, event, handler) :
        if event not in self.subscribers :
            self.subscribers[event] = []
        self.subscribers[event].append(handler)

    def publish(self, event) :
        for handler in self.subscribers.get(event, []) :
            handler()


if __name__ == "__main__" :
    eventbus = EventBus()
    def event() :
        print("Event called !")
    eventbus.subscribe("event", event)
    eventbus.publish("event")
    eventbus.publish("noevent")