from __future__ import division

import operator
import sdl2


class BaseComponent(object):
    def __init__(self):
        self.active = False

    def init(self):
        pass

    def peek(self):
        return False

    def render(self):
        pass

    def activate(self):
        pass

    def deactivate(self):
        pass

    def show(self):
        self.app.componenents_activation[self.name] = True

    def hide(self):
        self.app.componenents_activation[self.name] = False

    def toggle(self):
        if self.active:
            self.hide()
        else:
            self.show()

    def register_event_handler(self, event_type, event_handler):
        self.app.register_event_handler(
            event_type,
            lambda e: self.active and event_handler(e))


class Component(BaseComponent):
    props_operator = operator.eq

    def __init__(self, **props):
        BaseComponent.__init__(self)
        self.props = props
        self._render = False

    def set_state(self, props):
        for k, v in props.items():
            if (k not in self.props or
                    not self.props_operator(self.props[k], v)):
                self.props[k] = v
                self._render = True

    def peek(self):
        if not self._render:
            return False
        self._render = False
        return True


class ImmutableComponent(Component):
    props_operator = operator.is_


class Debugger(BaseComponent):
    refresh_delay = 0.1

    def init(self):
        self.frames = 0
        self.p1 = sdl2.SDL_GetPerformanceCounter()
        self.p2 = 0
        self.freq = sdl2.SDL_GetPerformanceFrequency()
        self.threshold = self.refresh_delay * self.freq

    def activate(self):
        self.frames = 0
        self.p1 = sdl2.SDL_GetPerformanceCounter()

    def peek(self):
        self.frames += 1
        self.p2 = sdl2.SDL_GetPerformanceCounter()
        return (self.p2 - self.p1) >= self.threshold

    def render(self):
        self.app.write('font-6', 0, 0,
            "%.3f" % (self.frames / ((self.p2 - self.p1) / self.freq)))
        if (self.p2 - self.p1) >= self.threshold:
            self.p1 = self.p2
            self.frames = 0
