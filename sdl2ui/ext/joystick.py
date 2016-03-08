import logging
import sdl2

import sdl2ui.ext


class BaseJoystick(sdl2ui.ext.Extension):
    logger = logging.getLogger(__name__)
    event_handlers = {
        sdl2.SDL_QUIT: 'close',
        sdl2.SDL_JOYDEVICEADDED: 'open',
        sdl2.SDL_JOYDEVICEREMOVED: 'close',
    }
    index = 0

    def init(self):
        self.joystick = None
        sdl2.SDL_InitSubSystem(sdl2.SDL_INIT_JOYSTICK)
        for event_type, handler_name in self._all_event_handlers:
            self.app.register_event_handler(
                event_type, getattr(self, handler_name))

    def open(self, event):
        self.joystick = sdl2.SDL_JoystickOpen(self.index)
        if self.joystick:
            self.logger.info(
                "Joystick %d found: %s",
                self.index, sdl2.SDL_JoystickName(self.joystick).decode())
        else:
            self.logger.warning("Could not find joystick %d", self.index)

    def close(self, event):
        if sdl2.SDL_JoystickGetAttached(self.joystick):
            self.logger.info(
                "Joystick %d removed: %s",
                self.index, sdl2.SDL_JoystickName(self.joystick).decode())
            sdl2.SDL_JoystickClose(self.joystick)

    @property
    def _all_event_handlers(self):
        for cls in reversed(type(self).mro()):
            if hasattr(cls, 'event_handlers'):
                for k, v in cls.event_handlers.items():
                    yield (k, v)


class BaseKeyboardJoystick(BaseJoystick):
    event_handlers = {
        sdl2.SDL_JOYBUTTONDOWN: 'button_down',
    }
    mapping = {
    }

    def button_down(self, event):
        key = self.mapping.get(event.jbutton.button)
        if key:
            self.app.keys[key] = sdl2.SDL_TRUE
        else:
            self.logger.debug(
                "Button %d on joystick %d not mapped",
                event.jbutton.button, self.index)
