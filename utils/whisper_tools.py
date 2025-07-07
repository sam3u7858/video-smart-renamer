import torch
import whisper
import io
import re

# lazy loading the whisper model
WhisperClient = None
print(f"[Whisper] Use GPU: {torch.cuda.is_available()}")  # 應回傳 True


def format_timestamp(seconds: float) -> str:
    """格式化為 VTT 時間戳記"""
    milliseconds = int(seconds * 1000)
    hours = milliseconds // 3600000
    minutes = (milliseconds % 3600000) // 60000
    seconds = (milliseconds % 60000) // 1000
    millis = milliseconds % 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"


def write_vtt(segments, file):
    """將 segments 寫入 WebVTT 字幕格式"""
    print("WEBVTT\n", file=file)
    for segment in segments:
        start = format_timestamp(segment["start"])
        end = format_timestamp(segment["end"])
        text = segment["text"].strip().replace("-->", "->")
        print(f"{start} --> {end}\n{text}\n", file=file)


def simplify_vtt_timestamp_to_start_only(vtt_text):
    """
    將 VTT 字幕中的時間戳記從 HH:MM:SS.mmm --> HH:MM:SS.mmm
    簡化為僅保留起始時間，格式為 MM:SS

    範例：
    00:01:23.456 --> 00:01:25.789  轉為 01:23
    """
    def convert_to_mmss(ts):
        h, m, s_ms = ts.split(":")
        s = s_ms.split(".")[0]
        mm = int(h) * 60 + int(m)
        return f"{mm:02d}:{int(s):02d}"

    pattern = re.compile(
        r"(\d{2}:\d{2}:\d{2}\.\d{3}) --> \d{2}:\d{2}:\d{2}\.\d{3}")

    return pattern.sub(lambda m: convert_to_mmss(m.group(1)), vtt_text)


def get_whisper_client(model="base"):
    global WhisperClient
    if WhisperClient is None:
        WhisperClient = whisper.load_model(model)
    return WhisperClient


def getTranscript(filepath, client=None, return_format="vtt"):
    """
    取得本地音訊檔的逐字稿
    :param filepath: 本地音訊檔路徑（如 .mp3, .wav）
    :param client: 可選的 whisper model 實例
    :param return_format: vtt 或 text
    :return: 辨識出的文字內容
    """
    if client is None:
        client = get_whisper_client()

    # @gemini-2.5-pro: Enable verbose logging to debug transcription issues.
    print(f"[Whisper] Starting transcription for {filepath}...")
    result = client.transcribe(filepath, verbose=True)
    print(f"[Whisper] Transcription finished for {filepath}.")

    if return_format == "vtt":
        buffer = io.StringIO()
        write_vtt(result["segments"], buffer)
        return simplify_vtt_timestamp_to_start_only(buffer.getvalue())
    else:
        return result["text"]


if __name__ == "__main__":
    client = get_whisper_client("medium")
    text = getTranscript("./test/sample.mp3", client)
    print(text)
