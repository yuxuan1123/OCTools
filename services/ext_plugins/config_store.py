"""
OCTools/services/ext_plugins/config_store.py
───────────────────────────────────────────────
插件配置（config.json）读写。

结构：
{
  "settings": { "idle_timeout_min": 10 },
  "plugins": {
    "<plugin_id>": { "enabled": true, "load_mode": "lazy" }
  }
}

load_mode 取值：always / lazy / auto_recycle
"""

import json
import os

from services.ext_plugins import paths

LOAD_MODES = ("always", "lazy", "auto_recycle")

_DEFAULT = {
    "settings": {"idle_timeout_min": 10},
    "plugins": {},
}


def _deep_default() -> dict:
    import copy
    return copy.deepcopy(_DEFAULT)


def load_config() -> dict:
    """读取 config.json；缺失/损坏时回退默认配置。"""
    cfg = _deep_default()
    path = paths.config_file()
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                settings = data.get("settings")
                if isinstance(settings, dict):
                    cfg["settings"].update(settings)
                plugins = data.get("plugins")
                if isinstance(plugins, dict):
                    cfg["plugins"] = dict(plugins)
        except (OSError, ValueError) as e:
            print(f"[外部插件] config.json 读取失败，使用默认配置：{e}")
    return cfg


def save_config(cfg: dict):
    """原子写入 config.json。"""
    path = paths.config_file()
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    except OSError as e:
        print(f"[外部插件] 保存 config.json 失败：{e}")


def plugin_entry(cfg: dict, plugin_id: str) -> dict:
    """返回插件配置条目；不存在时返回默认值（不写回）。"""
    plugins = cfg.setdefault("plugins", {})
    entry = plugins.get(plugin_id)
    if not isinstance(entry, dict):
        return {"enabled": True, "load_mode": "lazy"}
    return entry


def set_enabled(cfg: dict, plugin_id: str, enabled: bool):
    """设置启用状态并写回配置。"""
    entry = plugin_entry(cfg, plugin_id)
    entry["enabled"] = bool(enabled)
    cfg["plugins"][plugin_id] = entry
    save_config(cfg)


def set_load_mode(cfg: dict, plugin_id: str, mode: str):
    """设置加载模式（校验取值）并写回配置。"""
    if mode not in LOAD_MODES:
        raise ValueError(f"非法加载模式：{mode}")
    entry = plugin_entry(cfg, plugin_id)
    entry["load_mode"] = mode
    cfg["plugins"][plugin_id] = entry
    save_config(cfg)
