import itertools
import logging
import sdl2

import sdl2ui


class AudioDevice(sdl2ui.Component):
    logger = logging.getLogger(__name__)

    def init(self):
        self.c_callback = sdl2.SDL_AudioCallback(self._audio_callback)
        want = sdl2.SDL_AudioSpec(
            self.props['frequency'], self.props['format'],
            self.props['channels'], self.props['chunksize'], self.c_callback)
        self.audio_spec = sdl2.SDL_AudioSpec(
            self.props['frequency'], self.props['format'],
            self.props['channels'], self.props['chunksize'])
        self.logger.info("Opening audio device...")
        self.index = sdl2.SDL_OpenAudioDevice(
            None, 0, want, self.audio_spec,
            self.props.get('allowed_changes', 0))
        if self.index == 0:
            raise ValueError(
                "can't open audio device: %s" % sdl2.SDL_GetError().decode())
        self.app.register_event_handler(sdl2.SDL_QUIT, self.quit)
        self.load()

    def _audio_callback(self, userdata, buf, buflen):
        sdl2.SDL_memset(buf, 0, buflen)
        data = (sdl2.Uint8 * buflen)()
        for i, v in zip(range(buflen), self.callback(buflen)):
            data[i] = v
        sdl2.SDL_MixAudioFormat(
            buf, data, self.audio_spec.format, buflen, self.volume)

    def callback(self, length):
        return itertools.repeat(0)

    def quit(self, event):
        self.close()

    def load(self):
        pass

    def unload(self):
        pass

    def close(self):
        self.logger.info("Closing audio device %d", self.index)
        sdl2.SDL_CloseAudioDevice(self.index)
        self.unload()

    def deactivate(self):
        sdl2.SDL_PauseAudioDevice(self.index, 1)
        self.paused = True

    def activate(self):
        sdl2.SDL_PauseAudioDevice(self.index, 0)
        self.paused = False

    def get_volume(self):
        return getattr(self, '_volume', sdl2.SDL_MIX_MAXVOLUME)

    def set_volume(self, value):
        self._volume = int(value)

    volume = property(get_volume, set_volume)
