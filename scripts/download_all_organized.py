#!/usr/bin/env python3
"""
Télécharge PDF BVC organisés par CATÉGORIE
"""

import os
import re
import requests
from urllib.parse import urljoin
from pathlib import Path
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings()

# Structure de dossiers souhaitée
CATEGORIES = {
    "01 Nouveaux Rapports": "nouveaux-rapports",
    "02 Communiqués": "communiques", 
    "03 Bulletin": "bulletin",
    "04 BCFR": "bcfc",
    "05 Résumé séance": "resume-seance",
    "06 Autres": "autres"
}

BASE_URL = "https://www.casablanca-bourse.com"
URLS = {
    "editions-stat": "https://www.casablanca-bourse.com/fr/editions-statistiques",
    "publications": "https://www.casablanca-bourse.com/fr/publications-des-emetteurs",
}

def get_category(filename: str) -> str:
    """Détermine la catégorie par mots-clés"""
    fname_lower = filename.lower()
    
    if any(x in fname_lower for x in ["bcfc", "bcfr"]):
        return "04 BCFR"
    elif any(x in fname_lower for x in ["communiqué", "comm", "cp"]):
        return "02 Communiqués"
    elif any(x in fname_lower for x in ["bulletin", "bull"]):
        return "03 Bulletin"
    elif any(x in fname_lower for x in ["résumé", "resume", "seance"]):
        return "05 Résumé séance"
    elif any(x in fname_lower for x in ["rapport", "mensuel"]):
        return "01 Nouveaux Rapports"
    else:
        return "06 Autres"

def download_organized():
    bvc_root = Path("BVC")
    bvc_root.mkdir(exist_ok=True)
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    session = requests.Session()
    session.verify = False
    
    total = 0
    
    for section_name, url in URLS.items():
        print(f"📁 {section_name}")
        resp = session.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.lower().endswith(".pdf"):
                label = a.get_text(strip=True) or Path(href).name
                fname = re.sub(r"[^\w\-\.]", "_", label.strip()) + ".pdf"
                
                category = get_category(fname)
                cat_dir = bvc_root / category
                
                cat_dir.mkdir(exist_ok=True)
                path = cat_dir / fname
                
                if path.exists():
                    print(f"  ⏭️  {category}/{fname}")
                    continue
                
                full_url = urljoin(BASE_URL, href)
                print(f"  📥 {category}/{fname}")
                
                r = session.get(full_url, headers=headers, timeout=60, stream=True)
                r.raise_for_status()
                
                with open(path, "wb") as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)
                
                print(f"     ✅ OK")
                total += 1
    
    print(f"\n🎉 {total} fichiers organisés dans BVC/")
    print_tree(bvc_root)

def print_tree(root: Path):
    print("\n📂 Structure créée :")
    for cat in sorted(root.iterdir()):
        count = len(list(cat.glob("*.pdf")))
        print(f"  📁 {cat.name:<20} ({count} PDFs)")

if __name__ == "__main__":
    download_organized()

