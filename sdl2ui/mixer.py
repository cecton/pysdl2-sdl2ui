import logging
import re
import sdl2
from sdl2 import sdlmixer

import sdl2ui
import sdl2ui.resource


__all__ = ['Mixer']


class Mixer(sdl2ui.Component):
    logger = logging.getLogger(__name__)

    def init(self):
        self._closed = False
        self.logger.info("Initializing mixer component...")
        status = sdlmixer.Mix_OpenAudio(
            self.props.get('frequency', sdlmixer.MIX_DEFAULT_FREQUENCY),
            self.props.get('format', sdlmixer.MIX_DEFAULT_FORMAT),
            self.props.get('channels', sdlmixer.MIX_DEFAULT_CHANNELS),
            self.props.get('chunksize', 1024))
        if status != 0:
            raise Exception(
                "can't open mixer: %s" % sdlmixer.Mix_GetError().decode())
        self.app.register('play', self.play)
        self.app.register_event_handler(sdl2.SDL_QUIT, self.close)

    @property
    def closed(self):
        return self._closed

    def close(self, event):
        if not self.closed:
            self._closed = True
            self.logger.info("Closing mixer...")
            sdlmixer.Mix_HaltChannel(-1)
            sdlmixer.Mix_CloseAudio()

    def play(self, resource_key, channel=-1, loops=0):
        if self.closed:
            raise Exception("The mixer has been closed")
        return Channel(self, self.app.resources[resource_key], channel, loops)


class Channel(object):
    def __init__(self, mixer, audio, channel=-1, loops=0):
        self.mixer = mixer
        self.audio = audio
        self.paused = False
        self.index = sdlmixer.Mix_PlayChannel(channel, audio.sample, loops)

    def halt(self):
        if self.mixer.closed:
            raise Exception("The mixer has been closed")
        sdlmixer.Mix_HaltChannel(self.index)

    def pause(self):
        if self.mixer.closed:
            raise Exception("The mixer has been closed")
        sdlmixer.Mix_Pause(self.index)
        self.paused = True

    def resume(self):
        if self.mixer.closed:
            raise Exception("The mixer has been closed")
        sdlmixer.Mix_Resume(self.index)
        self.paused = False

    def toggle(self):
        if self.paused:
            self.resume()
        else:
            self.pause()

    def get_volume(self):
        if self.mixer.closed:
            raise Exception("The mixer has been closed")
        return sdlmixer.Mix_Volume(self.index, -1)

    def set_volume(self, value):
        if self.mixer.closed:
            raise Exception("The mixer has been closed")
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
