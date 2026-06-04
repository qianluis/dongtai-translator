#!/usr/bin/env python3
"""东台方言统一语音工具 - 所有智能体共用
用法: python3 tts_speak.py "要朗读的文本" [voice]
输出: MP3音频文件路径
"""
import asyncio, edge_tts, os, hashlib, sys

TTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tts_output')
os.makedirs(TTS_DIR, exist_ok=True)

def speak(text, voice='zh-CN-XiaoxiaoNeural'):
    """生成TTS音频，返回文件路径"""
    key = hashlib.md5(f'{text}_{voice}'.encode()).hexdigest()
    fpath = os.path.join(TTS_DIR, f'{key}.mp3')
    if os.path.exists(fpath) and os.path.getsize(fpath) > 100:
        return fpath
    async def gen():
        c = edge_tts.Communicate(text, voice)
        await c.save(fpath)
    asyncio.run(gen())
    return fpath

def speak_both(mandarin_text, dialect_text):
    """同时生成普通话和方言音频，返回两个文件路径"""
    mandarin_audio = speak(mandarin_text, 'zh-CN-XiaoxiaoNeural')  # 女声普通话
    dialect_audio = speak(dialect_text, 'zh-CN-YunxiNeural')       # 男声方言
    return mandarin_audio, dialect_audio

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 tts_speak.py '文本' [voice]")
        sys.exit(1)
    text = sys.argv[1]
    voice = sys.argv[2] if len(sys.argv) > 2 else 'zh-CN-XiaoxiaoNeural'
    path = speak(text, voice)
    print(path)
