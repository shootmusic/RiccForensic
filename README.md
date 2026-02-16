cat > README.md << 'EOF'
# RICC FORENSIC v1.0

    ____  _      __                     ____                      _            __
   / __ \(_)____/ /__________ ______   / __/_________ _____ ___  (_)________ _/ /
  / /_/ / / ___/ __/ ___/ __ `/ ___/  / /_/ ___/ __ `/ __ `__ \/ / ___/ __ `/ / 
 / _, _/ / /__/ /_/ /  / /_/ / /     / __/ /  / /_/ / / / / / / / /__/ /_/ / /  
/_/ |_/_/\___/\__/_/   \__,_/_/     /_/ /_/   \__,_/_/ /_/ /_/_/\___/\__,_/_/   
                                                                                

**Face-to-Identity Intelligence Suite**

Tool investigasi digital untuk melacak identitas dari foto target. 
Mencari akun sosial media, analisis geolokasi, ekstrak kontak, 
deteksi manipulasi foto, dan generate laporan lengkap.

Repository: https://github.com/shootmusic/RiccForensic

---

## MODEL DOWNLOAD

Model AI (InsightFace) **auto-download** saat pertama kali tool dijalankan.
- Ukuran: ~300MB
- Lokasi: `models/antelopev2/`

**Manual download (jika auto gagal):**
```bash
cd models
wget https://github.com/deepinsight/insightface/releases/download/v0.7/antelopev2.zip
unzip antelopev2.zip
rm antelopev2.zip
cd ..

FITUR
Table
Copy
Modul	Fungsi
Face Engine	Deteksi & recognition wajah
Reverse Search	Pencarian multi-platform (Yandex/Google/Bing)
Profile Scraper	Ekstrak data IG/Twitter/TikTok/FB
Geolocation	Tracking pola lokasi dari post
Contact Extract	Email, telepon, messenger
Enhancement	Perjelas foto blur/low-res
Deepfake Detect	Deteksi foto palsu/manipulasi
Report Generator	Laporan Text/JSON/HTML


INSTALASI
LINUX (Kali/Ubuntu/Debian)
bash
Copy

# 1. Clone repository
git clone https://github.com/shootmusic/RiccForensic.git

# 2. Masuk direktori
cd RiccForensic

# 3. Jalankan installer
python3 install.py

# 4. Jalankan tool (model auto-download ~300MB saat pertama kali)
./run target.jpg              # Mode CLI
./gui                         # Mode GUI

Dependensi manual (jika auto-install gagal):
bash
Copy

sudo apt-get update
sudo apt-get install -y tesseract-ocr libtesseract-dev exiftool libgl1-mesa-glx

WINDOWS (10/11)
powershell
Copy

# 1. Clone repository (PowerShell/CMD)
git clone https://github.com/shootmusic/RiccForensic.git

# 2. Masuk direktori
cd RiccForensic

# 3. Jalankan installer
python install.py

# 4. Jalankan tool (model auto-download ~300MB saat pertama kali)
run.bat target.jpg            # Mode CLI
gui.bat                       # Mode GUI

Dependensi manual Windows:

    Download & install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
    Add Tesseract ke PATH saat instalasi
    Download ExifTool: https://exiftool.org/exiftool-12.70.zip
    Extract ke folder bin/ dalam project

PENGGUNAAN
Mode CLI
bash
Copy

# Investigasi lengkap (model auto-download di background)
./run target.jpg

# Simpan report
./run target.jpg -o hasil.txt

# Format JSON
./run target.jpg -f json -o data.json

# Enhance foto dulu
./run target.jpg --enhance

# Cek keaslian foto
./run target.jpg --check-fake

# Mode cepat (tanpa deep scrape)
./run target.jpg --fast

# Bandingkan 2 wajah
./run target.jpg --compare referensi.jpg

Mode GUI
bash
Copy

./gui

TROUBLESHOOTING
"No space left on device" saat install
Model (~300MB) akan auto-download saat pertama kali ./run, bukan saat install.
"Model not found" / download gagal
Download manual:
bash
Copy

cd models
wget https://github.com/deepinsight/insightface/releases/download/v0.7/antelopev2.zip
unzip antelopev2.zip && rm antelopev2.zip

ModuleNotFoundError
bash
Copy

source venv/bin/activate
pip install -r requirements.txt

REQUIREMENTS

    OS: Linux (Kali/Ubuntu/Debian) atau Windows 10/11
    Python: 3.8+
    RAM: 4GB minimum, 8GB direkomendasikan
    Storage: 2GB (untuk models + venv)
    Network: Internet untuk search & model download

KREDIT
RICC FORENSIC v1.0
Repository: https://github.com/shootmusic/RiccForensic
Developed by RICC



