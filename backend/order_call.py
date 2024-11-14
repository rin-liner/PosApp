import requests
import json
import pyaudio
import wave
from pydub import AudioSegment
import io
from pathlib import Path

__assets = Path(__file__).parent/"assets"
WAV_PATH = str(__assets/"call.wav")

def load_and_convert_wav(file_path, target_rate):
    """
    WAVファイルを指定されたサンプルレートに変換して返す関数。
    """
    # WAVファイルを読み込み、pydubのAudioSegment形式に変換
    audio = AudioSegment.from_wav(file_path)

    # サンプルレートを変換
    if audio.frame_rate != target_rate:
        audio = audio.set_frame_rate(target_rate)

    # バイトデータに変換
    wav_data = io.BytesIO()
    audio.export(wav_data, format="wav")
    wav_data.seek(0)

    # オーディオ情報を取得
    wf = wave.open(wav_data, 'rb')
    audio_data = wf.readframes(wf.getnframes())
    channels = wf.getnchannels()
    sampwidth = wf.getsampwidth()
    framerate = wf.getframerate()

    return audio, channels, sampwidth, framerate  # AudioSegmentオブジェクトを返す

def vvox_test(text):
    """
    合成音声とcall.wavを結合して再生する。
    """
    host = "127.0.0.1"
    port = 50021

    params = (
        ('text', text),
        ('speaker', 3),  # 3:ずんだもん
    )

    # 音声合成用のクエリを作成
    query = requests.post(
        f'http://{host}:{port}/audio_query',
        params=params
    )

    # 音声合成を実施
    synthesis = requests.post(
        f'http://{host}:{port}/synthesis',
        headers={"Content-Type": "application/json"},
        params=params,
        data=json.dumps(query.json())
    )

    # 合成音声をバイナリ形式で取得
    voice = synthesis.content

    # 合成音声をWAV形式に変換（pydubで処理しやすくする）
    voice_audio = AudioSegment.from_file(io.BytesIO(voice), format="wav")
    target_rate = voice_audio.frame_rate  # 合成音声のサンプルレート

    # call.wavを読み込み、合成音声と同じサンプルレートに変換
    call_audio, channels, sampwidth, framerate = load_and_convert_wav(WAV_PATH, target_rate)

    # call.wavの音量を70%に調整 (-3.1 dBで約70%の音量)
    call_audio = call_audio - 3.1

    # call.wavと合成音声を結合
    combined_audio = call_audio + voice_audio

    # 結合された音声をWAVバイトデータに変換
    combined_data = io.BytesIO()
    combined_audio.export(combined_data, format="wav")
    combined_data.seek(0)

    # 再生処理
    wf = wave.open(combined_data, 'rb')
    pya = pyaudio.PyAudio()
    stream = pya.open(format=pya.get_format_from_width(wf.getsampwidth()),
                      channels=wf.getnchannels(),
                      rate=wf.getframerate(),
                      output=True)

    # 音声を再生
    data = wf.readframes(1024)
    while data:
        stream.write(data)
        data = wf.readframes(1024)

    # ストリームを停止・終了
    stream.stop_stream()
    stream.close()
    pya.terminate()
