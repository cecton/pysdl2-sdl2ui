import logging
import re
from sdl2 import sdlmixer

import sdl2ui
import sdl2ui.resource


class Mixer(sdl2ui.Extension):
    logger = logging.getLogger(__name__)
    frequency = sdlmixer.MIX_DEFAULT_FREQUENCY
    format = sdlmixer.MIX_DEFAULT_FORMAT
    channels = sdlmixer.MIX_DEFAULT_CHANNELS
    chunksize = 1024

    def init(self):
        self.logger.info("Initializing mixer...")
        status = sdlmixer.Mix_OpenAudio(
            self.frequency, self.format, self.channels, self.chunksize)
        if status != 0:
            raise ValueError(
                "can't open mixer: %s" % sdlmixer.Mix_GetError().decode())
        self.app.register('play', self.play)

    def close(self):
        self.logger.info("Destroying mixer...")
        sdlmixer.Mix_HaltChannel(-1)
        sdlmixer.Mix_CloseAudio()

    def play(self, resource_key, channel=-1, loops=0):
        return Channel(self.app.resources[resource_key], channel, loops)


class Channel(object):
    def __init__(self, audio, channel=-1, loops=0):
        self.audio = audio
        self.index = sdlmixer.Mix_PlayChannel(channel, audio.sample, loops)

    def halt(self):
        sdlmixer.Mix_HaltChannel(self.index)

    def pause(self):
        sdlmixer.Mix_Pause(self.index)

    def resume(self):
        sdlmixer.Mix_Resume(self.index)

    def get_volume(self):
        return sdlmixer.Mix_Volume(self.index, -1)

    def set_volume(self, value):
        sdlmixer.Mix_Volume(self.index, int(value))

    volume = property(get_volume, set_volume)


class Audio(sdl2ui.resource.BaseResource):
    regex = re.compile(r"^.*\.(wav|flac|ogg|mod|mid|mp3)$")

    def load(self):
        self.sample = sdlmixer.Mix_LoadWAV(self.filepath.encode())
        if not self.sample:
            raise ValueError(
                "can't load resource %r: %s"
                % (self.filename, sdlmixer.Mix_GetError().decode()))

    def close(self):
        if getattr(self, 'sample', None):
            sdlmixer.Mix_FreeChunk(self.sample)
