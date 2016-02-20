from __future__ import division

import sdl2


class Component(object):
    default_active = True

    def get_active(self):
        return self._active

    def set_active(self, value):
        self._active = value
        self.app._update_active_components()
        if value:
            self.activate()
        else:
            self.deactivate()

    active = property(get_active, set_active)

    def __init__(self, app):
        self.app = app
        self._active = self.default_active
        self.init()

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

    def toggle(self):
        self.active = not self.active
        return self.active


class DebuggerComponent(Component):
    default_active = False
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
