"""
octool/core/utils/exceptions.py
───────────────────────────────────────────────
自定义异常体系（核心引擎层共用）

分层：
  ConverterError            所有转换相关异常基类
  ├── FormatUnsupportedError  源/目标格式不支持
  ├── ConversionFailedError   转换过程失败（含底层库异常包装）
  ├── DependencyMissingError  缺少第三方依赖（ffmpeg / pandoc / paddleocr 等）
  └── FileMissingError        输入文件不存在 / 输出无法创建

设计原则：
  - 引擎层抛这些异常，业务层（services）捕获并转为日志与返回值；
  - 每个异常携带可读的 message，直接可用于日志展示。
"""


class ConverterError(Exception):
    """所有转换相关异常的基类"""

    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


class FormatUnsupportedError(ConverterError):
    """源/目标格式不支持或不可达"""

    def __init__(self, src: str = "", dst: str = "", detail: str = ""):
        msg = f"不支持的转换: {src} → {dst}"
        if detail:
            msg += f"（{detail}）"
        super().__init__(msg)
        self.src = src
        self.dst = dst


class ConversionFailedError(ConverterError):
    """转换过程失败（底层库报错 / 输出为空等）"""

    def __init__(self, message: str = "", cause: Exception = None):
        if cause is not None and message:
            message = f"{message}：{cause}"
        super().__init__(message)
        self.cause = cause


class DependencyMissingError(ConverterError):
    """缺少第三方依赖（ffmpeg / pandoc / paddleocr / kokoro …）"""

    def __init__(self, dependency: str, hint: str = ""):
        msg = f"缺少依赖: {dependency}"
        if hint:
            msg += f"（{hint}）"
        super().__init__(msg)
        self.dependency = dependency


class FileMissingError(ConverterError):
    """输入文件不存在 / 输出目录无法创建"""

    def __init__(self, path: str, role: str = "输入"):
        super().__init__(f"{role}路径无效: {path}")
        self.path = path
