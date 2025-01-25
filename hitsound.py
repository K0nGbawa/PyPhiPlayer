from sys import argv
from json import load

from pydub import AudioSegment

import const

NoteClickAudios = {
    1: AudioSegment.from_file("./resources/sounds/tap.wav"),
    2: AudioSegment.from_file("./resources/sounds/drag.wav"),
    3: AudioSegment.from_file("./resources/sounds/tap.wav"),
    4: AudioSegment.from_file("./resources/sounds/flick.wav")
}



def summon(Chart, audio, output, offset=0):
    ChartAudio:AudioSegment = AudioSegment.from_file(audio)
    ChartAudio_Length = ChartAudio.duration_seconds
    ChartAudio_Split_Audio_Block_Length = ChartAudio.duration_seconds * 1000 / 85 #ms
    ChartAudio_Split_Length = int(ChartAudio_Length / (ChartAudio_Split_Audio_Block_Length / 1000)) + 1
    ChartAudio_Split_Audio_List = [AudioSegment.silent(ChartAudio_Split_Audio_Block_Length + 500) for _ in [None] * ChartAudio_Split_Length]
    JudgeLine_cut = 0

    for JudgeLine in Chart["judgeLineList"]:
        Note_cut = 0
        for note in JudgeLine["notesBelow"] + JudgeLine["notesAbove"]:
            try:
                t = note["time"] - (offset if note["type"] in (1, 3) else 0)
                t_index = int(t / (ChartAudio_Split_Audio_Block_Length / 1000))
                t %= ChartAudio_Split_Audio_Block_Length / 1000
                seg: AudioSegment = ChartAudio_Split_Audio_List[t_index]
                ChartAudio_Split_Audio_List[t_index] = seg.overlay(NoteClickAudios[note["type"]], t * 1000)
                print(f"Process Note: {JudgeLine_cut}+{Note_cut}")
                Note_cut += 1
            except IndexError:
                pass
        JudgeLine_cut += 1

    print("Merge...")
    for i,seg in enumerate(ChartAudio_Split_Audio_List):
        ChartAudio = ChartAudio.overlay(seg, i * ChartAudio_Split_Audio_Block_Length + Chart["offset"] * 1000)

    ChartAudio.export(output)

    print("Done.")