from flask import Flask, render_template, request, send_file
import sqlite3

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    certificate_info = None
    error_message = None

    if request.method == "POST":
        code = request.form["verification_code"]
        conn = sqlite3.connect("sertifika.db")
        cursor = conn.cursor()
        cursor.execute("SELECT ad, soyad, egitim_adi, sertifika_yolu FROM sertifikalar WHERE dogrulama_kodu = ?", (code,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            certificate_info = {
                "ad": result[0],
                "soyad": result[1],
                "egitim_adi": result[2],
                "sertifika_yolu": result[3]
            }
        else:
            error_message = "❌ Böyle bir doğrulama kodlu sertifika bulunamadı. Lütfen sertifikanızda yazan doğrulama kodunu eksiksiz girin."

    return render_template("index.html", certificate_info=certificate_info, error_message=error_message)

@app.route("/download")
def download():
    path = request.args.get("path")
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
