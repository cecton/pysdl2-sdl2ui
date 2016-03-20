import itertools
import logging
import re
import sdl2

import sdl2ui.ext
import sdl2ui.resource


class AudioDevice(object):
    logger = logging.getLogger(__name__)
    frequency = None
    format = None
    channels = None
    chunksize = None
    allowed_changes = 0

    def __init__(self, app):
        self.app = app
        self.c_callback = sdl2.SDL_AudioCallback(self._audio_callback)
        want = sdl2.SDL_AudioSpec(
            self.frequency, self.format, self.channels, self.chunksize,
            self.c_callback)
        self.audio_spec = sdl2.SDL_AudioSpec(
            self.frequency, self.format, self.channels, self.chunksize)
        self.logger.info("Opening audio device...")
        self.index = sdl2.SDL_OpenAudioDevice(
            None, 0, want, self.audio_spec, self.allowed_changes)
        if self.index == 0:
            raise ValueError(
                "can't open audio device: %s" % sdl2.SDL_GetError().decode())
        self.init()
        sdl2.SDL_PauseAudioDevice(self.index, 0)

    def _audio_callback(self, userdata, buf, buflen):
        sdl2.SDL_memset(buf, 0, buflen)
        data = (sdl2.Uint8 * buflen)()
        for i, v in zip(range(buflen), self.callback(buflen)):
            data[i] = v
        sdl2.SDL_MixAudioFormat(
            buf, data, self.audio_spec.format, buflen, self.volume)

    def init(self):
        pass

    def callback(self, length):
        return itertools.repeat(0)

    def close(self):
        self.logger.info("Closing audio device %d", self.index)
        sdl2.SDL_CloseAudioDevice(self.index)

    def pause(self):
        sdl2.SDL_PauseAudioDevice(self.index, 1)

    def resume(self):
        sdl2.SDL_PauseAudioDevice(self.index, 0)

    def get_volume(self):
        return getattr(self, '_volume', sdl2.SDL_MIX_MAXVOLUME)

    def set_volume(self, value):
        self._volume = int(value)

    volume = property(get_volume, set_volume)
