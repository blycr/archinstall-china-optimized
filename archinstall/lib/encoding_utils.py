"""
编码安全工具模块

处理各种编码边界情况，确保在 Arch Linux ISO 环境下能安全处理各种字符编码。
"""

import os
import sys
from pathlib import Path
from typing import Any

from archinstall.lib.output import debug, warn


def safe_decode(
	data: bytes,
	encoding: str = 'utf-8',
	errors: str = 'backslashreplace',
	fallback_encoding: str = 'latin-1',
) -> str:
	"""
	安全地解码字节数据，处理各种编码错误

	Args:
		data: 要解码的字节数据
		encoding: 主要编码
		errors: 错误处理策略
		fallback_encoding: 失败时的备用编码

	Returns:
		解码后的字符串
	"""
	if not isinstance(data, bytes):
		return str(data)

	try:
		return data.decode(encoding, errors=errors)
	except (UnicodeDecodeError, LookupError):
		try:
			return data.decode(fallback_encoding, errors='replace')
		except Exception:
			# 最后的回退方案
			return data.decode('ascii', errors='replace')


def safe_encode(
	text: str,
	encoding: str = 'utf-8',
	errors: str = 'backslashreplace',
) -> bytes:
	"""
	安全地编码字符串

	Args:
		text: 要编码的字符串
		encoding: 目标编码
		errors: 错误处理策略

	Returns:
		编码后的字节数据
	"""
	if isinstance(text, bytes):
		return text

	try:
		return text.encode(encoding, errors=errors)
	except (UnicodeEncodeError, LookupError):
		# 使用备用编码
		return text.encode('latin-1', errors='replace')


def ensure_utf8_environment() -> None:
	"""
	确保当前环境使用 UTF-8 编码

	在 ISO 环境下，可能需要手动设置编码环境变量。
	"""
	# 设置 Python 的默认编码
	if hasattr(sys, 'setdefaultencoding'):
		# Python 3 中这通常在 sitecustomize.py 中设置
		pass

	# 设置环境变量
	utf8_vars = {
		'LC_ALL': 'C.UTF-8',
		'LANG': 'C.UTF-8',
		'PYTHONIOENCODING': 'utf-8',
	}

	for key, value in utf8_vars.items():
		if key not in os.environ or 'UTF-8' not in os.environ.get(key, '').upper():
			os.environ[key] = value
			debug(f'设置环境变量: {key}={value}')


def get_filesystem_encoding() -> str:
	"""
	获取文件系统编码

	Returns:
		文件系统编码名称
	"""
	try:
		# Python 3.6+
		encoding = sys.getfilesystemencoding()
		if encoding:
			return encoding
	except Exception:
		pass

	# 回退方案
	return 'utf-8'


def safe_path_to_str(path: Path | str) -> str:
	"""
	安全地将路径转换为字符串

	Args:
		path: 路径对象或字符串

	Returns:
		字符串形式的路径
	"""
	if isinstance(path, str):
		return path

	try:
		return str(path)
	except UnicodeEncodeError:
		# 处理包含特殊字符的路径
		try:
			return path.as_posix()
		except Exception:
			return repr(path)


def safe_read_text(
	path: Path,
	encoding: str = 'utf-8',
	errors: str = 'backslashreplace',
) -> str:
	"""
	安全地读取文本文件

	Args:
		path: 文件路径
		encoding: 文件编码
		errors: 错误处理策略

	Returns:
		文件内容
	"""
	try:
		return path.read_text(encoding=encoding, errors=errors)
	except UnicodeDecodeError:
		# 尝试使用不同编码
		for enc in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
			try:
				return path.read_text(encoding=enc)
			except UnicodeDecodeError:
				continue
		# 最后的回退方案
		return path.read_bytes().decode('utf-8', errors='replace')
	except Exception as e:
		warn(f'读取文件失败 {path}: {e}')
		raise


def safe_write_text(
	path: Path,
	content: str,
	encoding: str = 'utf-8',
	errors: str = 'backslashreplace',
) -> None:
	"""
	安全地写入文本文件

	Args:
		path: 文件路径
		content: 文件内容
		encoding: 文件编码
		errors: 错误处理策略
	"""
	# 确保父目录存在
	path.parent.mkdir(parents=True, exist_ok=True)

	try:
		path.write_text(content, encoding=encoding, errors=errors)
	except UnicodeEncodeError:
		# 尝试编码为字节后再写入
		data = content.encode(encoding, errors=errors)
		path.write_bytes(data)
	except Exception as e:
		warn(f'写入文件失败 {path}: {e}')
		raise


def sanitize_filename(filename: str) -> str:
	"""
	清理文件名，移除或替换不安全的字符

	Args:
		filename: 原始文件名

	Returns:
		清理后的文件名
	"""
	# 替换常见的危险字符
	unsafe_chars = '<>:"/\\|?*\x00-\x1f'
	result = filename

	for char in unsafe_chars:
		result = result.replace(char, '_')

	# 限制长度
	if len(result) > 255:
		name, ext = result[:251], ''
		if '.' in result:
			parts = result.rsplit('.', 1)
			name, ext = parts[0][:251], '.' + parts[1]
		result = name + ext

	# 确保不以空格或点结尾
	result = result.rstrip('. ')

	# 如果为空，使用默认名称
	if not result:
		result = 'unnamed'

	return result


def safe_command_output(
	output: bytes | str | None,
	default: str = '',
) -> str:
	"""
	安全地处理命令输出

	Args:
		output: 命令输出（字节或字符串）
		default: 默认值（如果处理失败）

	Returns:
		处理后的字符串
	"""
	if output is None:
		return default

	if isinstance(output, str):
		return output

	try:
		return safe_decode(output)
	except Exception as e:
		debug(f'解码命令输出失败: {e}')
		return default


def detect_encoding(data: bytes) -> str:
	"""
	尝试检测字节数据的编码

	这是一个简单的启发式检测，不是 100% 准确。

	Args:
		data: 字节数据

	Returns:
		检测到的编码名称
	"""
	# 检查 UTF-8 BOM
	if data.startswith(b'\xef\xbb\xbf'):
		return 'utf-8-sig'

	# 检查 UTF-16 BOM
	if data.startswith(b'\xff\xfe'):
		return 'utf-16-le'
	if data.startswith(b'\xfe\xff'):
		return 'utf-16-be'

	# 尝试 UTF-8
	try:
		data.decode('utf-8')
		return 'utf-8'
	except UnicodeDecodeError:
		pass

	# 尝试 Latin-1（总是成功，但可能不正确）
	return 'latin-1'


def configure_stdio_encoding() -> None:
	"""
	配置标准输入输出的编码

	在 ISO 环境下，标准输入输出可能使用错误的编码。
	"""
	import io

	# 重新配置 stdout 和 stderr
	if sys.stdout.encoding != 'UTF-8':
		try:
			sys.stdout = io.TextIOWrapper(
				sys.stdout.buffer,
				encoding='utf-8',
				errors='backslashreplace',
				line_buffering=True,
			)
			debug('stdout 编码已重新配置为 UTF-8')
		except Exception as e:
			debug(f'无法重新配置 stdout: {e}')

	if sys.stderr.encoding != 'UTF-8':
		try:
			sys.stderr = io.TextIOWrapper(
				sys.stderr.buffer,
				encoding='utf-8',
				errors='backslashreplace',
				line_buffering=True,
			)
			debug('stderr 编码已重新配置为 UTF-8')
		except Exception as e:
			debug(f'无法重新配置 stderr: {e}')


class EncodingSafeHandler:
	"""
	编码安全处理器

	提供上下文管理器，确保代码块在正确的编码环境下运行。
	"""

	def __init__(self, encoding: str = 'utf-8'):
		self.encoding = encoding
		self._original_env: dict[str, str | None] = {}

	def __enter__(self) -> 'EncodingSafeHandler':
		# 保存原始环境变量
		for key in ['LC_ALL', 'LANG', 'PYTHONIOENCODING']:
			self._original_env[key] = os.environ.get(key)

		# 设置 UTF-8 环境
		ensure_utf8_environment()
		return self

	def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
		# 恢复原始环境变量
		for key, value in self._original_env.items():
			if value is None:
				os.environ.pop(key, None)
			else:
				os.environ[key] = value


# 便捷的导出函数
__all__ = [
	'safe_decode',
	'safe_encode',
	'ensure_utf8_environment',
	'get_filesystem_encoding',
	'safe_path_to_str',
	'safe_read_text',
	'safe_write_text',
	'sanitize_filename',
	'safe_command_output',
	'detect_encoding',
	'configure_stdio_encoding',
	'EncodingSafeHandler',
]
