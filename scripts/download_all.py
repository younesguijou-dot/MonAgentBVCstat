#!/usr/bin/env python3
"""
Version 1 FIXÉE : SSL + certificats Ubuntu
"""

import os
import re
import ssl
import requests
from urllib.parse import urljoin
from pathlib import Path
from bs4 import BeautifulSoup
import urllib3

# Désactive les warnings SSL temporaires
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://www.casablanca-bourse.com"
URLS = {
    "stats": "https://www.casablanca-bourse.com/fr/editions-statistiques",
    "communiques": "https://www.casablanca-bourse.com/fr/publications-des-emetteurs",
}

def download_all():
    data_dir = Path("data/downloaded")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Headers + bypass SSL pour Ubuntu Actions
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # Session avec vérif SSL désactivée
    session = requests.Session()
    session.verify = False  # Bypass SSL strict
    
    total_files = 0
    
    for section, url in URLS.items():
        print(f"📁 {section.upper()}")
        try:
            resp = session.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            
            section_count = 0
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.lower().endswith(".pdf"):
                    full_url = urljoin(BASE_URL, href)
                    label = a.get_text(strip=True) or Path(href).name
                    fname = re.sub(r"[^\w\-\.]", "_", label.strip()) + ".pdf"
                    
                    path = data_dir / fname
                    
                    if path.exists():
                        print(f"  ⏭️  {fname}")
                        continue
                    
                    print(f"  📥 {fname}")
                    r = session.get(full_url, headers=headers, timeout=60, stream=True)
                    r.raise_for_status()
                    
                    with open(path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    print(f"     ✅ OK")
                    section_count += 1
                    total_files += 1
            
            print(f"     📊 {section_count} fichiers {section}")
            
        except Exception as e:
            print(f"     ❌ Erreur {section}: {e}")
    
    print(f"\n🎉 TOTAL: {total_files} fichiers dans data/downloaded/")
    return total_files

if __name__ == "__main__":
    download_all()
