import logging
import sdl2

import sdl2ui.ext


class BaseJoystick(sdl2ui.ext.Extension):
    logger = logging.getLogger(__name__)
    event_handlers = {
    }
    index = 0

    def init(self):
        self.joystick = None
        sdl2.SDL_InitSubSystem(sdl2.SDL_INIT_JOYSTICK)
        self.app.register_event_handler(sdl2.SDL_JOYDEVICEADDED, self.open)
        self.app.register_event_handler(sdl2.SDL_JOYDEVICEREMOVED, self.close)
        self.app.register_event_handler(sdl2.SDL_QUIT, self.close)
        for event_type, handler_name in self.event_handlers.items():
            self.app.register_event_handler(
                event_type, getattr(self, handler_name))

    def open(self, event):
        if not event.jdevice.which == self.index:
            return
        self.joystick = sdl2.SDL_JoystickOpen(self.index)
        self.joystick_id = sdl2.SDL_JoystickInstanceID(self.joystick)
        if self.joystick:
            self.logger.info(
                "Joystick %d found: %s",
                self.index, sdl2.SDL_JoystickName(self.joystick).decode())
        else:
            self.logger.warning("Could not open joystick %d", self.index)

    def close(self, event):
        if event.type == sdl2.SDL_JOYDEVICEREMOVED and \
                not event.jdevice.which == self.index:
            return
        self.logger.info(
            "Joystick %d removed: %s",
            self.index, sdl2.SDL_JoystickName(self.joystick).decode())
        sdl2.SDL_JoystickClose(self.joystick)


class BaseKeyboardJoystick(BaseJoystick):
    event_handlers = {
        sdl2.SDL_JOYBUTTONDOWN: 'button_down',
    }
    mapping = {
    }

    def button_down(self, event):
        if not event.jbutton.which == self.joystick_id:
            return
        key = self.mapping.get(event.jbutton.button)
        if key:
            self.app.keys[key] = sdl2.SDL_TRUE
        else:
            self.logger.debug(
                "Button %d on joystick %d not mapped",
                event.jbutton.button, self.index)
