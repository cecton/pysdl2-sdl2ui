
from collections import OrderedDict
from contextlib import contextmanager
import ctypes
import itertools
import logging
try:
    import sdl2
except ImportError as ex:
    if not hasattr(sys, "_gen_docs"):
        sys.exit("SDL2 library not found: %s" % ex)

from sdl2ui import Component
from sdl2ui.resource import load as resource_loader


def _get_active_components_recursively(component):
    if not component.active:
        return []
    active_childs = []
    for child in component.components:
        active_childs.extend(_get_active_components_recursively(child))
    return [component] + active_childs


class App(Component):
    name = "SDL2 Application"
    logger = logging.getLogger(__name__)

    @classmethod
    def run(cls, **kwargs):
        app = cls(**kwargs)
        app.loop()
        return app

    def __init__(self, **options):
        Component.__init__(self, self, None, **options)
        self.viewport = sdl2.SDL_Rect()
        self._components_activation = OrderedDict()
        self.resources = {}
        self.tints = []
        self.timers = []
        self._running = True
        self.logger.info("Initializing application: %s", self.name)
        sdl2.SDL_Init(self.props.get('init_flags', 0))
        self.register_event_handler(sdl2.SDL_QUIT, self._quit)
        self.register_event_handler(sdl2.SDL_WINDOWEVENT, self._window_event)
        self.keys = sdl2.SDL_GetKeyboardState(None)
        self.window = self._get_window()
        self.renderer = self._get_renderer()
        self.load_resource('font-6', 'font-6.png')
        self.resources['font-6'].make_font(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?("
            ")[]~-_+@:/'., ")
        self.enable()
        try:
            self.init()
        except:
            self.quit()
            self._clean_up()
            raise
        sdl2.SDL_ShowWindow(self.window)

    def touch(self):
        self._touched = True

    def peek(self):
        if not self._touched:
            return False
        self._touched = False
        return True

    @property
    def touched(self):
        return self._touched

    @property
    def running(self):
        return self._running

    def _get_window(self):
        return sdl2.SDL_CreateWindow(
            self.name.encode(),
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            self.props.get('width'),
            self.props.get('height'),
            self.props.get('window_flags', 0))

    def _get_renderer(self):
        renderer = \
            sdl2.SDL_CreateRenderer(self.window, -1, self.props.get('renderer_flags'))
        zoom = self.props.get('zoom', 1)
        if zoom is not 1:
            sdl2.SDL_RenderSetScale(renderer, zoom, zoom)
        sdl2.SDL_RenderGetViewport(renderer, self.viewport)
        self.logger.debug("Viewport: %dx%d", self.viewport.w, self.viewport.h)
        return renderer

    def _destroy_resources(self):
        for k in list(self.resources.keys()):
            self.resources[k].close()

    def _clean_up(self):
        self.logger.info("Destroying application: %s", self.name)
        self._destroy_resources()
        if self.renderer:
            sdl2.SDL_DestroyRenderer(self.renderer)
        if self.window:
            sdl2.SDL_HideWindow(self.window)
            sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()

    def quit(self, exception=None):
        sdl2.SDL_PumpEvents()
        sdl2.SDL_FlushEvents(sdl2.SDL_FIRSTEVENT, sdl2.SDL_LASTEVENT)
        event = sdl2.SDL_Event()
        event.type = sdl2.SDL_QUIT
        self.poll_safe(event)

    def _window_event(self, event):
        self.touch()

    def _quit(self, event):
        self._running = False

    def _poll_events(self):
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            self.poll(event)

    def _call_timers(self, ticks):
        if self.timers:
            i = 0
            for time, callback in self.timers:
                if time > ticks:
                    break
                i += 1
                callback()
            if i > 0:
                self.timers = self.timers[i:]

    @property
    def active_components(self):
        return self._active_components

    @property
    def components_to_peek(self):
        if self._components_to_peek is None:
            self._components_to_peek = [
                component
                for component in self._active_components
                if hasattr(component, 'peek')
            ]
        return self._components_to_peek

    @property
    def components_to_render(self):
        if self._components_to_render is None:
            self._components_to_render = [
                component
                for component in self._active_components
                if hasattr(component, 'render')
            ]
        return self._components_to_render

    def _update_active_components(self):
        if not self._components_activation:
            return
        has_changed = False
        activations = list(self._components_activation.items())
        self._components_activation.clear()
        for component, active in activations:
            if not component.active == active:
                has_changed = True
                component.active = active
                if active:
                    component.activate()
                    self.logger.debug("Component has been activated: %r",
                        component)
                else:
                    component.deactivate()
                    self.logger.debug("Component has been deactivated: %r",
                        component)
        if has_changed:
            self._active_components = _get_active_components_recursively(self)
            self._components_to_peek = None
            self._components_to_render = None
            self.touch()

    def _peek_components(self):
        # NOTE: any() used on a generator returns as soon as it finds a True
        #       operand. Here, we need all the peek() methods to be called.
        return any([
            component.peek()
            for component in self.components_to_peek
        ])

    def _render_components(self):
        sdl2.SDL_RenderClear(self.renderer)
        for component in self.components_to_render:
            component.render()
        sdl2.SDL_RenderPresent(self.renderer)

    def enable_component(self, component):
        self._components_activation[component] = True

    def disable_component(self, component):
        self._components_activation[component] = False

    def toggle_component(self, component):
        self._components_activation[component] = not component.active

    def init(self):
        pass

    def loop(self):
        dt = int(1000 / self.props.get('fps', 60))
        try:
            while self._running:
                t1 = sdl2.timer.SDL_GetTicks()
                self._update_active_components()
                self._poll_events()
                self._call_timers(t1)
                if self._peek_components():
                    self._render_components()
                t2 = sdl2.timer.SDL_GetTicks()
                delay = dt - (t2 - t1)
                if delay > 0:
                    sdl2.timer.SDL_Delay(delay)
        except BaseException as exception:
            self.quit(exception)
            raise
        finally:
            self._clean_up()

    def load_resource(self, key, filename):
        self.logger.info("Loading %r: %s", key, filename)
        self.resources[key] = resource_loader(self, filename)

    @contextmanager
    def tint(self, tint):
        self.tints.append(tint)
        try:
            yield
        finally:
            self.tints.pop()

    def _call_resource(self, resource_key, method, *args, **kwargs):
        resource = self.resources[resource_key]
        if self.tints:
            with resource.tint(*self.tints[-1]):
                return getattr(resource, method)(*args, **kwargs)
        else:
            return getattr(resource, method)(*args, **kwargs)

    def draw(self, resource_key, *args, **kwargs):
        return self._call_resource(resource_key, 'draw', *args, **kwargs)

    def write(self, resource_key, *args, **kwargs):
        return self._call_resource(resource_key, 'write', *args, **kwargs)

    def add_timer(self, interval, callback):
        ticks = sdl2.timer.SDL_GetTicks() + interval
        self.timers.append((ticks, callback))
