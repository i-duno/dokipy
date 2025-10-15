from __future__ import annotations
import typing
import pygame
import uuid
import threading

CHANNEL_EVENTS = 0

class Audio:
    def __init__(self, system: AudioSystem, sound_group: str, path: str):
        self.System = system
        self.Sound = pygame.mixer.Sound(path)
        self.Channel = -1
        self.VolGroup = sound_group
    
    def Play(self, vol: float = 1.0, loop: bool = False, callback: typing.Union[typing.Callable, None, list[typing.Callable]] = None):
        if self.Channel != -1 and self.IsPlaying():
            self.System._unpause(self)
            return
        if callback is not None and not isinstance(callback, list):
            callback = [callback]

        self.System._stop(self)
        self.System._play(self, vol, loop, callback)
    
    def Stop(self):
        self.System._stop(self)

    def Pause(self):
        self.System._pause(self)

    def IsPlaying(self):
        return self.System._isPlaying(self)
    

class AudioSystem:
    def __init__(self, max_channel=64):
        pygame.mixer.init()
        pygame.mixer.set_num_channels(max_channel)
        self.Channels = [pygame.mixer.Channel(id) for id in range(max_channel)]
        self.ChannelAudio: dict[int, Audio] = {}
        self.Sounds = {}
        self.Callbacks = {}

        global CHANNEL_EVENTS
        CHANNEL_EVENTS = pygame.USEREVENT+max_channel

    def Load(self, path: str, name: typing.Union[str, None] = None, sound_group: str = 'default', load_async: bool = False) -> Audio:
        if name is None:
            name = str(uuid.uuid4())
        if name in self.Sounds:
            return self.Sounds[name]

        def load_sound():
            self.Sounds[name] = Audio(self, path=path, sound_group=sound_group)

        if load_async:
            threading.Thread(target=load_sound, daemon=True).start()
        else:
            load_sound()

        return self.Sounds[name]
    
    def Update(self, event: pygame.event.Event):
        if event.type in self.Callbacks:
            func_cache = self.Callbacks[event.type]
            del self.Callbacks[event.type]
            for callback in func_cache:
                try:
                    callback()
                except Exception as e:
                    print(f'exception at sound {e}')
                    continue

    def SetGroup_Vol(self, sound_group: str, vol: float):
        for k, audio in self.ChannelAudio.items():
            if not self._isPlaying(audio=audio):
                continue
            if audio.VolGroup == sound_group:
                self.Channels[k].set_volume(vol)
                

    def _isPlaying(self, audio: Audio) -> bool:
        return self.Channels[audio.Channel].get_busy()

    def _play(self, audio: Audio, vol: float, loop: bool, callback: typing.Union[None, list[typing.Callable]]):
        for i, channel in enumerate(self.Channels):
            ev_id = pygame.USEREVENT+i
            if not channel.get_busy():
                channel.set_volume(vol)
                channel.play(audio.Sound, loops=-1 if loop else 0)
                channel.set_endevent(ev_id)
                self.ChannelAudio[i] = audio
                
                audio.Channel = i
                if callback:
                    self.Callbacks[ev_id] = callback
                break

    def _stop(self, audio: Audio):
        ev_id = pygame.USEREVENT+audio.Channel
        if ev_id in self.Callbacks:
            del self.Callbacks[ev_id]
        
        self.Channels[audio.Channel].stop()

    def _pause(self, audio: Audio):
        if self._isPlaying(audio):
            self.Channels[audio.Channel].pause()
    
    def _unpause(self, audio: Audio):
        self.Channels[audio.Channel].unpause()