import sqlite3

# 📌 Veritabanına bağlan
conn = sqlite3.connect("sertifika.db")
cursor = conn.cursor()

# 📌 Eğer tablo varsa, tamamen sıfırla (Bütün kayıtları sil)
cursor.execute("DROP TABLE IF EXISTS sertifikalar")

# 📌 Yeni sertifikalar tablosunu oluştur
cursor.execute('''
    CREATE TABLE sertifikalar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad TEXT NOT NULL,
        soyad TEXT NOT NULL,
        egitim_adi TEXT NOT NULL,
        egitim_tarihi TEXT,
        dogrulama_kodu TEXT UNIQUE NOT NULL,
        sertifika_yolu TEXT NOT NULL
    )
''')

# 📌 Değişiklikleri kaydet ve bağlantıyı kapat
conn.commit()
conn.close()

print("✅ Tüm eski kayıtlar silindi ve veritabanı sıfırlandı.")
print("✅ Yeni sertifikalar tablosu oluşturuldu.")
