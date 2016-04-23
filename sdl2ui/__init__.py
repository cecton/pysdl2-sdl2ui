from __future__ import division

import logging
import operator
import sdl2

__version__ = '0.1.14'
__author__ = 'Cecile Tonglet'


class Component(object):
    logger = logging.getLogger(__name__)
    eq_operator = operator.eq

    def __init__(self, app, parent, **props):
        self.app = app
        self.parent = parent
        self.active = False
        self.props = props
        self.components = []
        self.event_handlers = {}
        self.state = {}

    def set_state(self, state):
        for k, v in state.items():
            if (k not in self.state or
                    not self.eq_operator(self.state[k], v)):
                self.state.update(state)
                self.app.touch()
                return

    def init(self):
        pass

    def activate(self):
        pass

    def deactivate(self):
        pass

    def enable(self):
        self.app.enable_component(self)

    def disable(self):
        self.app.disable_component(self)

    def toggle(self):
        self.app.toggle_component(self)

    def register_event_handler(self, event_type, handler):
        self.event_handlers.setdefault(event_type, []).append(handler)

    def add_component(self, component, **props):
        assert issubclass(component, Component), \
            "must be a %s subclass" % Component
        instance = component(self.app, self, **props)
        self.components.append(instance)
        instance.init()
        return instance

    def poll(self, event):
        if not self.active:
            return
        for event_handler in self.event_handlers.get(event.type, []):
            event_handler(event)
        for child in self.components:
            child.poll(event)

    def poll_safe(self, event):
        if not self.active:
            return
        for event_handler in self.event_handlers.get(event.type, []):
            try:
                event_handler(event)
            except:
                self.logger.exception(
                    "Error during execution of event handler: %r",
                    event_handler)
        for child in self.components:
            child.poll_safe(event)


class NullComponent(Component):
    def __bool__(self):
        return False


from sdl2ui.app import App
