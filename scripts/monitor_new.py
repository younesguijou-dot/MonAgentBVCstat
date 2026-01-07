#!/usr/bin/env python3
"""
Version 2 : Détecte et télécharge les NOUVEAUX PDF + notification Telegram
"""

import os
from pathlib import Path
from datetime import datetime
from scripts.download_all import URLS, BASE_URL  # Réutilise la logique

def get_new_pdfs():
    data_dir = Path("data/downloaded")
    last_scan_file = Path("data/last_scan.txt")
    
    # Lit le dernier scan
    if last_scan_file.exists():
        last_scan = datetime.fromisoformat(last_scan_file.read_text().strip())
    else:
        last_scan = datetime.min
    
    headers = {"User-Agent": "Mozilla/5.0..."}  # Même headers
    new_files = []
    
    for section, url in URLS.items():
        resp = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        for a in soup.find_all("a", href=True):
            if a["href"].lower().endswith(".pdf"):
                # Parse la date depuis le texte du lien (heuristique)
                link_text = a.get_text(strip=True)
                date_match = re.search(r"(\d{2}/\d{2}/\d{4})", link_text)
                
                if date_match:
                    file_date = datetime.strptime(date_match.group(1), "%d/%m/%Y")
                    if file_date > last_scan:
                        new_files.append(link_text)
    
    # Met à jour le dernier scan
    last_scan_file.write_text(datetime.now().isoformat())
    
    return new_files

def monitor_and_notify():
    new_pdfs = get_new_pdfs()
    
    if not new_pdfs:
        print("✅ Aucun nouveau PDF détecté")
        return
    
    message = f"🚨 <b>{len(new_pdfs)} NOUVEAUX PDF BVC</b>\n\n"
    for pdf in new_pdfs[:5]:  # Top 5
        message += f"📄 {pdf}\n"
    
    if len(new_pdfs) > 5:
        message += f"... et {len(new_pdfs)-5} de plus"
    
    # Envoie Telegram
    import asyncio
    from scripts.send_telegram import send_telegram
    asyncio.run(send_telegram(message))
    
    print(f"📤 Notification envoyée pour {len(new_pdfs)} nouveaux fichiers")

if __name__ == "__main__":
    monitor_and_notify()
