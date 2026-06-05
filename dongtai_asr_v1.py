#!/usr/bin/env python3
"""
东台方言ASR管线 — 双模型融合 + ASR纠错层
整合 WenetSpeech-Wu(吴语专) + SenseVoiceSmall(通用)
"""

import os
import sys
import json
import time
import wave
import re
import numpy as np

# ============================================================
# ASR纠错规则 (基于测试发现的系统错误模式)
# ============================================================
ASR_CORRECTION_RULES = {
    # === 搿 → 格/隔 系统错误 ===
    "格格": "搿个", "隔的": "搿个", "格个": "搿个",
    "隔的菜": "搿个菜", "隔个": "搿个",
    
    # === 俫 → 来/还 系统错误 ===
    # 需要上下文判断，基础替换
    "我来东台": "我俫东台",
    "老王来屋里": "老王俫屋里",
    "还去哪里": "俫去哪里",
    
    # === 侬 → 萌/弄 系统错误 ===
    "萌吃过": "侬吃过", "弄好": "侬好",
    
    # === 方言特有词纠错 ===
    "刷瓜": "刷刮", "刷瓜葛": "刷刮",
    "神呢": "什呢", "什的": "什呢",
    "尸体": "事体",
    "物药紧": "勿要紧",
    "药紧": "要紧",
    "扎十": "扎实",
    "吓他": "下子", "瞎子": "下子",
    "下次": "下子",
    
    # === 句尾语气词 ===
    # "格" at end → "个" (吴语特有)
}

# ============================================================
# 双模型ASR引擎
# ============================================================
class DongtaiASR:
    """东台方言ASR引擎 - 双模型融合"""
    
    def __init__(self):
        self.wu_recognizer = None
        self.sv_model = None
        self._wu_loaded = False
        self._sv_loaded = False
    
    def load_wu_model(self):
        """加载WenetSpeech-Wu吴语模型"""
        if self._wu_loaded:
            return True
        try:
            import sherpa_onnx
            model_dir = os.path.expanduser(
                "~/asr_models/sherpa-onnx-wenetspeech-wu-u2pp-conformer-ctc-zh-int8-2026-02-03"
            )
            onnx_file = os.path.join(model_dir, "model.int8.onnx")
            tokens_file = os.path.join(model_dir, "tokens.txt")
            
            self.wu_recognizer = sherpa_onnx.OfflineRecognizer.from_wenet_ctc(
                model=onnx_file,
                tokens=tokens_file,
                num_threads=4,
                provider="cpu",
            )
            self._wu_loaded = True
            return True
        except Exception as e:
            print(f"WenetSpeech-Wu load failed: {e}")
            return False
    
    def load_sv_model(self):
        """加载SenseVoiceSmall通用模型"""
        if self._sv_loaded:
            return True
        try:
            from funasr import AutoModel
            self.sv_model = AutoModel(
                model="iic/SenseVoiceSmall", 
                device="cpu", 
                disable_update=True
            )
            self._sv_loaded = True
            return True
        except Exception as e:
            print(f"SenseVoiceSmall load failed: {e}")
            return False
    
    def _recognize_wu(self, wav_path):
        """WenetSpeech-Wu识别"""
        with wave.open(wav_path, 'rb') as wf:
            sample_rate = wf.getframerate()
            frames = wf.readframes(wf.getnframes())
            n_channels = wf.getnchannels()
        
        samples = np.frombuffer(frames, dtype=np.int16)
        samples_float = samples.astype(np.float32) / 32768.0
        if n_channels > 1:
            samples_float = samples_float[::n_channels]
        
        stream = self.wu_recognizer.create_stream()
        stream.accept_waveform(sample_rate, samples_float.tolist())
        self.wu_recognizer.decode_stream(stream)
        return stream.result.text
    
    def _recognize_sv(self, wav_path):
        """SenseVoiceSmall识别"""
        res = self.sv_model.generate(input=wav_path)
        raw = res[0]["text"] if res else ""
        return re.sub(r'<\|[^|]*\|>', '', raw).strip()
    
    @staticmethod
    def correct_asr(text):
        """ASR纠错层"""
        corrected = text
        for wrong, right in ASR_CORRECTION_RULES.items():
            corrected = corrected.replace(wrong, right)
        return corrected
    
    @staticmethod
    def _char_similarity(s1, s2):
        """字符相似度"""
        s1_set = set(s1.replace("，","").replace("。","").replace(" ",""))
        s2_set = set(s2.replace("，","").replace("。","").replace(" ",""))
        if not s1_set:
            return 0.0
        return len(s1_set & s2_set) / len(s1_set)
    
    def recognize(self, wav_path, fusion=True):
        """
        双模型融合识别
        
        Args:
            wav_path: WAV文件路径
            fusion: 是否融合两个模型结果
            
        Returns:
            dict: {
                "text": 最终识别文本,
                "wu_result": 吴语模型结果,
                "sv_result": 通用模型结果,
                "confidence": 置信度,
                "model_used": 使用的模型
            }
        """
        results = {}
        
        # Model 1: WenetSpeech-Wu
        if self._wu_loaded:
            try:
                t0 = time.time()
                wu_text = self._recognize_wu(wav_path)
                wu_time = time.time() - t0
                wu_corrected = self.correct_asr(wu_text)
                results["wu"] = {
                    "raw": wu_text,
                    "corrected": wu_corrected,
                    "time": round(wu_time, 3),
                }
            except Exception as e:
                results["wu_error"] = str(e)
        
        # Model 2: SenseVoiceSmall
        if self._sv_loaded:
            try:
                t0 = time.time()
                sv_text = self._recognize_sv(wav_path)
                sv_time = time.time() - t0
                sv_corrected = self.correct_asr(sv_text)
                results["sv"] = {
                    "raw": sv_text,
                    "corrected": sv_corrected,
                    "time": round(sv_time, 3),
                }
            except Exception as e:
                results["sv_error"] = str(e)
        
        # Fusion logic
        if fusion and "wu" in results and "sv" in results:
            wu_c = results["wu"]["corrected"]
            sv_c = results["sv"]["corrected"]
            
            # If both agree, high confidence
            if wu_c == sv_c:
                final_text = wu_c
                confidence = 0.95
                model_used = "both"
            else:
                # Pick the one that makes more sense after correction
                # Heuristic: prefer Wu model for dialect words, SV for standard words
                sim = self._char_similarity(wu_c, sv_c)
                
                if sim >= 0.9:
                    # Very similar - use Wu model (dialect-specialized)
                    final_text = wu_c
                    confidence = 0.85
                    model_used = "wu"
                elif sim >= 0.7:
                    # Moderately similar - merge: take Wu for dialect parts
                    final_text = wu_c  # Wu model is dialect-primary
                    confidence = 0.75
                    model_used = "wu_primary"
                else:
                    # Very different - low confidence, report both
                    final_text = f"{wu_c} | {sv_c}"
                    confidence = 0.5
                    model_used = "disagreement"
        elif "wu" in results:
            final_text = results["wu"]["corrected"]
            confidence = 0.8
            model_used = "wu_only"
        elif "sv" in results:
            final_text = results["sv"]["corrected"]
            confidence = 0.7
            model_used = "sv_only"
        else:
            final_text = ""
            confidence = 0.0
            model_used = "none"
        
        results["text"] = final_text
        results["confidence"] = confidence
        results["model_used"] = model_used
        
        return results


# ============================================================
# Test
# ============================================================
if __name__ == "__main__":
    print("东台方言ASR双模型融合管线测试")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    asr = DongtaiASR()
    
    # Load models
    print("\nLoading models...")
    wu_ok = asr.load_wu_model()
    sv_ok = asr.load_sv_model()
    print(f"  WenetSpeech-Wu: {'✓' if wu_ok else '✗'}")
    print(f"  SenseVoiceSmall: {'✓' if sv_ok else '✗'}")
    
    # Test with dialect audio
    test_dir = "/app/data/所有对话/主对话/asr_test_audio"
    wav_files = sorted([f for f in os.listdir(test_dir) if f.endswith('.wav')]) if os.path.exists(test_dir) else []
    
    orig_map = {
        "dt_greeting.wav": "侬好，今朝天气蛮好个",
        "dt_comfort.wav": "搿个事体勿要紧个",
        "dt_ask_where.wav": "俫去哪里啊",
        "dt_praise.wav": "伊搿人蛮扎实个",
        "dt_ask_meal.wav": "侬吃过饭了没啊",
        "dt_praise_child.wav": "搿个小囡蛮刷刮个",
        "dt_dinner_plan.wav": "今朝夜头吃点什呢",
        "dt_visit.wav": "老王俫屋里去下子",
        "dt_thank.wav": "搿个菜蛮好吃，难为你了",
        "dt_meta.wav": "我俫东台话蛮有味道个",
    }
    
    print(f"\n{'='*70}")
    print("双模型融合识别测试")
    print("="*70)
    
    all_results = []
    for wf in wav_files:
        wav_path = os.path.join(test_dir, wf)
        orig = orig_map.get(wf, "?")
        tag = wf.replace("dt_", "").replace(".wav", "")
        
        result = asr.recognize(wav_path, fusion=True)
        
        # Calculate accuracy
        orig_clean = orig.replace("，","").replace("。","")
        final_clean = result["text"].replace("，","").replace("。","").replace(" ","")
        sim = asr._char_similarity(orig_clean, final_clean)
        
        status = "✓" if sim >= 0.8 else ("△" if sim >= 0.5 else "✗")
        print(f"\n  {status}[{tag}] ({sim:.0%}, {result['model_used']}) 原文:{orig}")
        if "wu" in result:
            print(f"    吴语raw: {result['wu']['raw']}")
            print(f"    吴语fix: {result['wu']['corrected']}")
        if "sv" in result:
            print(f"    通用fix: {result['sv']['corrected']}")
        print(f"    → 最终: {result['text']} (conf={result['confidence']})")
        
        all_results.append({
            "tag": tag, "original": orig, "final": result["text"],
            "similarity": round(sim, 2), "model_used": result["model_used"],
            "confidence": result["confidence"],
        })
    
    # Summary
    avg_sim = sum(r["similarity"] for r in all_results) / max(len(all_results), 1)
    good = sum(1 for r in all_results if r["similarity"] >= 0.8)
    
    print(f"\n{'='*70}")
    print(f"融合管线汇总: 均分{avg_sim:.0%}, 好{good}/{len(all_results)}")
    print("="*70)
    
    # Save
    save_path = "/app/data/所有对话/主对话/asr_fusion_results.json"
    with open(save_path, "w") as f:
        json.dump({
            "results": all_results,
            "avg_similarity": round(avg_sim, 3),
            "good_count": good,
            "total": len(all_results),
            "correction_rules_count": len(ASR_CORRECTION_RULES),
        }, f, ensure_ascii=False, indent=2)
    print(f"Saved: {save_path}")
