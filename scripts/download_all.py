#!/usr/bin/env python3
"""
Version 1 : Télécharge TOUS les PDF BVC (communiqués, stats...)
"""

import os
import re
import requests
from urllib.parse import urljoin
from pathlib import Path
from bs4 import BeautifulSoup

BASE_URL = "https://www.casablanca-bourse.com"
URLS = {
    "stats": "https://www.casablanca-bourse.com/fr/editions-statistiques",
    "communiques": "https://www.casablanca-bourse.com/fr/publications-des-emetteurs",
    # Ajoute d'autres pages si besoin
}

def download_all():
    data_dir = Path("data/downloaded")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    all_files = []
    
    for section, url in URLS.items():
        print(f"📁 {section.upper()}")
        resp = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.lower().endswith(".pdf"):
                full_url = urljoin(BASE_URL, href)
                label = a.get_text(strip=True) or Path(href).name
                fname = re.sub(r"[^\w\-\.]", "_", label.strip()) + ".pdf"
                
                path = data_dir / fname
                all_files.append(str(path))
                
                if path.exists():
                    print(f"  ⏭️  {fname}")
                    continue
                
                print(f"  📥 {fname}")
                r = requests.get(full_url, headers=headers, timeout=60)
                r.raise_for_status()
                path.write_bytes(r.content)
                print(f"     ✅ OK")
    
    print(f"\n🎉 {len(all_files)} fichiers téléchargés dans data/downloaded/")
    return all_files

if __name__ == "__main__":
    download_all()
