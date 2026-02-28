"""
字体自动下载模块

在极端边界环境下（完全无中文字体），自动下载并安装轻量级中文字体。
提供多种下载源和回退机制，确保在各种网络环境下都能工作。
"""

import hashlib
import os
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

from archinstall.lib.output import debug, info, warn


# 轻量级中文字体下载源（按优先级排序）
# 优先选择体积小、下载快、许可证开放的字体
FALLBACK_FONTS: list[dict] = [
	{
		'name': 'WenQuanYi Bitmap Song',
		'package': 'wqy-bitmapfont',
		'url': 'https://downloads.sourceforge.net/project/wqy/wqy-bitmapfont/0.9.9-1/wqy-bitmapfont-pcf-0.9.9-1.tar.gz',
		'size_mb': 4.5,
		'license': 'GPLv2',
		'description': '文泉驿点阵宋体，仅包含常用汉字，体积小',
		'checksum': None,  # 可选：添加校验和验证
	},
	{
		'name': 'GNU Unifont',
		'package': 'unifont',
		'url': 'https://ftp.gnu.org/gnu/unifont/unifont-15.1.04/unifont-15.1.04.pcf.gz',
		'size_mb': 12,
		'license': 'GPLv2+',
		'description': 'GNU Unifont，包含所有 Unicode 字符，包括中文',
		'checksum': None,
	},
]

# 镜像源（用于加速下载）
MIRROR_URLS: list[str] = [
	'https://mirrors.tuna.tsinghua.edu.cn/',
	'https://mirrors.ustc.edu.cn/',
	'https://mirrors.aliyun.com/',
]

# 本地缓存目录
FONT_CACHE_DIR = Path('/var/cache/archinstall/fonts')


class FontDownloadError(Exception):
	"""字体下载错误"""
	pass


class FontInstallError(Exception):
	"""字体安装错误"""
	pass


def ensure_font_cache_dir() -> Path:
	"""确保字体缓存目录存在"""
	FONT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
	return FONT_CACHE_DIR


def download_with_progress(
	url: str,
	destination: Path,
	timeout: int = 30,
	chunk_size: int = 8192,
) -> bool:
	"""
	带进度显示的下载函数

	Args:
		url: 下载 URL
		destination: 目标路径
		timeout: 超时时间（秒）
		chunk_size: 下载块大小

	Returns:
		是否成功
	"""
	try:
		debug(f'开始下载: {url}')

		req = urllib.request.Request(url)
		req.add_header('User-Agent', 'archinstall-font-downloader/1.0')

		with urllib.request.urlopen(req, timeout=timeout) as response:
			total_size = int(response.headers.get('Content-Length', 0))
			downloaded = 0

			with open(destination, 'wb') as f:
				while True:
					chunk = response.read(chunk_size)
					if not chunk:
						break
					f.write(chunk)
					downloaded += len(chunk)

					# 每 100KB 显示一次进度
					if total_size > 0 and downloaded % (100 * 1024) < chunk_size:
						percent = (downloaded / total_size) * 100
						debug(f'下载进度: {percent:.1f}%')

		debug(f'下载完成: {destination} ({downloaded} bytes)')
		return True

	except urllib.error.URLError as e:
		warn(f'下载失败 {url}: {e}')
		return False
	except TimeoutError:
		warn(f'下载超时 {url}')
		return False
	except Exception as e:
		warn(f'下载出错 {url}: {e}')
		return False


def verify_checksum(file_path: Path, expected_checksum: str, algorithm: str = 'sha256') -> bool:
	"""
	验证文件校验和

	Args:
		file_path: 文件路径
		expected_checksum: 预期的校验和
		algorithm: 哈希算法

	Returns:
		是否匹配
	"""
	try:
		hasher = hashlib.new(algorithm)
		with open(file_path, 'rb') as f:
			for chunk in iter(lambda: f.read(8192), b''):
				hasher.update(chunk)

		computed = hasher.hexdigest()
		return computed.lower() == expected_checksum.lower()
	except Exception as e:
		debug(f'校验和验证失败: {e}')
		return False


def extract_font_archive(archive_path: Path, extract_to: Path) -> list[Path]:
	"""
	解压字体压缩包

	Args:
		archive_path: 压缩包路径
		extract_to: 解压目标目录

	Returns:
		解压出的字体文件列表
	"""
	extracted_fonts: list[Path] = []

	try:
		if archive_path.suffix == '.gz' and not archive_path.suffixes:
			# 单个 .gz 文件（如 unifont.pcf.gz）
			import gzip
			extract_to.mkdir(parents=True, exist_ok=True)
			output_path = extract_to / archive_path.stem

			with gzip.open(archive_path, 'rb') as f_in:
				with open(output_path, 'wb') as f_out:
					f_out.write(f_in.read())

			extracted_fonts.append(output_path)
			debug(f'解压完成: {output_path}')

		elif archive_path.suffix in ['.tar', '.gz', '.tgz', '.bz2', '.xz']:
			# tar 压缩包
			with tarfile.open(archive_path, 'r:*') as tar:
				# 只提取字体文件
				font_extensions = ['.pcf', '.pcf.gz', '.ttf', '.otf']
				for member in tar.getmembers():
					if any(member.name.endswith(ext) for ext in font_extensions):
						tar.extract(member, extract_to)
						extracted_fonts.append(extract_to / member.name)

			debug(f'从压缩包提取 {len(extracted_fonts)} 个字体文件')

		return extracted_fonts

	except Exception as e:
		warn(f'解压失败 {archive_path}: {e}')
		return []


def install_font_to_system(font_files: list[Path], target: Path | None = None) -> bool:
	"""
	安装字体到系统

	Args:
		font_files: 字体文件列表
		target: 目标系统路径（None 表示当前系统）

	Returns:
		是否成功
	"""
	try:
		if target is None:
			# 安装到当前系统
			font_dir = Path('/usr/share/fonts/archinstall-extra')
		else:
			# 安装到目标系统
			font_dir = target / 'usr/share/fonts/archinstall-extra'

		font_dir.mkdir(parents=True, exist_ok=True)

		installed = []
		for font_file in font_files:
			if font_file.exists():
				dest = font_dir / font_file.name
				# 复制文件
				import shutil
				shutil.copy2(font_file, dest)
				installed.append(dest)
				debug(f'已安装字体: {dest}')

		if installed:
			# 更新字体缓存
			if target is None:
				os.system('fc-cache -fv ' + str(font_dir) + ' 2>/dev/null')
			info(f'成功安装 {len(installed)} 个字体文件')
			return True
		else:
			warn('没有字体文件被安装')
			return False

	except Exception as e:
		warn(f'安装字体失败: {e}')
		return False


def download_and_install_font(
	font_info: dict | None = None,
	target: Path | None = None,
	use_cache: bool = True,
	timeout: int = 30,
) -> bool:
	"""
	下载并安装字体

	Args:
		font_info: 字体信息字典（None 使用默认第一个）
		target: 目标系统路径
		use_cache: 是否使用缓存
		timeout: 下载超时

	Returns:
		是否成功
	"""
	if font_info is None:
		font_info = FALLBACK_FONTS[0]

	font_name = font_info['name']
	font_url = font_info['url']
	font_package = font_info['package']

	info(f'正在下载字体: {font_name}')

	# 确定缓存路径
	cache_dir = ensure_font_cache_dir()
	archive_name = Path(font_url).name
	cache_path = cache_dir / archive_name

	# 检查缓存
	if use_cache and cache_path.exists():
		debug(f'使用缓存的字体文件: {cache_path}')
	else:
		# 下载字体
		if not download_with_progress(font_url, cache_path, timeout=timeout):
			# 尝试镜像源
			for mirror in MIRROR_URLS:
				mirror_url = mirror + font_url.split('/', 3)[-1]
				debug(f'尝试镜像源: {mirror_url}')
				if download_with_progress(mirror_url, cache_path, timeout=timeout):
					break
			else:
				raise FontDownloadError(f'无法从任何源下载字体: {font_name}')

	# 验证校验和（如果有）
	if font_info.get('checksum'):
		if not verify_checksum(cache_path, font_info['checksum']):
			raise FontDownloadError(f'字体文件校验和验证失败: {font_name}')

	# 解压字体
	with tempfile.TemporaryDirectory() as temp_dir:
		temp_path = Path(temp_dir)
		font_files = extract_font_archive(cache_path, temp_path)

		if not font_files:
			raise FontInstallError(f'无法从压缩包提取字体: {archive_name}')

		# 安装字体
		if install_font_to_system(font_files, target):
			info(f'字体 {font_name} 安装成功')
			return True
		else:
			raise FontInstallError(f'字体安装失败: {font_name}')


def ensure_chinese_font_available(
	target: Path | None = None,
	auto_download: bool = True,
	prefer_download: bool = False,
) -> bool:
	"""
	确保中文字体可用

	这是主要的入口函数，检查并确保系统有中文字体可用。

	Args:
		target: 目标系统路径
		auto_download: 是否自动下载字体
		prefer_download: 是否优先下载（即使已有字体）

	Returns:
		是否有中文字体可用
	"""
	from archinstall.lib.font_config import detect_chinese_support

	# 检查现有字体
	if not prefer_download:
		support = detect_chinese_support()
		if support['has_cjk_font']:
			debug('系统中已有 CJK 字体，跳过下载')
			return True

	if not auto_download:
		warn('未找到 CJK 字体且自动下载已禁用')
		return False

	# 尝试下载并安装字体
	for font_info in FALLBACK_FONTS:
		try:
			if download_and_install_font(font_info, target):
				return True
		except Exception as e:
			debug(f'字体 {font_info["name"]} 安装失败: {e}')
			continue

	warn('所有字体下载源都失败，无法安装中文字体')
	return False


def create_minimal_bitmap_font(target: Path | None = None) -> Path | None:
	"""
	创建最小化的位图字体（紧急回退方案）

	在完全无法下载字体时，使用内嵌的汉字数据创建位图字体。
	这是最后的手段，包含最常用的几十个汉字。

	Args:
		target: 目标系统路径

	Returns:
		字体目录路径，失败返回 None
	"""
	try:
		from archinstall.lib.emergency_font import create_emergency_font_package
		return create_emergency_font_package(target)
	except ImportError:
		# 如果 emergency_font 模块不可用，使用简化版本
		warn('emergency_font 模块不可用，使用简化字体')
		return _create_simple_emergency_font(target)
	except Exception as e:
		warn(f'创建紧急字体失败: {e}')
		return None


def _create_simple_emergency_font(target: Path | None = None) -> Path | None:
	"""
	创建简化的紧急字体（备用方案）

	当完整紧急字体模块不可用时使用。
	"""
	try:
		if target is None:
			font_dir = Path('/usr/share/fonts/archinstall-emergency')
		else:
			font_dir = target / 'usr/share/fonts/archinstall-emergency'

		font_dir.mkdir(parents=True, exist_ok=True)
		bdf_path = font_dir / 'simple-emergency.bdf'

		# 最小化的 BDF 字体（仅包含"中文字体缺失"提示）
		bdf_content = '''STARTFONT 2.1
FONT -Archinstall-Simple-Medium-R-Normal--12-120-75-75-C-120-ISO10646-1
SIZE 12 75 75
FONTBOUNDINGBOX 12 12 0 -2
STARTPROPERTIES 2
FONT_ASCENT 10
FONT_DESCENT 2
ENDPROPERTIES
CHARS 4
STARTCHAR U+4E2D
ENCODING 20013
SWIDTH 1000 0
DWIDTH 12 0
BBX 12 12 0 -2
BITMAP
000
000
7F8
408
408
7F8
408
408
408
408
000
000
ENDCHAR
STARTCHAR U+6587
ENCODING 25991
SWIDTH 1000 0
DWIDTH 12 0
BBX 12 12 0 -2
BITMAP
000
7F8
010
010
7F8
010
010
010
7F8
000
000
000
ENDCHAR
STARTCHAR U+7F3A
ENCODING 32570
SWIDTH 1000 0
DWIDTH 12 0
BBX 12 12 0 -2
BITMAP
7F8
408
408
7F8
408
408
7F8
408
408
408
000
000
ENDCHAR
STARTCHAR U+5931
ENCODING 22833
SWIDTH 1000 0
DWIDTH 12 0
BBX 12 12 0 -2
BITMAP
000
000
7F8
010
010
010
010
010
010
7F8
000
000
ENDCHAR
ENDFONT
'''
		bdf_path.write_text(bdf_content, encoding='utf-8')
		info(f'创建简化紧急字体: {bdf_path}')
		return font_dir

	except Exception as e:
		warn(f'创建简化字体失败: {e}')
		return None


# 便捷的导出函数
__all__ = [
	'download_and_install_font',
	'ensure_chinese_font_available',
	'create_minimal_bitmap_font',
	'download_with_progress',
	'install_font_to_system',
	'FALLBACK_FONTS',
	'FontDownloadError',
	'FontInstallError',
]
