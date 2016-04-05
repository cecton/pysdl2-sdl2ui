import sdl2

import sdl2ui


class Debugger(sdl2ui.Component):
    def init(self):
        self.frames = 0
        self.p1 = sdl2.SDL_GetPerformanceCounter()
        self.p2 = 0
        self.freq = sdl2.SDL_GetPerformanceFrequency()
        self.threshold = self.props.get('refresh_delay', 0.1) * self.freq

    def activate(self):
        self.frames = 0
        self.p1 = sdl2.SDL_GetPerformanceCounter()

    def peek(self):
        self.frames += 1
        self.p2 = sdl2.SDL_GetPerformanceCounter()
        return (self.p2 - self.p1) >= self.threshold

    def render(self):
        self.app.write(
            'font-6', self.props.get('x', 0), self.props.get('y', 0),
            "%.3f" % (self.frames / ((self.p2 - self.p1) / self.freq)))
        if (self.p2 - self.p1) >= self.threshold:
            self.p1 = self.p2
            self.frames = 0
