import os
import django
from PIL import Image, ImageDraw, ImageFont
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rentcar.settings")
django.setup()

from administrator.models import Mobil

def generate_car_image(nama_mobil, filename):
    # Buat direktori jika belum ada
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Warna acak untuk background mobil
    colors = [(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))]
    bg_color = random.choice(colors)
    
    img = Image.new('RGB', (800, 600), color=bg_color)
    d = ImageDraw.Draw(img)
    
    # Tambahkan teks sederhana
    d.text((50, 250), nama_mobil, fill=(255, 255, 255))
    
    img.save(filename)
    return filename

mobil_data = [
    {"nama_mobil": "Toyota Avanza", "merk": "Toyota", "nomor_polisi": "B 1234 ABC", "harga": 300000},
    {"nama_mobil": "Honda Brio", "merk": "Honda", "nomor_polisi": "B 2345 CDE", "harga": 250000},
    {"nama_mobil": "Mitsubishi Xpander", "merk": "Mitsubishi", "nomor_polisi": "B 3456 DEF", "harga": 350000},
    {"nama_mobil": "Suzuki Ertiga", "merk": "Suzuki", "nomor_polisi": "B 4567 EFG", "harga": 300000},
    {"nama_mobil": "Toyota Innova Zenix", "merk": "Toyota", "nomor_polisi": "B 5678 FGH", "harga": 600000},
    {"nama_mobil": "Honda HR-V", "merk": "Honda", "nomor_polisi": "B 6789 GHI", "harga": 450000},
    {"nama_mobil": "Daihatsu Xenia", "merk": "Daihatsu", "nomor_polisi": "B 7890 HIJ", "harga": 300000},
    {"nama_mobil": "Toyota Fortuner", "merk": "Toyota", "nomor_polisi": "B 8901 IJK", "harga": 800000},
    {"nama_mobil": "Mitsubishi Pajero", "merk": "Mitsubishi", "nomor_polisi": "B 9012 JKL", "harga": 800000},
    {"nama_mobil": "Honda CR-V", "merk": "Honda", "nomor_polisi": "B 0123 KLM", "harga": 700000},
]

for data in mobil_data:
    # Slugify untuk nama file
    slug = data['nama_mobil'].lower().replace(' ', '_')
    rel_path = f"mobil/{slug}.jpg"
    abs_path = os.path.join("media", rel_path)
    
    # Hasilkan gambar
    generate_car_image(data['nama_mobil'], abs_path)
    
    # Hapus jika sudah ada (agar tidak duplicate saat di-run ulang)
    if Mobil.objects.filter(nomor_polisi=data['nomor_polisi']).exists():
        Mobil.objects.filter(nomor_polisi=data['nomor_polisi']).delete()
        
    mobil = Mobil.objects.create(
        nama_mobil=data['nama_mobil'],
        merk=data['merk'],
        nomor_polisi=data['nomor_polisi'],
        harga_harian=data['harga'],
        harga_mingguan=data['harga'] * 6, # Diskon mingguan
        harga_bulanan=data['harga'] * 20, # Diskon bulanan
        foto=rel_path,
        tersedia=True
    )
    print(f"Berhasil menambahkan: {mobil.nama_mobil} dengan foto {rel_path}")

print("10 Data Mobil dummy beserta foto berhasil dibuat!")
