import logging
from sdl2 import sdlmixer


class Mixer(object):
    logger = logging.getLogger(__name__)
    frequency = sdlmixer.MIX_DEFAULT_FREQUENCY
    format = sdlmixer.MIX_DEFAULT_FORMAT
    channels = sdlmixer.MIX_DEFAULT_CHANNELS
    chunksize = 1024

    def __init__(self, **kwargs):
        self.frequency = kwargs.get('frequency', self.frequency)
        self.format = kwargs.get('format', self.format)
        self.channels = kwargs.get('channels', self.channels)
        self.chunksize = kwargs.get('chunksize', self.chunksize)
        self.logger.info("Initializing mixer...")
        status = sdlmixer.Mix_OpenAudio(
            self.frequency, self.format, self.channels, self.chunksize)
        if status != 0:
            raise ValueError("can't open mixer: %s" % sdlmixer.Mix_GetError())

    def __del__(self):
        self.logger.info("Destroying mixer...")
        sdlmixer.Mix_HaltChannel(-1)
        sdlmixer.Mix_CloseAudio()

    def play(self, audio, channel=-1, loops=0):
        return Channel(channel, audio, loops)

    def halt(self, channel=-1):
        sdlmixer.Mix_HaltChannel(channel)


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
