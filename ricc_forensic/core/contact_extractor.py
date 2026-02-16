"""
Contact Information Extractor
"""

import re
from typing import Dict, List

class ContactExtractor:
    def __init__(self):
        self.patterns = {
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'phone_id': r'(?:\+62|62|0)[8-9][0-9]{8,11}',
            'phone_intl': r'\+\d{1,3}[\s.-]?\(?\d{1,4}\)?[\s.-]?\d{1,4}[\s.-]?\d{1,9}',
            'url': r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*',
            'telegram': r't\.me/(\w+)',
            'whatsapp': r'wa\.me/(\d+)'
        }
    
    def extract(self, text: str) -> Dict:
        if not text:
            return self._empty()
        
        results = {
            "emails": list(set(re.findall(self.patterns['email'], text))),
            "phones": [],
            "urls": list(set(re.findall(self.patterns['url'], text))),
            "telegram": re.findall(self.patterns['telegram'], text),
            "whatsapp": re.findall(self.patterns['whatsapp'], text)
        }
        
        phones = []
        phones.extend(re.findall(self.patterns['phone_id'], text))
        phones.extend(re.findall(self.patterns['phone_intl'], text))
        results["phones"] = list(set(phones))
        
        results["emails"] = self._filter_emails(results["emails"])
        results["urls"] = self._filter_urls(results["urls"])
        
        return results
    
    def from_profile(self, profile: Dict) -> Dict:
        text = ""
        if profile.get("biography"):
            text += profile["biography"] + " "
        if profile.get("full_name"):
            text += profile["full_name"] + " "
        
        for post in profile.get("recent_posts", []):
            if post.get("caption"):
                text += post["caption"] + " "
        
        return self.extract(text)
    
    def _filter_emails(self, emails: List[str]) -> List[str]:
        invalid = ['example.com', 'test.com', 'domain.com']
        return [e for e in emails if not any(i in e.lower() for i in invalid)]
    
    def _filter_urls(self, urls: List[str]) -> List[str]:
        skip = ['instagram.com', 'facebook.com', 'twitter.com', 'youtube.com', 'bit.ly', 't.co']
        return [u for u in urls if not any(s in u.lower() for s in skip)]
    
    def _empty(self) -> Dict:
        return {"emails": [], "phones": [], "urls": [], "telegram": [], "whatsapp": []}
    
    def cross_reference(self, profiles: List[Dict]) -> Dict:
        emails = set()
        phones = set()
        
        for p in profiles:
            c = p.get("contacts", {})
            emails.update(c.get("emails", []))
            phones.update(c.get("phones", []))
        
        return {
            "emails": list(emails),
            "phones": list(phones),
            "profile_count": len(profiles)
        }
