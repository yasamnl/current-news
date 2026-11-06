import os
import re
import time
import json
import feedparser
from datetime import datetime, timedelta
from supabase import create_client, Client
from groq import Groq

# Inisialisasi Environment Variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, GROQ_API_KEY]):
    raise ValueError("Environment variables SUPABASE_URL, SUPABASE_KEY, atau GROQ_API_KEY belum terkonfigurasi!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

# Konfigurasi RSS Feeds per Kategori
RSS_FEEDS = {
    'hukum': [
        'https://www.antaranews.com/rss/hukum.xml',
        'https://rss.tempo.co/hukum'
    ],
    'olahraga': [
        'https://www.antaranews.com/rss/olahraga.xml',
        'https://rss.tempo.co/olahraga'
    ]
}

def delete_old_articles(days_limit=30):
    """
    Menghapus artikel yang berumur lebih dari 'days_limit' hari dari Supabase
    untuk menghemat ruang penyimpanan.
    """
    cutoff_date = (datetime.now() - timedelta(days=days_limit)).isoformat()
    try:
        response = supabase.table("articles").delete().lt("created_at", cutoff_date).execute()
        print(f"[Cleanup DB] Berhasil membersihkan artikel yang dibuat sebelum {cutoff_date}")
    except Exception as e:
        print(f"[Cleanup DB Error] Gagal menghapus artikel lama: {e}")

def generate_slug(text):
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')

def process_with_groq(title, original_summary):
    """
    Memanggil Groq API untuk rewrite judul, ringkasan, dan 3 poin TL;DR
    """
    prompt = f"""
    Anda adalah editor berita senior. Berdasarkan berita berikut:
    Judul: {title}
    Ringkasan: {original_summary}

    Tolong hasilkan output JSON persis dalam format berikut (tanpa markdown atau teks tambahan):
    {{
        "click_title": "Judul berita yang sangat memancing rasa penasaran namun akurat",
        "ai_summary": "Ringkasan berita 2 paragraf pendek dalam bahasa kasual-profesional",
        "tldr": [
            "Poin penting 1 dalam 10 kata",
            "Poin penting 2 dalam 10 kata",
            "Poin penting 3 dalam 10 kata"
        ]
    }}
    """
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=600
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"[Warning] Groq API Limit/Error: {e}. Menggunakan fallback data asli.")
        return {
            "click_title": title,
            "ai_summary": original_summary,
            "tldr": ["Baca selengkapnya di sumber asli."]
        }

def run_scraper():
    # 1. Jalankan pembersihan database terlebih dahulu
    delete_old_articles(days_limit=30)
    
    MAX_ARTICLES_PER_CATEGORY = 3 
    
    for category, urls in RSS_FEEDS.items():
        print(f"--- Memproses Kategori: {category} ---")
        processed_count = 0
        
        for url in urls:
            if processed_count >= MAX_ARTICLES_PER_CATEGORY:
                break
                
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                if processed_count >= MAX_ARTICLES_PER_CATEGORY:
                    break
                    
                source_url = entry.link
                
                # Cek duplikasi URL sumber untuk mencegah error duplicate content
                check_existing = supabase.table("articles").select("id").eq("source_url", source_url).execute()
                if check_existing.data:
                    print(f"[Skip] Artikel sudah ada: {source_url}")
                    continue
                
                raw_title = entry.title
                raw_summary = getattr(entry, 'summary', raw_title)
                
                # Ekstraksi Gambar
                image_url = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=600"
                if 'media_content' in entry:
                    image_url = entry.media_content[0]['url']
                elif 'enclosures' in entry and len(entry.enclosures) > 0:
                    image_url = entry.enclosures[0].href
                
                # AI Rewrite via Groq
                ai_data = process_with_groq(raw_title, raw_summary)
                time.sleep(2)
                
                payload = {
                    "title": ai_data.get("click_title", raw_title),
                    "slug": f"{generate_slug(ai_data.get('click_title', raw_title))}-{int(time.time())}",
                    "summary": ai_data.get("ai_summary", raw_summary),
                    "tldr": ai_data.get("tldr", []),
                    "content": raw_summary,
                    "source_url": source_url, # Diset UNIQUE di database
                    "image_url": image_url,
                    "category": category
                }
                
                try:
                    supabase.table("articles").insert(payload).execute()
                    print(f"[Success] Tersimpan: {payload['title']}")
                    processed_count += 1
                except Exception as err:
                    print(f"[Error DB] {err}")

if __name__ == "__main__":
    run_scraper()
