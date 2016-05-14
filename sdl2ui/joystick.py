import ctypes
import logging
import sdl2

import sdl2ui


class Joystick(object):
    logger = logging.getLogger(__name__)

    def __init__(self, index, existing_guids=[]):
        self.index = index
        self.joystick = None
        self.id = -1
        self.name = sdl2.SDL_JoystickNameForIndex(index).decode()
        guid = sdl2.SDL_JoystickGetDeviceGUID(index)
        self.guid = "".join(map("{:02x}".format, guid.data))
        if self.guid in existing_guids:
            self.guid += "-{}".format(index)

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
                "Joystick %d opened: %s (%s)",
                self.index, self.name, self.guid)
            self.id = sdl2.SDL_JoystickInstanceID(self.joystick)

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
        self.app.register_event_handler(sdl2.SDL_JOYDEVICEADDED, self.added)
        self.app.register_event_handler(sdl2.SDL_JOYDEVICEREMOVED, self.removed)

    def added(self, event):
        # NOTE: automatically instantiate Joystick, the joystick will not
        #       be opened anyway
        # NOTE: event.jdevice.which is the joystick index during a
        #       JOYDEVICEADDED event
        self.joysticks[event.jdevice.which] = Joystick(
            event.jdevice.which,
            [x.guid for x in self.joysticks.values()])

    def removed(self, event):
        # NOTE: automatically drop the Joystick instance so we can keep an
        #       accurate list of the joystick available. It will not be deleted
        #       anyway if it is referenced somewhere else.
        # NOTE: event.jdevice.which is the joystick id during a
        #       JOYDEVICEREMOVED event (not index!)
        for index, joystick in list(self.joysticks.items()):
            if joystick.id == event.jdevice.which:
                self.joysticks.pop(index)

    def quit(self, event):
        for joystick in self.joysticks.values():
            joystick.close()

    def get(self, index):
        return self.joysticks[index]

    def find(self, id):
        for joystick in self.joysticks.values():
            if joystick.id == id:
                return joystick
        return None

    def reload(self):
        sdl2.SDL_QuitSubSystem(sdl2.SDL_INIT_JOYSTICK)
        self.joysticks.clear()
        sdl2.SDL_InitSubSystem(sdl2.SDL_INIT_JOYSTICK)
        sdl2.SDL_PumpEvents()
        event = sdl2.SDL_Event()
        while sdl2.SDL_PeepEvents(
                ctypes.byref(event),
                1,
                sdl2.SDL_GETEVENT,
                sdl2.SDL_JOYDEVICEADDED,
                sdl2.SDL_JOYDEVICEADDED) != 0:
            self.added(event)
