import logging
import sdl2

import sdl2ui


class Joystick(object):
    logger = logging.getLogger(__name__)

    def __init__(self, index):
        self.index = index
        self.joystick = None
        self.id = -1
        self.name = None

    @property
    def opened(self):
        return (
            self.joystick is not None and
            sdl2.SDL_JoystickGetAttached(self.joystick) == sdl2.SDL_TRUE
        )

    def open(self):
        if self.opened:
            return
        self.joystick = sdl2.SDL_JoystickOpen(self.index)
        self.id = sdl2.SDL_JoystickInstanceID(self.joystick)
        self.name = sdl2.SDL_JoystickName(self.joystick).decode()
        if not self.opened:
            self.logger.warning("Could not open joystick %d", self.index)
        else:
            self.logger.info(
                "Joystick %d opened: %s", self.index, self.name)

    def close(self):
        if not self.opened:
            return
        sdl2.SDL_JoystickClose(self.joystick)
        self.logger.info("Joystick %d removed: %s", self.index, self.name)
        self.joystick = None
        self.id = -1
        self.name = None


class JoystickManager(sdl2ui.Component):
    def init(self):
        self.joysticks = {}
        sdl2.SDL_InitSubSystem(sdl2.SDL_INIT_JOYSTICK)
        self.app.register_event_handler(sdl2.SDL_QUIT, self.quit)

    def quit(self, event):
        for joystick in self.joysticks.values():
            joystick.close()

    def get(self, index):
        try:
            return self.joysticks[index]
        except KeyError:
            self.joysticks[index] = Joystick(index)
            return self.joysticks[index]


class KeyboardJoystick(sdl2ui.Component):
    logger = logging.getLogger(__name__)

    def init(self):
        self.event = sdl2.SDL_Event()
        self.app.register_event_handler(sdl2.SDL_JOYDEVICEADDED, self.added)
        self.app.register_event_handler(sdl2.SDL_JOYDEVICEREMOVED,
            self.removed)
        self.register_event_handler(
            sdl2.SDL_JOYBUTTONDOWN, self.button_down)
        self.set_state({
            'keyboard_mapping': {},
        })

    def added(self, event):
        self.joystick = self.props['manager'].get(event.jdevice.which)
        if self.joystick.index != self.props['index']:
            return
        self.joystick.open()

    def removed(self, event):
        self.joystick = self.props['manager'].get(event.jdevice.which)
        if self.joystick.index != self.props['index']:
            return
        self.joystick.close()

    def load(self, keyboard_mapping):
        self.set_state({
            'keyboard_mapping': keyboard_mapping,
        })

    def _push_keyboard_event(self, key):
        self.event.type = sdl2.SDL_KEYDOWN
        self.event.key.keysym.scancode = key
        self.event.key.keysym.sym = sdl2.SDL_GetKeyFromScancode(key)
        sdl2.SDL_PushEvent(self.event)

    def button_down(self, event):
        if not event.jbutton.which == self.joystick.id:
            return
        key = self.state['keyboard_mapping'].get(event.jbutton.button)
        if key:
            self.app.keys[key] = sdl2.SDL_TRUE
            self._push_keyboard_event(key)
        else:
            self.logger.debug(
                "Button %d on joystick %d not mapped",
                event.jbutton.button, self.props['index'])
