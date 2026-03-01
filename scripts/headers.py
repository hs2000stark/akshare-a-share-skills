"""AKShare 请求头伪装模块。

设置真实浏览器的请求头，减少被识别为爬虫的概率。
"""

import logging
import random

import requests

logger = logging.getLogger(__name__)

# 常见浏览器的 User-Agent
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    # Chrome on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    # Firefox on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    # Safari on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    # Chrome on Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


class RequestHeaders:
    """请求头管理器。"""

    _session = None
    _initialized = False

    @classmethod
    def get_random_user_agent(cls) -> str:
        """获取随机的 User-Agent。"""
        return random.choice(USER_AGENTS)

    @classmethod
    def init_session(cls) -> None:
        """初始化全局 requests session，设置伪装请求头。"""
        if cls._initialized:
            return

        # 创建 session
        cls._session = requests.Session()

        # 设置默认请求头
        cls._session.headers.update({
            "User-Agent": cls.get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        })

        # 设置 referer 和 origin（某些网站需要）
        cls._session.headers.update({
            "Referer": "https://www.eastmoney.com/",
            "Origin": "https://www.eastmoney.com",
        })

        cls._initialized = True
        logger.info("请求头伪装已初始化")

    @classmethod
    def get_session(cls) -> requests.Session:
        """获取配置好的 session。"""
        if not cls._initialized:
            cls.init_session()
        return cls._session

    @classmethod
    def rotate_user_agent(cls) -> None:
        """轮换 User-Agent（每次请求随机更换）。"""
        if cls._session:
            cls._session.headers["User-Agent"] = cls.get_random_user_agent()

    @classmethod
    def set_headers(cls, **kwargs) -> None:
        """自定义请求头。"""
        if not cls._initialized:
            cls.init_session()
        cls._session.headers.update(kwargs)


def init_headers() -> None:
    """初始化请求头伪装（供外部调用）。"""
    RequestHeaders.init_session()


def get_session() -> requests.Session:
    """获取配置好的 session。"""
    return RequestHeaders.get_session()


def rotate_ua() -> None:
    """轮换 User-Agent。"""
    RequestHeaders.rotate_user_agent()
