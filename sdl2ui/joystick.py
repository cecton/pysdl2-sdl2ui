import logging
import sdl2

import sdl2ui


class Joystick(object):
    logger = logging.getLogger(__name__)

    def __init__(self, index):
        self.index = index
        self.joystick = None
        self.id = -1
        self.name = sdl2.SDL_JoystickNameForIndex(index).decode()
        guid = sdl2.SDL_JoystickGetDeviceGUID(index)
        self.guid = "".join(map("{:02x}".format, guid.data))

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
        if not self.opened:
            self.logger.warning("Could not open joystick %d", self.index)
        else:
            self.logger.info(
                "Joystick %d opened: %s", self.index, self.name)
            self.id = sdl2.SDL_JoystickInstanceID(self.joystick)
            self.name = sdl2.SDL_JoystickName(self.joystick).decode()
            guid = sdl2.SDL_JoystickGetGUID(self.joystick)
            self.guid = "".join(map("{:02x}".format, guid.data))

    def close(self):
        if not self.opened:
            return
        sdl2.SDL_JoystickClose(self.joystick)
        self.logger.info("Joystick %d removed: %s", self.index, self.name)
        self.joystick = None
        self.id = -1


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
