import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# Hedef URL
URL = "https://teamrunbo.com/yaristakvimimiz/"

def scrape_races():
    print("Veriler çekiliyor...")
    
    # Siteye istek at (User-Agent ekleyerek tarayıcı gibi davranalım)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        response.encoding = 'utf-8' # Türkçe karakter sorunu olmaması için
    except Exception as e:
        print(f"Siteye erişilemedi: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    
    # TablePress tablosunu bul
    table = soup.find("table", {"id": "tablepress-1"})
    
    if not table:
        print("Tablo bulunamadı!")
        return

    races = []
    
    # Satırları gez (tbody içindeki tr'ler)
    rows = table.find("tbody").find_all("tr")
    
    for row in rows:
        cols = row.find_all("td")
        
        # Boş veya başlık satırıysa atla
        if not cols or len(cols) < 6:
            continue
            
        # Sadece "Ay" başlığı olan satırları atla (Örn: Ocak 2026)
        # Genelde 1. sütununda bold tag içinde ay ismi olur
        if "Ocak" in cols[0].text or "Şubat" in cols[0].text:
             # Ancak bazen ay satırları veri içermez, kontrol edelim.
             # Eğer 2. sütun boşsa büyük ihtimalle ay başlığıdır.
             if not cols[1].text.strip():
                 continue

        # Verileri ayıkla
        try:
            # 1. Sütun: Tip / İkon
            race_type_raw = cols[0].get_text(strip=True)
            
            # 2. Sütun: Yarış Adı ve Link
            name_cell = cols[1]
            race_name = name_cell.get_text(strip=True)
            link_tag = name_cell.find("a")
            race_link = link_tag["href"] if link_tag else "#"
            
            # 3. Sütun: Tarih
            race_date = cols[2].get_text(strip=True)
            
            # 4. Sütun: Yer
            race_location = cols[3].get_text(strip=True)
            
            # 5. Sütun: Mesafe
            race_distance = cols[4].get_text(strip=True)
            
            # 6. Sütun: Notlar / Etiketler
            notes_raw = cols[5].get_text(strip=True)
            tags = []
            if "TR" in notes_raw or "🇹🇷" in notes_raw: tags.append("TR")
            if "UTMB" in notes_raw: tags.append("UTMB")
            if "İPTAL" in notes_raw or "ERTELENDİ" in notes_raw: tags.append("İPTAL/ERTELEME")
            if "YENİ" in notes_raw: tags.append("YENİ")
            
            # Kategoriyi ikon veya metinden tahmin et
            category = "Diğer"
            if "🌳" in race_type_raw or "Patika" in race_type_raw: category = "Patika"
            elif "🛣" in race_type_raw or "Yol" in race_type_raw: category = "Yol"
            elif "🏊" in race_type_raw: category = "Yüzme"
            elif "🚵" in race_type_raw or "Bisiklet" in race_type_raw: category = "Bisiklet"
            elif "🧭" in race_type_raw: category = "Oryantiring"

            # Yarış nesnesini oluştur
            race_data = {
                "id": len(races) + 1,
                "type": category,
                "icon": race_type_raw, # Orijinal ikonu koru
                "name": race_name,
                "date": race_date,
                "location": race_location,
                "distance": race_distance,
                "link": race_link,
                "tags": tags,
                "notes": notes_raw
            }
            
            # Boş isimli satırları ekleme
            if race_name:
                races.append(race_data)

        except Exception as e:
            print(f"Satır işlenirken hata: {e}")
            continue

    # JSON dosyasına kaydet
    with open("races.json", "w", encoding="utf-8") as f:
        json.dump(races, f, ensure_ascii=False, indent=2)
    
    print(f"Toplam {len(races)} yarış başarıyla kaydedildi: races.json")

if __name__ == "__main__":
    scrape_races()
