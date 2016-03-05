from __future__ import division

from collections import OrderedDict
from contextlib import contextmanager
import ctypes
import logging
try:
    import sdl2
except ImportError as ex:
    if not hasattr(sys, "_gen_docs"):
        sys.exit("SDL2 library not found: %s" % ex)

from sdl2ui.component import Component
from sdl2ui.resource import load as resource_loader


class App(object):
    name = "SDL2 Application"
    logger = logging.getLogger(__name__)
    init_flags = 0
    window_flags = sdl2.SDL_WINDOW_HIDDEN
    renderer_flags = 0
    default_extensions = []
    default_components = []
    default_resources = [('font-6', 'font-6.png')]
    width = None
    height = None
    zoom = 1
    fps = 60

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', self.name)
        self.width = kwargs.get('width', self.width)
        self.height = kwargs.get('height', self.height)
        self.zoom = kwargs.get('zoom', self.zoom)
        self.fps = kwargs.get('fps', self.fps)
        self.init_flags = kwargs.get('init_flags', self.init_flags)
        self.window_flags = kwargs.get('window_flags', self.window_flags)
        self.renderer_flags = kwargs.get('renderer_flags', self.renderer_flags)
        self.extensions = {}
        self.components = OrderedDict()
        self.resources = {}
        self.tints = []
        assert self.width, "missing argument width"
        assert self.height, "missing argument height"
        assert self.window_flags, "missing argument window_flags"
        self.quit = False
        self.renderer = None
        self.window = None
        self.logger.info("Initializing application: %s", self.name)
        for extension_class in self.default_extensions:
            self.add_extension(extension_class)
        for extension_class in kwargs.get('extensions', []):
            self.add_extension(extension_class)
        sdl2.SDL_Init(self.init_flags)
        self.window = self._get_window()
        self.renderer = self._get_renderer()
        for key, resource_file in self._all_default_resources:
            self.load_resource(key, resource_file)
        for key, resource_file in kwargs.get('resources', []):
            self.load_resource(key, resource_file)
        self.resources['font-6'].make_font(4, 11,
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?("
            ")[]~-_+@:/'., ")
        for component_class in kwargs.get('components', []):
            self.add_component(component_class)
        for component_class in self.default_components:
            self.add_component(component_class)
        self._update_active_components()
        self.init()
        sdl2.SDL_ShowWindow(self.window)

    @property
    def _all_default_resources(self):
        all_resources = []
        for cls in type(self).mro():
            if issubclass(cls, App):
                all_resources.extend(vars(cls)['default_resources'])
        return all_resources

    def _get_window(self):
        return sdl2.SDL_CreateWindow(
            self.name.encode(),
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            self.width * self.zoom,
            self.height * self.zoom,
            self.window_flags)

    def _get_renderer(self):
        renderer = \
            sdl2.SDL_CreateRenderer(self.window, -1, self.renderer_flags)
        if self.zoom != 1:
            sdl2.SDL_RenderSetScale(renderer, self.zoom, self.zoom)
        return renderer

    def _destroy_extensions(self):
        for k in list(self.extensions.keys()):
            del self.extensions[k]

    def _destroy_resources(self):
        for k in list(self.resources.keys()):
            del self.resources[k]

    def __del__(self):
        self.logger.info("Destroying application: %s", self.name)
        self._destroy_resources()
        self._destroy_extensions()
        if self.renderer:
            sdl2.SDL_DestroyRenderer(self.renderer)
        if self.window:
            sdl2.SDL_HideWindow(self.window)
            sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()

    def _poll_events(self):
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                self.quit = True
            elif event.type in (sdl2.SDL_KEYDOWN, sdl2.SDL_KEYUP):
                self.keys = sdl2.SDL_GetKeyboardState(None)

    def _update_active_components(self):
        self._active_components = [
            x for x in self.components.values() if x.active
        ]

    def _peek_components(self):
        return any(x.peek() for x in self._active_components)

    def _render_components(self):
        sdl2.SDL_RenderClear(self.renderer)
        for component in self._active_components:
            component.render()
        sdl2.SDL_RenderPresent(self.renderer)

    def add_extension(self, extension_class):
        assert issubclass(extension_class, Extension), \
            "must be an Extension class"
        if extension_class in self.extensions:
            raise ValueError("extension already exists")
        self.extensions[extension_class] = extension_class(self)

    def add_component(self, component_class):
        assert issubclass(component_class, Component), \
            "must be a Component class"
        if component_class in self.components:
            raise ValueError("component already exists")
        self.components[component_class] = component_class(self)

    def register(self, attr, object):
        if hasattr(self, attr):
            raise AttributeError("attribute already exists")
        setattr(self, attr, object)

    def init(self):
        pass

    def loop(self):
        dt = int(1000 / self.fps)
        self.keys = sdl2.SDL_GetKeyboardState(None)
        self._render_components()
        while not self.quit:
            t1 = sdl2.timer.SDL_GetTicks()
            self._poll_events()
            if self._peek_components():
                self._render_components()
            t2 = sdl2.timer.SDL_GetTicks()
            delay = dt - (t2 - t1)
            if delay > 0:
                sdl2.timer.SDL_Delay(delay)

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


class Extension(object):
    def __init__(self, app):
        self.app = app
        self.init()

    def init(self):
        pass
