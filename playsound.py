import math
from struct import unpack

import win32comext.directsound.directsound as ds
import win32event as w32e
from pywintypes import WAVEFORMATEX


def _wav_header_unpack(data):
    (
        _format,
        nchannels,
        samplespersecond,
        datarate,
        blockalign,
        bitspersample,
        data,
        datalength
    ) = unpack("<4sl4s4slhhllhh4sl", data)[5:]
    wfx = WAVEFORMATEX()
    wfx.wFormatTag = _format
    wfx.nChannels = nchannels
    wfx.nSamplesPerSec = samplespersecond
    wfx.nAvgBytesPerSec = datarate
    wfx.nBlockAlign = blockalign
    wfx.wBitsPerSample = bitspersample
    return datalength, wfx

def open_audio(path: str):
    with open(path, 'rb') as f:
        data = f.read()
    return DirectSound(data)

class DirectSound:
    def __init__(self, data: bytes):
        self._hdr = data[0:44]
        self._bufdata = data[44:]
        self._sdesc = ds.DSBUFFERDESC()
        self._sdesc.dwBufferBytes, self._sdesc.lpwfxFormat = _wav_header_unpack(self._hdr)
        self._sdesc.dwFlags = ds.DSBCAPS_CTRLVOLUME | ds.DSBCAPS_CTRLPOSITIONNOTIFY | ds.DSBCAPS_GLOBALFOCUS
        self._volume = 0  # -10000 ~ 0
        self._buffers = []

    def _play(self):
        event = w32e.CreateEvent(None, 0, 0, None)
        dxs = ds.DirectSoundCreate(None, None)
        dxs.SetCooperativeLevel(None, ds.DSSCL_PRIORITY)

        buffer = dxs.CreateSoundBuffer(self._sdesc, None)
        buffer.QueryInterface(ds.IID_IDirectSoundNotify).SetNotificationPositions((-1, event))
        buffer.Update(0, self._bufdata)
        buffer.SetVolume(self._volume)
        buffer.Play(0)
        return event, buffer

    def set_volume(self, v: float):
        self._volume = int(-10000 if v <= 1e-5 else (0 if v >= 1.0 else 2000 * math.log10(v)))

    def play(self, wait: bool = False):
        event, buffer = self._play()
        self._buffers.append(buffer)

        for buffer in self._buffers:
            if buffer.GetStatus() == 0:
                self._buffers.remove(buffer)

        if wait:
            w32e.WaitForSingleObject(event, -1)