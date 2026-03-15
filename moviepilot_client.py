#!/usr/bin/env python3
import os
import sys
import json
import argparse
import requests
from typing import Optional, Dict, Any, List

class MoviePilotClient:
    """
    MoviePilot 客户端，用于调用 MoviePilot (v2) 的 API。
    遵循 KISS 原则，封装核心常用的操作：搜索、订阅和下载查询。
    """

    def __init__(self, base_url: Optional[str] = None, api_token: Optional[str] = None):
        # 优先从环境变量读取
        self.base_url = (base_url or os.environ.get("MOVIEPILOT_URL") or "http://127.0.0.1:3000").rstrip("/")
        self.api_token = api_token or os.environ.get("MOVIEPILOT_API_TOKEN") or ""

        # 读取同级目录下的 config.json
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    if not api_token and not os.environ.get("MOVIEPILOT_API_TOKEN"):
                        self.api_token = config.get("MOVIEPILOT_API_TOKEN", self.api_token)
                    if not base_url and not os.environ.get("MOVIEPILOT_URL"):
                        self.base_url = config.get("MOVIEPILOT_URL", self.base_url).rstrip("/")
            except Exception as e:
                print(f"[!] Warning: Failed to parse config.json - {e}", file=sys.stderr)

        self.headers = {"Content-Type": "application/json"}

    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        url = f"{self.base_url}{endpoint}"
        # MoviePilot v2 接口通常在 query params 中传递 token
        if self.api_token:
            if "params" not in kwargs:
                kwargs["params"] = {}
            if "token" not in kwargs["params"]:
                kwargs["params"]["token"] = self.api_token
        try:
            response = requests.request(method, url, headers=self.headers, timeout=15, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"[!] HTTP Error: {e.response.status_code} - {e.response.text}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"[!] Request Error: {e}", file=sys.stderr)
            raise

    # ---------------- 仪表盘 (Dashboard) ---------------- #

    def get_system_statistic(self) -> Dict[str, Any]:
        """影视库统计：电影数、剧集数、集数"""
        return self._request("GET", "/api/v1/dashboard/statistic")

    def get_system_storage(self) -> Dict[str, Any]:
        """存储空间信息"""
        return self._request("GET", "/api/v1/dashboard/storage")

    def get_downloader_info(self) -> Dict[str, Any]:
        """下载器信息"""
        return self._request("GET", "/api/v1/dashboard/downloader")

    def get_scheduler_info(self) -> List[Dict[str, Any]]:
        """后台服务信息"""
        return self._request("GET", "/api/v1/dashboard/schedule")

    def get_process_info(self) -> List[Dict[str, Any]]:
        """进程信息"""
        return self._request("GET", "/api/v1/dashboard/processes")

    # ---------------- 站点 (Site) ---------------- #

    def get_sites(self) -> List[Dict[str, Any]]:
        """所有站点"""
        return self._request("GET", "/api/v1/site/")

    def test_site(self, site_id: int) -> Dict[str, Any]:
        """测试站点"""
        return self._request("GET", f"/api/v1/site/test/{site_id}")

    def sync_cookiecloud(self) -> Dict[str, Any]:
        """同步 CookieCloud"""
        return self._request("POST", "/api/v1/site/cookiecloud")

    # ---------------- 订阅 (Subscribe) ---------------- #

    def get_subscribes(self) -> List[Dict[str, Any]]:
        """所有订阅"""
        return self._request("GET", "/api/v1/subscribe/")

    def add_subscribe(self, media_id: int, type_name: str = "movie", season: Optional[int] = None) -> Dict[str, Any]:
        """添加订阅"""
        data = {"tmdbid": media_id, "type": "电影" if type_name == "movie" else "电视剧"}
        if season is not None:
            data["season"] = season
        return self._request("POST", "/api/v1/subscribe/", json=data)

    def delete_subscribe(self, sub_id: int) -> Dict[str, Any]:
        """删除订阅"""
        return self._request("DELETE", f"/api/v1/subscribe/{sub_id}")

    def refresh_subscribes(self) -> Dict[str, Any]:
        """刷新订阅"""
        return self._request("GET", "/api/v1/subscribe/refresh")


    def get_site_rss(self):
        return self._request("GET", "/api/v1/site/rss")

    def get_site_resource(self, site_id: int, keyword: str = ""):
        return self._request("GET", f"/api/v1/site/resource/{site_id}", params={"keyword": keyword})

    def get_site_user(self, site_id: int):
        return self._request("GET", f"/api/v1/site/userdata/{site_id}")

    def get_sub_history(self, mtype: str):
        return self._request("GET", f"/api/v1/subscribe/history/{mtype}")

    def get_sub_popular(self, mtype: str = ""):
        return self._request("GET", "/api/v1/subscribe/popular", params={"stype": "电影" if mtype == "movie" else "电视剧" if mtype == "tv" else mtype} if mtype else {"stype": "电影"})

    def recognize_media(self, title: str):
        return self._request("GET", "/api/v1/media/recognize", params={"title": title})

    def get_media_detail(self, media_id: int):
        return self._request("GET", f"/api/v1/media/{media_id}")

    def get_douban_info(self, douban_id: str):
        return self._request("GET", f"/api/v1/douban/{douban_id}")

    def get_tmdb_seasons(self, tmdb_id: str):
        return self._request("GET", f"/api/v1/tmdb/seasons/{tmdb_id}")

    def get_sys_env(self):
        return self._request("GET", "/api/v1/system/env")

    def get_sys_users(self):
        return self._request("GET", "/api/v1/user/")

    def send_sys_msg(self, text: str):
        # We assume standard title and body. Post to /api/v1/message/
        return self._request("POST", "/api/v1/message/", json={"title": "Message from OpenClaw", "content": text})


    # ---------------- 媒体 (Media) ---------------- #

    def search_title(self, keyword: str, page: int = 1) -> Dict[str, Any]:
        """模糊搜索资源 (站点资源搜索)"""
        return self._request("GET", "/api/v1/search/title", params={"keyword": keyword, "page": page})

    def get_media_library(self, type_name: str = "movie", page: int = 1, count: int = 30) -> Any:
        """获取媒体库列表 (本地已入库)"""
        # 注意：此处根据开发文档，type_name 是 query 参数
        return self._request("GET", "/api/v1/media/library", params={"type_name": type_name, "page": page, "count": count})

    # ---------------- 下载 (Download) ---------------- #

    def get_downloads(self) -> List[Dict[str, Any]]:
        """正在下载的任务"""
        return self._request("GET", "/api/v1/download/")

    def add_download_simple(self, url: str) -> Dict[str, Any]:
        """通过链接添加下载"""
        return self._request("POST", "/api/v1/download/add", json={"url": url})

    def start_download(self, hash_string: str) -> Dict[str, Any]:
        """开始下载任务"""
        return self._request("GET", f"/api/v1/download/start/{hash_string}")

    def stop_download(self, hash_string: str) -> Dict[str, Any]:
        """暂停下载任务"""
        return self._request("GET", f"/api/v1/download/stop/{hash_string}")

    def delete_download(self, hash_string: str) -> Dict[str, Any]:
        """删除下载任务"""
        return self._request("DELETE", f"/api/v1/download/{hash_string}")

    # ---------------- 历史 (History) ---------------- #

    def get_transfer_history(self, page: int = 1, count: int = 30) -> Dict[str, Any]:
        """查询整理记录"""
        return self._request("GET", "/api/v1/history/transfer", params={"page": page, "count": count})

    def get_download_history(self, page: int = 1, count: int = 30) -> List[Dict[str, Any]]:
        """查询下载历史"""
        return self._request("GET", "/api/v1/history/download", params={"page": page, "count": count})

    # ---------------- 系统 (System) ---------------- #

    def restart_system(self) -> Dict[str, Any]:
        """重启系统"""
        return self._request("GET", "/api/v1/system/restart")

    def run_scheduler(self, jobid: str) -> Dict[str, Any]:
        """运行后台服务"""
        return self._request("GET", "/api/v1/system/runscheduler", params={"jobid": jobid})

def main():
    parser = argparse.ArgumentParser(description="MoviePilot-2 API 插件工具 - 根据开发文档优化版")
    parser.add_argument("--url", type=str, help="服务地址")
    parser.add_argument("--token", type=str, help="API Token")

    subparsers = parser.add_subparsers(dest="action", help="选择操作模块")

    # Status
    subparsers.add_parser("status", help="获取影视库统计及存储空间信息")

    # Site
    p_site = subparsers.add_parser("site", help="站点中心")
    p_site.add_argument("cmd", choices=["list", "test", "sync", "rss", "resource", "user"])
    p_site.add_argument("--key", type=str, help="搜索词")
    p_site.add_argument("--id", type=int, help="站点ID")

    # Subscribe
    p_sub = subparsers.add_parser("sub", help="订阅管理")
    p_sub.add_argument("cmd", choices=["list", "add", "del", "refresh", "history", "popular"])
    p_sub.add_argument("--id", type=int, help="订阅ID/TMDBID")
    p_sub.add_argument("--type", choices=["movie", "tv"], default="movie")
    p_sub.add_argument("--season", type=int, help="季数 (仅TV)")

    # Media
    p_media = subparsers.add_parser("media", help="媒体检索")
    p_media.add_argument("cmd", choices=["search", "library", "rec", "detail", "douban", "tmdb"])
    p_media.add_argument("--id", type=str, help="TMDB ID or 豆瓣ID")
    p_media.add_argument("keyword", nargs="?", help="搜索关键词")
    p_media.add_argument("--type", choices=["movie", "tv"], default="movie")
    p_media.add_argument("--page", type=int, default=1)
    p_media.add_argument("--count", type=int, default=30)

    # Download
    p_dl = subparsers.add_parser("dl", help="下载管理")
    p_dl.add_argument("cmd", choices=["list", "add", "start", "stop", "del", "info"])
    p_dl.add_argument("--url", help="下载链接")
    p_dl.add_argument("--hash", help="任务Hash")

    # History
    p_his = subparsers.add_parser("history", help="历史记录")
    p_his.add_argument("cmd", choices=["download", "transfer"])
    p_his.add_argument("--page", type=int, default=1)

    # System
    p_sys = subparsers.add_parser("sys", help="系统工具")
    p_sys.add_argument("cmd", choices=["restart", "run", "jobs", "info", "env", "user", "msg"])
    p_sys.add_argument("--text", type=str, help="消息内容")
    p_sys.add_argument("--job", help="Job ID")

    args = parser.parse_args()
    if not args.action:
        parser.print_help()
        sys.exit(0)

    client = MoviePilotClient(base_url=args.url, api_token=args.token)

    try:
        if args.action == "status":
            stat = client.get_system_statistic()
            storage = client.get_system_storage()
            print(json.dumps({"statistic": stat, "storage": storage}, indent=2, ensure_ascii=False))

        elif args.action == "site":
            if args.cmd == "list":
                print(json.dumps(client.get_sites(), indent=2, ensure_ascii=False))
            elif args.cmd == "test":
                print(json.dumps(client.test_site(args.id), indent=2))
            elif args.cmd == "sync":
                print(json.dumps(client.sync_cookiecloud(), indent=2))
            elif args.cmd == "rss":
                print(json.dumps(client.get_site_rss(), indent=2, ensure_ascii=False))
            elif args.cmd == "resource":
                print(json.dumps(client.get_site_resource(args.id, args.key), indent=2, ensure_ascii=False))
            elif args.cmd == "user":
                print(json.dumps(client.get_site_user(args.id), indent=2, ensure_ascii=False))

        elif args.action == "sub":
            if args.cmd == "list":
                print(json.dumps(client.get_subscribes(), indent=2, ensure_ascii=False))
            elif args.cmd == "add":
                print(json.dumps(client.add_subscribe(args.id, args.type, args.season), indent=2))
            elif args.cmd == "del":
                print(json.dumps(client.delete_subscribe(args.id), indent=2))
            elif args.cmd == "refresh":
                print(json.dumps(client.refresh_subscribes(), indent=2))
            elif args.cmd == "history":
                print(json.dumps(client.get_sub_history(args.type), indent=2, ensure_ascii=False))
            elif args.cmd == "popular":
                print(json.dumps(client.get_sub_popular(args.type), indent=2, ensure_ascii=False))

        elif args.action == "media":
            if args.cmd == "search":
                print(json.dumps(client.search_title(args.keyword, args.page), indent=2, ensure_ascii=False))
            elif args.cmd == "library":
                print(json.dumps(client.get_media_library(args.type, args.page, args.count), indent=2, ensure_ascii=False))
            elif args.cmd == "rec":
                print(json.dumps(client.recognize_media(args.keyword), indent=2, ensure_ascii=False))
            elif args.cmd == "detail":
                print(json.dumps(client.get_media_detail(args.id), indent=2, ensure_ascii=False))
            elif args.cmd == "douban":
                print(json.dumps(client.get_douban_info(args.id), indent=2, ensure_ascii=False))
            elif args.cmd == "tmdb":
                print(json.dumps(client.get_tmdb_seasons(args.id), indent=2, ensure_ascii=False))

        elif args.action == "dl":
            if args.cmd == "list":
                print(json.dumps(client.get_downloads(), indent=2, ensure_ascii=False))
            elif args.cmd == "add":
                print(json.dumps(client.add_download_simple(args.url), indent=2))
            elif args.cmd == "start":
                print(json.dumps(client.start_download(args.hash), indent=2))
            elif args.cmd == "stop":
                print(json.dumps(client.stop_download(args.hash), indent=2))
            elif args.cmd == "del":
                print(json.dumps(client.delete_download(args.hash), indent=2))
            elif args.cmd == "info":
                print(json.dumps(client.get_downloader_info(), indent=2, ensure_ascii=False))

        elif args.action == "history":
            if args.cmd == "download":
                print(json.dumps(client.get_download_history(args.page), indent=2, ensure_ascii=False))
            elif args.cmd == "transfer":
                print(json.dumps(client.get_transfer_history(args.page), indent=2, ensure_ascii=False))

        elif args.action == "sys":
            if args.cmd == "restart":
                print(json.dumps(client.restart_system(), indent=2))
            elif args.cmd == "run":
                print(json.dumps(client.run_scheduler(args.job), indent=2))
            elif args.cmd == "jobs":
                print(json.dumps(client.get_scheduler_info(), indent=2, ensure_ascii=False))
            elif args.cmd == "info":
                print(json.dumps(client.get_scheduler_info(), indent=2, ensure_ascii=False))
            elif args.cmd == "env":
                print(json.dumps(client.get_sys_env(), indent=2, ensure_ascii=False))
            elif args.cmd == "user":
                print(json.dumps(client.get_sys_users(), indent=2, ensure_ascii=False))
            elif args.cmd == "msg":
                print(json.dumps(client.send_sys_msg(args.text), indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"[!] 操作失败: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
