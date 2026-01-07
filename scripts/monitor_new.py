#!/usr/bin/env python3
"""
Version 2 : Monitor NOUVEAUX PDF (AUTONOME)
"""

import os
import re
from pathlib import Path
from datetime import datetime
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://www.casablanca-bourse.com"
URLS = {
    "stats": "https://www.casablanca-bourse.com/fr/editions-statistiques",
    "communiques": "https://www.casablanca-bourse.com/fr/publications-des-emetteurs",
}

def scan_all_urls():
    """Scanne toutes les pages et retourne les liens PDF avec dates"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    session = requests.Session()
    session.verify = False
    
    all_pdfs = []
    
    for section, url in URLS.items():
        print(f"🔍 Scan {section}...")
        try:
            resp = session.get(url, headers=headers, timeout=30)
            soup = BeautifulSoup(resp.text, "html.parser")
            
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.lower().endswith(".pdf"):
                    label = a.get_text(strip=True)
                    full_url = urljoin(BASE_URL, href)
                    
                    # Extrait date du texte (dd/mm/yyyy)
                    date_match = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})", label)
                    if date_match:
                        try:
                            file_date = datetime.strptime(date_match.group(1), "%d/%m/%Y")
                            all_pdfs.append({
                                "section": section,
                                "label": label,
                                "url": full_url,
                                "date": file_date
                            })
                        except ValueError:
                            pass  # Date mal formée
            
        except Exception as e:
            print(f"❌ Erreur {section}: {e}")
    
    return sorted(all_pdfs, key=lambda x: x["date"], reverse=True)

def get_last_scan_date():
    last_file = Path("data/last_scan.txt")
    if last_file.exists():
        return datetime.fromisoformat(last_file.read_text().strip())
    return datetime(2020, 1, 1)  # Date très ancienne

def monitor_and_notify():
    print("🚀 Début monitoring PDF BVC...")
    
    # Scan complet
    all_pdfs = scan_all_urls()
    last_scan = get_last_scan_date()
    
    # Filtre les nouveaux
    new_pdfs = [pdf for pdf in all_pdfs if pdf["date"] > last_scan]
    
    if not new_pdfs:
        print("✅ Aucun nouveau PDF détecté")
        Path("data/last_scan.txt").write_text(datetime.now().isoformat())
        return
    
    # Prépare message Telegram
    message = f"🚨 <b>{len(new_pdfs)} NOUVEAUX PDF BVC</b>\n\n"
    for pdf in new_pdfs[:10]:  # Top 10
        message += f"📄 <b>{pdf['label'][:60]}...</b>\n"
        message += f"📅 {pdf['date'].strftime('%d/%m/%Y')} | {pdf['section'].upper()}\n\n"
    
    if len(new_pdfs) > 10:
        message += f"➕ {len(new_pdfs)-10} de plus"
    
    # Sauvegarde dernier scan
    Path("data/last_scan.txt").write_text(datetime.now().isoformat())
    
    # Envoi Telegram
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if token and chat_id:
        import asyncio
        from telegram import Bot
        bot = Bot(token=token)
        asyncio.run(bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML"))
        print("📱 Notification Telegram envoyée !")
    else:
        print("⚠️ Secrets Telegram manquants - message simulé :")
        print(message)
    
    print(f"✅ {len(new_pdfs)} nouveaux PDF détectés")

if __name__ == "__main__":
    monitor_and_notify()
