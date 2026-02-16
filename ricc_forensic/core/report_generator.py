"""
Report Generator
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict

class ReportGenerator:
    def __init__(self):
        self.width = 70
    
    def generate(self, data: Dict, fmt: str = "text") -> str:
        if fmt == "json":
            return json.dumps(data, indent=2, ensure_ascii=False, default=str)
        elif fmt == "html":
            return self._html(data)
        return self._text(data)
    
    def _text(self, data: Dict) -> str:
        lines = [
            "=" * self.width,
            "RICC FORENSIC - INTELLIGENCE REPORT",
            "=" * self.width,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Target Hash: {data.get('face_hash', 'Unknown')}",
            f"Confidence: {data.get('confidence_score', 0):.1f}%",
            ""
        ]
        
        lines.extend([
            "EXECUTIVE SUMMARY",
            "-" * self.width,
            f"Accounts Found: {data.get('summary', {}).get('total_accounts', 0)}",
            f"Locations Tracked: {data.get('summary', {}).get('total_locations', 0)}",
            f"Contact Points: {data.get('summary', {}).get('total_contacts', 0)}",
            f"Risk Level: {self._risk_level(data)}",
            ""
        ])
        
        lines.append("DISCOVERED ACCOUNTS")
        lines.append("-" * self.width)
        for acc in data.get("accounts", []):
            lines.extend([
                f"[{acc.get('platform', 'Unknown')}]",
                f"  Username: @{acc.get('username', 'unknown')}",
                f"  Name: {acc.get('full_name', 'N/A')}",
                f"  Bio: {acc.get('biography', 'N/A')[:100]}",
                f"  Followers: {acc.get('followers', 'N/A')}",
                f"  URL: {acc.get('url', 'N/A')}",
                ""
            ])
        
        lines.extend([
            "LOCATION PATTERN",
            "-" * self.width
        ])
        for loc in data.get("locations", [])[:10]:
            lines.extend([
                f"  {loc.get('name')}",
                f"    Frequency: {loc.get('frequency', 0)}",
                f"    Coords: {loc.get('coordinates', {}).get('lat', 'N/A')}, {loc.get('coordinates', {}).get('lon', 'N/A')}",
                f"    Maps: {loc.get('maps_url', 'N/A')}",
                ""
            ])
        
        lines.extend([
            "CONTACT LEAKS",
            "-" * self.width
        ])
        contacts = data.get("contacts", {})
        if contacts.get("emails"):
            lines.append(f"  Emails: {', '.join(contacts['emails'])}")
        if contacts.get("phones"):
            lines.append(f"  Phones: {', '.join(contacts['phones'])}")
        if contacts.get("urls"):
            lines.append(f"  URLs: {len(contacts['urls'])} found")
        
        lines.extend([
            "",
            "=" * self.width,
            "END OF REPORT",
            "=" * self.width
        ])
        
        return "\n".join(lines)
    
    def _html(self, data: Dict) -> str:
        accounts_html = "".join([
            f'<div class="account"><h3>{acc.get("platform")}: @{acc.get("username")}</h3>'
            f'<p>{acc.get("biography", "")}</p></div>'
            for acc in data.get("accounts", [])
        ])
        
        return f"""<!DOCTYPE html>
<html>
<head>
<title>Ricc Forensic Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }}
.header {{ background: #333; padding: 20px; }}
.account {{ border-left: 4px solid #666; padding-left: 15px; margin: 10px 0; }}
</style>
</head>
<body>
<div class="header">
<h1>RICC FORENSIC REPORT</h1>
<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>
{accounts_html}
</body>
</html>"""
    
    def _risk_level(self, data: Dict) -> str:
        score = data.get("confidence_score", 0)
        if score > 80:
            return "CRITICAL"
        elif score > 60:
            return "HIGH"
        elif score > 40:
            return "MEDIUM"
        return "LOW"
    
    def save(self, report: str, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(report)
        return path
