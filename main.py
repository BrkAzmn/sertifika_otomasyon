import os
import base64
import pickle
import sqlite3
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from unidecode import unidecode  # Türkçe karakterleri dönüştürmek için

# 📌 Gmail API'ye bağlanma fonksiyonu
def create_service():
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    creds = None
    if os.path.exists('token.json'):
        with open('token.json', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('gmail', 'v1', credentials=creds)
    return service

# 📌 Veritabanında en yüksek doğrulama kodunu kontrol eden fonksiyon
def generate_verification_code():
    conn = sqlite3.connect("sertifika.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(CAST(SUBSTR(dogrulama_kodu, 6) AS INTEGER)) FROM sertifikalar WHERE dogrulama_kodu LIKE 'VEGA-%'")
    last_code = cursor.fetchone()[0]

    if last_code is None:
        new_code = 0
    else:
        new_code = last_code + 1

    verification_code = f"VEGA-{new_code:05d}"
    conn.close()
    return verification_code

# 📌 İsim ortalama fonksiyonu
def adjust_name_position(name, base_y, font, img_width):
    text_width = font.getlength(name)
    new_x = (img_width - text_width) // 2
    return (new_x, base_y)

# 📌 Sertifika oluşturma fonksiyonu
def create_certificate(row, template_path):
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    img_width, _ = img.size  

    try:
        font_large = ImageFont.truetype("arial.ttf", 100)
        font_medium = ImageFont.truetype("arial.ttf", 40)
        font_small = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font_large = font_medium = font_small = ImageFont.load_default()

    # 📌 Sütunları güvenli şekilde okuma
    ad = str(row.get('Ad', '')).strip()
    soyad = str(row.get('Soyad', '')).strip()
    egitim_adi = str(row.get('Eğitim Adı', 'Bilinmiyor')).strip()
    egitim_tarihi = row.get('Eğitim Tarihi', '')

    # 📌 Tarih formatını "gün.ay.yıl" olarak değiştir
    if isinstance(egitim_tarihi, pd.Timestamp):
        egitim_tarihi = egitim_tarihi.strftime("%d.%m.%Y")  # 🔥 Güncellenmiş format
    else:
        egitim_tarihi = str(egitim_tarihi).strip()

    # 📌 Eğer ad veya soyad boşsa hata verdirme, "Bilinmiyor" olarak ata
    if not ad:
        ad = "Bilinmiyor"
    if not soyad:
        soyad = "Bilinmiyor"

    # 📌 Doğrulama kodu üret
    verification_code = generate_verification_code()

    # 📌 Dosya ismi için güvenli format
    safe_name = unidecode(f"{ad} {soyad}").replace(" ", "_")
    course_folder = unidecode(f"{egitim_adi} {egitim_tarihi}").replace(" ", "_")
    os.makedirs(course_folder, exist_ok=True)
    certificate_path = os.path.join(course_folder, f"{safe_name}_sertifika.png")

    base_name_y = 625
    name_pos = adjust_name_position(f"{ad} {soyad}", base_name_y, font_large, img_width)
    course_pos = (450, 878)
    date_pos = (140, 1000)
    code_pos = (620, 1000)

    draw.text(name_pos, f"{ad} {soyad}", font=font_large, fill="black")
    draw.text(course_pos, egitim_adi, font=font_medium, fill="black")  
    draw.text(date_pos, egitim_tarihi, font=font_small, fill="black")
    draw.text(code_pos, verification_code, font=font_small, fill="black")

    img.save(certificate_path, "PNG")

    # 📌 Veritabanına ekleme (boş değerler kontrol edildi)
    conn = sqlite3.connect("sertifika.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sertifikalar (ad, soyad, egitim_adi, egitim_tarihi, dogrulama_kodu, sertifika_yolu)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (ad, soyad, egitim_adi, egitim_tarihi, verification_code, certificate_path))
    conn.commit()
    conn.close()
    
    return certificate_path, verification_code

# 📌 E-posta gönderme fonksiyonu
def send_email(service, to, subject, body, attachment):
    try:
        message = MIMEMultipart()
        message['To'] = to
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        with open(attachment, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment)}"')
            message.attach(part)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        print(f"✅ E-posta başarıyla gönderildi: {to}")

    except Exception as e:
        print(f"❌ E-posta gönderme hatası: {e}")

# 📌 Ana fonksiyon
def main():
    # 📌 Excel dosyasını oku, boş satırları ve gereksiz boşlukları temizle
    df = pd.read_excel("katilimcilar.xlsx")
    df = df.dropna(how="all")  # Tamamen boş satırları kaldır
    df.columns = df.columns.str.strip()  # Başlıklardaki boşlukları kaldır

    # 📌 Sütunların doğru isimlendirildiğini kontrol et
    expected_columns = {"Ad", "Soyad", "E-posta Adresi", "Eğitim Adı", "Eğitim Tarihi"}
    missing_columns = expected_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"❌ Excel dosyasında eksik sütunlar var: {missing_columns}")

    service = create_service()
    template_path = "image.png"

    for index, row in df.iterrows():
        certificate_path, verification_code = create_certificate(row, template_path)
        
        subject = f"{row['Ad']} {row['Soyad']} - {row['Eğitim Adı']} Sertifikası"
        body = f"Sayın {row['Ad']},\n\n{row['Eğitim Adı']} sertifikanız ektedir.\n\nSertifika doğrulama kodunuz: {verification_code}.\n\nSaygılarımızla,\nVakıf Katılım Eğitim ve Gelişim Akademisi"
        
        send_email(service, row['E-posta Adresi'], subject, body, certificate_path)
        print(f"✅ Sertifika gönderildi: {row['Ad']} {row['Soyad']} - Doğrulama Kodu: {verification_code}")

if __name__ == "__main__":
    main()
