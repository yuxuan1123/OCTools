"""
OCTools/config/stt_config.py
───────────────────────────────────────────────
语音识别（STT）配置模型，支持保存 / 加载。

设计要点：
  - 配置模型统一集中在 config/，引擎逻辑留在 core/engines/speech_engine.py
  - 模型目录来自 config/ui_config.json 的 paths.models.sensevoice，
    换机/换盘只改 JSON 里的 models.root，无需动代码
"""

import os
from dataclasses import dataclass

from config.ui_config import CONFIG as _C, migrate_model_path

# ════════════════════════════════════════════
#  模型路径 / 常量
# ════════════════════════════════════════════

# SenseVoiceSmall 本地模型目录
STT_DEFAULT_MODEL_DIR = _C.model_path("sensevoice")

# 识别语言选项（SenseVoice 支持）
STT_LANGUAGE_LABELS = [
    ("auto", "自动检测（中/英/粤语等）"),
    ("zh", "中文"),
    ("en", "英文"),
    ("yue", "粤语"),
    ("ja", "日语"),
    ("ko", "韩语"),
    ("nospeech", "仅静音检测"),
]

STT_DEVICE_LABELS = [
    ("cpu", "CPU（纯离线）"),
    ("cuda", "CUDA（GPU，需显卡驱动）"),
]


@dataclass
class SttConfig:
    """语音识别配置（音频 → TXT）"""
    model_dir: str = STT_DEFAULT_MODEL_DIR
    device: str = "cpu"            # cpu / cuda
    language: str = "auto"         # auto / zh / en / yue / ja / ko / nospeech
    use_itn: bool = True           # 数字归一化：1200 而非 一千二百

    def validate(self):
        errors = []
        if not self.model_dir or not os.path.isdir(self.model_dir):
            errors.append(f"语音识别模型目录不存在: {self.model_dir}")
        if self.device not in ("cpu", "cuda"):
            errors.append(f"未知设备: {self.device}")
        return errors

    # ── 序列化（与 TtsConfig 保持一致的接口）──
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, d):
        cfg = cls()
        for k, v in (d or {}).items():
            if hasattr(cfg, k):
                try:
                    setattr(cfg, k, v)
                except Exception:
                    pass
        # 历史配置里保存的可能是改名前的模型目录，修正为当前路径
        cfg.model_dir = migrate_model_path(cfg.model_dir, STT_DEFAULT_MODEL_DIR)
        return cfg

    def to_json(self, indent=2):
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_json(cls, s):
        import json
        return cls.from_dict(json.loads(s))

    def save_to_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @classmethod
    def from_file(cls, path):
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return cls.from_json(f.read())
        except Exception:
            return None


def default_config() -> SttConfig:
    return SttConfig()