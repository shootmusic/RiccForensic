"""
Social Media Profile Scraper
"""

import requests
import re
import time
from typing import Dict, List, Optional

class SocmedScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
            'Accept': 'application/json'
        })
        self.delay = 1.5
    
    def scrape(self, platform: str, username: str) -> Dict:
        if platform == "Instagram":
            return self._instagram(username)
        elif platform == "Twitter":
            return self._twitter(username)
        elif platform == "TikTok":
            return self._tiktok(username)
        return {"error": "Unsupported platform"}
    
    def _instagram(self, username: str) -> Dict:
        try:
            url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
            headers = {'X-IG-App-ID': '936619743392459'}
            
            r = self.session.get(url, headers=headers, timeout=10)
            
            if r.status_code == 200:
                data = r.json().get("data", {}).get("user", {})
                
                if not data:
                    return {"error": "User not found"}
                
                return {
                    "success": True,
                    "platform": "Instagram",
                    "username": username,
                    "full_name": data.get("full_name"),
                    "biography": data.get("biography"),
                    "followers": data.get("edge_followed_by", {}).get("count"),
                    "following": data.get("edge_follow", {}).get("count"),
                    "posts": data.get("edge_owner_to_timeline_media", {}).get("count"),
                    "is_private": data.get("is_private"),
                    "is_verified": data.get("is_verified"),
                    "external_url": data.get("external_url"),
                    "profile_pic": data.get("profile_pic_url_hd"),
                    "recent_posts": self._ig_posts(data)
                }
            
            return self._ig_embed(username)
            
        except Exception as e:
            return {"error": str(e)}
    
    def _ig_posts(self, user_data: Dict) -> List[Dict]:
        posts = []
        edges = user_data.get("edge_owner_to_timeline_media", {}).get("edges", [])
        
        for edge in edges[:15]:
            node = edge.get("node", {})
            loc = node.get("location", {})
            
            posts.append({
                "id": node.get("id"),
                "shortcode": node.get("shortcode"),
                "timestamp": node.get("taken_at_timestamp"),
                "caption": self._ig_caption(node),
                "likes": node.get("edge_liked_by", {}).get("count", 0),
                "is_video": node.get("is_video"),
                "location": {
                    "name": loc.get("name") if loc else None,
                    "id": loc.get("id") if loc else None
                }
            })
        
        return posts
    
    def _ig_caption(self, node: Dict) -> str:
        edges = node.get("edge_media_to_caption", {}).get("edges", [])
        return edges[0].get("node", {}).get("text", "") if edges else ""
    
    def _ig_embed(self, username: str) -> Dict:
        try:
            url = f"https://www.instagram.com/{username}/embed/"
            r = self.session.get(url, timeout=10)
            
            bio = re.search(r'<meta property="og:description" content="([^"]*)"', r.text)
            img = re.search(r'<meta property="og:image" content="([^"]*)"', r.text)
            
            return {
                "success": True,
                "platform": "Instagram",
                "username": username,
                "biography": bio.group(1) if bio else None,
                "profile_pic": img.group(1) if img else None,
                "method": "embed"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _twitter(self, username: str) -> Dict:
        instances = ["https://nitter.net", "https://nitter.it", "https://nitter.cz"]
        
        for inst in instances:
            try:
                url = f"{inst}/{username}"
                r = self.session.get(url, timeout=10)
                
                if r.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(r.text, 'html.parser')
                    
                    name = soup.find('a', class_='profile-card-fullname')
                    bio = soup.find('div', class_='profile-bio')
                    loc = soup.find('div', class_='profile-location')
                    stats = soup.find_all('span', class_='profile-stat-num')
                    
                    return {
                        "success": True,
                        "platform": "Twitter",
                        "username": username,
                        "full_name": name.text if name else None,
                        "biography": bio.text if bio else None,
                        "location": loc.text if loc else None,
                        "stats": [s.text for s in stats[:3]] if stats else []
                    }
            except:
                continue
        
        return {"error": "Twitter scrape failed"}
    
    def _tiktok(self, username: str) -> Dict:
        try:
            url = f"https://www.tiktok.com/@{username}"
            r = self.session.get(url, timeout=10)
            
            match = re.search(r'<script id="SIGI_STATE" type="application/json">([^<]+)</script>', r.text)
            
            if match:
                import json
                data = json.loads(match.group(1))
                user = data.get("UserModule", {}).get("users", {}).get(username, {})
                
                return {
                    "success": True,
                    "platform": "TikTok",
                    "username": username,
                    "nickname": user.get("nickname"),
                    "signature": user.get("signature"),
                    "followers": user.get("followerCount"),
                    "following": user.get("followingCount"),
                    "likes": user.get("heartCount"),
                    "videos": user.get("videoCount")
                }
            
            return {
                "success": False,
                "platform": "TikTok",
                "username": username,
                "note": "Requires browser automation"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def extract_from_url(self, url: str) -> Optional[Dict]:
        patterns = {
            r'instagram\.com/([^/?]+)': 'Instagram',
            r'facebook\.com/([^/?]+)': 'Facebook',
            r'twitter\.com/([^/?]+)': 'Twitter',
            r'x\.com/([^/?]+)': 'Twitter',
            r'tiktok\.com/@([^/?]+)': 'TikTok',
            r'linkedin\.com/in/([^/?]+)': 'LinkedIn',
            r'youtube\.com/(?:c/|channel/|user/|@)([^/?]+)': 'YouTube'
        }
        
        for pattern, platform in patterns.items():
            match = re.search(pattern, url.lower())
            if match:
                username = match.group(1).split('?')[0].split('#')[0]
                return {"platform": platform, "username": username, "url": url}
        
        return None
