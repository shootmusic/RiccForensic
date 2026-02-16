"""
Reverse Image Search Engine
"""

import requests
import time
import re
from typing import List, Dict, Optional
from urllib.parse import quote_plus, urlparse

class ReverseSearch:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.delay = 2
    
    def search(self, image_path: str, engines: List[str] = None) -> Dict[str, List[Dict]]:
        if engines is None:
            engines = ['yandex', 'google', 'bing']
        
        results = {}
        for engine in engines:
            try:
                if engine == 'yandex':
                    results[engine] = self._yandex(image_path)
                elif engine == 'google':
                    results[engine] = self._google(image_path)
                elif engine == 'bing':
                    results[engine] = self._bing(image_path)
                time.sleep(self.delay)
            except Exception as e:
                results[engine] = []
        return results
    
    def _yandex(self, image_path: str) -> List[Dict]:
        url = 'https://yandex.com/images/search'
        
        with open(image_path, 'rb') as f:
            files = {'upfile': ('image.jpg', f, 'image/jpeg')}
            r = self.session.post(f"{url}?rpt=imageview", files=files, timeout=30)
        
        return self._parse_yandex(r.text)
    
    def _parse_yandex(self, html: str) -> List[Dict]:
        results = []
        
        for match in re.findall(r'"url":"(https?://[^"]+\.(?:jpg|jpeg|png|webp))"', html):
            results.append({"url": match, "type": "image", "source": "yandex"})
        
        for match in re.findall(r'href="(https?://[^"]+)"[^>]*class="[^"]*link[^"]*"', html):
            if self._valid(match):
                results.append({"url": match, "type": "page", "source": "yandex"})
        
        return results[:30]
    
    def _google(self, image_path: str) -> List[Dict]:
        temp = self._upload_temp(image_path)
        if not temp:
            return []
        
        url = f"https://www.google.com/searchbyimage?image_url={quote_plus(temp)}"
        r = self.session.get(url, timeout=30)
        return self._parse_google(r.text)
    
    def _parse_google(self, html: str) -> List[Dict]:
        results = []
        for url, title in re.findall(r'href="(https?://[^"]+)"[^>]*>([^<]+)</a>', html):
            if self._valid(url) and self._social(url):
                results.append({"url": url, "type": "page", "title": title.strip(), "source": "google"})
        return results[:25]
    
    def _bing(self, image_path: str) -> List[Dict]:
        temp = self._upload_temp(image_path)
        if not temp:
            return []
        
        url = f"https://www.bing.com/images/search?q=imgurl:{quote_plus(temp)}"
        r = self.session.get(url, timeout=30)
        
        results = []
        for match in re.findall(r'murl&quot;:&quot;(https?://[^&]+)&quot;', r.text):
            results.append({"url": match, "type": "image", "source": "bing"})
        return results[:25]
    
    def _upload_temp(self, image_path: str) -> Optional[str]:
        try:
            with open(image_path, 'rb') as f:
                r = self.session.post(
                    "https://api.imgur.com/3/image",
                    headers={"Authorization": "Client-ID 546c25a59c58ad7"},
                    files={"image": f},
                    timeout=30
                )
                return r.json().get("data", {}).get("link")
        except:
            return None
    
    def _valid(self, url: str) -> bool:
        skip = ['google.', 'gstatic.', 'facebook.com/tr', 'pixel.']
        return not any(s in url.lower() for s in skip)
    
    def _social(self, url: str) -> bool:
        patterns = ['instagram.com', 'facebook.com', 'twitter.com', 'x.com', 
                   'tiktok.com', 'linkedin.com', 'vk.com', 'reddit.com']
        return any(p in url.lower() for p in patterns)
    
    def filter_social(self, results: List[Dict]) -> List[Dict]:
        platforms = {
            'instagram.com': 'Instagram',
            'facebook.com': 'Facebook',
            'twitter.com': 'Twitter',
            'x.com': 'Twitter',
            'tiktok.com': 'TikTok',
            'linkedin.com': 'LinkedIn',
            'vk.com': 'VK',
            'reddit.com': 'Reddit'
        }
        
        filtered = []
        for r in results:
            url = r.get("url", "").lower()
            for domain, name in platforms.items():
                if domain in url:
                    r["platform"] = name
                    filtered.append(r)
                    break
        return filtered
