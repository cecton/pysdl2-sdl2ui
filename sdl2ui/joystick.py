import logging
import sdl2

import sdl2ui


class BaseJoystick(sdl2ui.Component):
    logger = logging.getLogger(__name__)

    def init(self):
        self.logger.info(
            "Initializing joystick component for device %d",
            self.props['index'])
        self.joystick = None
        sdl2.SDL_InitSubSystem(sdl2.SDL_INIT_JOYSTICK)
        self.app.register_event_handler(sdl2.SDL_QUIT, self.close)
        self.register_event_handler(sdl2.SDL_JOYDEVICEADDED, self.open)
        self.register_event_handler(sdl2.SDL_JOYDEVICEREMOVED, self.close)

    def open(self, event):
        if not event.jdevice.which == self.props['index']:
            return
        self.joystick = sdl2.SDL_JoystickOpen(self.props['index'])
        self.joystick_id = sdl2.SDL_JoystickInstanceID(self.joystick)
        if self.joystick:
            self.logger.info(
                "Joystick %d found: %s",
                self.props['index'],
                sdl2.SDL_JoystickName(self.joystick).decode())
        else:
            self.logger.warning(
                "Could not open joystick %d", self.props['index'])

    def close(self, event):
        if event.type == sdl2.SDL_JOYDEVICEREMOVED and \
                not event.jdevice.which == self.props['index']:
            return
        if sdl2.SDL_JoystickGetAttached(self.joystick) == sdl2.SDL_TRUE:
            self.logger.info(
                "Joystick %d removed: %s",
                self.props['index'],
                sdl2.SDL_JoystickName(self.joystick).decode())
            sdl2.SDL_JoystickClose(self.joystick)


class KeyboardJoystick(BaseJoystick):
    def init(self):
        BaseJoystick.init(self)
        self.register_event_handler(
            sdl2.SDL_JOYBUTTONDOWN, self.button_down)
        self.event = sdl2.SDL_Event()

    def _push_keyboard_event(self, key):
        self.event.type = sdl2.SDL_KEYDOWN
        self.event.key.keysym.scancode = key
        self.event.key.keysym.sym = sdl2.SDL_GetKeyFromScancode(key)
        sdl2.SDL_PushEvent(self.event)

    def button_down(self, event):
        if not event.jbutton.which == self.joystick_id:
            return
        key = self.props['keyboard_mapping'].get(event.jbutton.button)
        if key:
            self.app.keys[key] = sdl2.SDL_TRUE
            self._push_keyboard_event(key)
        else:
            self.logger.debug(
                "Button %d on joystick %d not mapped",
                event.jbutton.button, self.props['index'])
