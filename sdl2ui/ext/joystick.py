import logging
import sdl2

import sdl2ui.ext


class BaseJoystick(sdl2ui.ext.Extension):
    logger = logging.getLogger(__name__)
    event_handlers = {}
    index = 0

    def init(self):
        sdl2.SDL_InitSubSystem(sdl2.SDL_INIT_JOYSTICK)
        for event_type, handler_name in self.event_handlers.items():
            self.app.register_event_handler(
                event_type, getattr(self, handler_name))
        self.joystick = sdl2.SDL_JoystickOpen(self.index)
        if self.joystick:
            self.logger.info(
                "Joystick %d found: %s",
                self.index, sdl2.SDL_JoystickName(self.joystick).decode())
        else:
            self.logger.warning("Could not find joystick %d", self.index)

    def close(self):
        if sdl2.SDL_JoystickGetAttached(self.joystick):
            sdl2.SDL_JoystickClose(self.joystick)


class BaseKeyboardJoystick(BaseJoystick):
    event_handlers = {
        sdl2.SDL_JOYBUTTONDOWN: 'update_button',
    }
    mapping = {
    }

    def update_button(self, event):
        key = self.mapping.get(event.jbutton.button)
        if key:
            self.app.keys[key] = sdl2.SDL_TRUE
        else:
            self.logger.debug(
                "Button %d on joystick %d not mapped",
                event.jbutton.button, self.index)
