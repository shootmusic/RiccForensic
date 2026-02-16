"""
Geolocation Analysis
"""

import requests
from typing import List, Dict, Optional
from urllib.parse import quote_plus
from datetime import datetime

class GeoAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.nominatim = "https://nominatim.openstreetmap.org/search"
    
    def analyze(self, posts: List[Dict]) -> List[Dict]:
        location_data = []
        
        for post in posts:
            loc = post.get("location")
            if loc and loc.get("name"):
                location_data.append({
                    "name": loc["name"],
                    "id": loc.get("id"),
                    "timestamp": post.get("timestamp"),
                    "post_id": post.get("id")
                })
        
        grouped = self._group(location_data)
        
        for name, data in grouped.items():
            coords = self._geocode(name)
            if coords:
                data["coordinates"] = coords
                data["maps_url"] = f"https://www.google.com/maps/@{coords['lat']},{coords['lon']},17z"
        
        return sorted(grouped.values(), key=lambda x: x["frequency"], reverse=True)
    
    def _group(self, data: List[Dict]) -> Dict[str, Dict]:
        groups = {}
        
        for item in data:
            name = item["name"]
            if name not in groups:
                groups[name] = {
                    "name": name,
                    "frequency": 0,
                    "timestamps": [],
                    "first_seen": None,
                    "last_seen": None
                }
            
            groups[name]["frequency"] += 1
            if item["timestamp"]:
                groups[name]["timestamps"].append(item["timestamp"])
        
        for name, data in groups.items():
            ts = [t for t in data["timestamps"] if t]
            if ts:
                data["first_seen"] = min(ts)
                data["last_seen"] = max(ts)
        
        return groups
    
    def _geocode(self, name: str) -> Optional[Dict]:
        try:
            r = self.session.get(
                self.nominatim,
                params={"q": name, "format": "json", "limit": 1},
                timeout=10
            )
            data = r.json()
            
            if data:
                return {
                    "lat": float(data[0]["lat"]),
                    "lon": float(data[0]["lon"]),
                    "display": data[0]["display_name"]
                }
        except:
            pass
        return None
    
    def timeline(self, locations: List[Dict]) -> List[Dict]:
        events = []
        
        for loc in locations:
            for ts in loc.get("timestamps", []):
                if ts:
                    events.append({
                        "timestamp": ts,
                        "date": datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M"),
                        "location": loc["name"],
                        "coordinates": loc.get("coordinates")
                    })
        
        return sorted(events, key=lambda x: x["timestamp"])
    
    def predict_home(self, locations: List[Dict]) -> Optional[Dict]:
        if not locations:
            return None
        
        home = max(locations, key=lambda x: x["frequency"])
        
        if home["frequency"] >= 3:
            return {
                "location": home["name"],
                "confidence": min(home["frequency"] * 10, 90),
                "coordinates": home.get("coordinates"),
                "reason": "Highest frequency"
            }
        
        return None
