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
        self.logger.info("Initializing mixer component...")
        status = sdlmixer.Mix_OpenAudio(
            self.props.get('frequency', sdlmixer.MIX_DEFAULT_FREQUENCY),
            self.props.get('format', sdlmixer.MIX_DEFAULT_FORMAT),
            self.props.get('channels', sdlmixer.MIX_DEFAULT_CHANNELS),
            self.props.get('chunksize', 1024))
        if status != 0:
            raise Exception(
                "can't open mixer: %s" % sdlmixer.Mix_GetError().decode())
        self.app.register_event_handler(sdl2.SDL_QUIT, self.quit)

    def quit(self, event):
        self.logger.info("Closing mixer...")
        sdlmixer.Mix_HaltChannel(-1)
        sdlmixer.Mix_CloseAudio()

    def open(self, resource, loops=0):
        return self.add_component(Channel,
            audio=self.app.resources[resource],
            loops=loops)


class Channel(sdl2ui.Component):
    def init(self):
        self.channel = None

    def halt(self):
        sdlmixer.Mix_HaltChannel(self.channel)

    def deactivate(self):
        sdlmixer.Mix_Pause(self.channel)

    def activate(self):
        if self.channel is None:
            self.channel = sdlmixer.Mix_PlayChannel(
                -1, self.props['audio'].sample, self.props.get('loops', 0))
        sdlmixer.Mix_Resume(self.channel)

    def get_volume(self):
        return sdlmixer.Mix_Volume(self.channel, -1)

    def set_volume(self, value):
        sdlmixer.Mix_Volume(self.channel, int(value))

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
