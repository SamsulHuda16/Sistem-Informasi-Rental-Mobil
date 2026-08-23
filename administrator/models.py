from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('administrator', 'Administrator'),
        ('pelanggan', 'Pelanggan'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    nik = models.CharField(max_length=16, unique=True, null=True, blank=True)
    no_telepon = models.CharField(max_length=15, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.username} - {self.role}'
    
class Mobil(models.Model):
    nama_mobil = models.CharField(max_length=100)
    merk = models.CharField(max_length=100)
    nomor_polisi = models.CharField(max_length=20, unique=True)
    harga_harian = models.DecimalField(max_digits=12, decimal_places=2)
    harga_mingguan = models.DecimalField(max_digits=12, decimal_places=2)
    harga_bulanan = models.DecimalField(max_digits=12, decimal_places=2)
    foto = models.ImageField(upload_to='mobil/', null=True, blank=True)
    tersedia = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.nama_mobil} ({self.nomor_polisi})'

class Penyewaan(models.Model):
    STATUS_CHOICES = (
        ('diajukan', 'Diajukan'),
        ('disetujui', 'Disetujui'),
        ('ditolak', 'Ditolak'),
        # 'divalidasi' dicadangkan untuk alur validasi tambahan di masa depan
        # Saat ini belum digunakan oleh view manapun
        ('divalidasi', 'Divalidasi Administrator'),
        ('selesai', 'Selesai'),
    )

    pelanggan = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    mobil = models.ForeignKey(Mobil, on_delete=models.CASCADE)

    # Identitas pemesan tamu (tanpa akun)
    nama_tamu = models.CharField(max_length=100, null=True, blank=True)
    nik_tamu = models.CharField(max_length=16, null=True, blank=True)
    no_telepon_tamu = models.CharField(max_length=20, null=True, blank=True)
    email_tamu = models.EmailField(null=True, blank=True)

    tanggal_sewa = models.DateField()
    tanggal_kembali = models.DateField()
    lama_sewa = models.PositiveIntegerField()

    total_biaya = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    dengan_supir = models.BooleanField(default=False)
    metode_pembayaran = models.CharField(max_length=20)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='diajukan'
    )

    def __str__(self):
        if self.pelanggan and self.pelanggan.username != '__guest__':
            nama = self.pelanggan.username
        else:
            nama = self.nama_tamu or 'Tamu'
        return f"{nama} - {self.mobil.nama_mobil}"

    def setujui(self):
        self.status = 'disetujui'
        self.save()

        self.mobil.tersedia = False
        self.mobil.save()
    def selesai(self):
        self.status = 'selesai'
        self.save()

        self.mobil.tersedia = True
        self.mobil.save()

class Pengembalian(models.Model):
    penyewaan = models.OneToOneField(Penyewaan, on_delete=models.CASCADE)
    tanggal_pengembalian = models.DateField()
    kondisi_mobil = models.TextField()
    denda = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selesai = models.BooleanField(default=False)

class HistoriJabatan(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    jabatan = models.CharField(max_length=20)
    mulai = models.DateTimeField(auto_now_add=True)
    selesai = models.DateTimeField(null=True, blank=True)
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.username} - {self.jabatan}'
    
class Pembayaran(models.Model):
    STATUS_CHOICES = (
        ('menunggu', 'Menunggu'),
        ('lunas', 'Lunas'),
    )

    penyewaan = models.OneToOneField(Penyewaan, on_delete=models.CASCADE)
    jumlah = models.DecimalField(max_digits=12, decimal_places=2)
    metode = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='menunggu')
    bukti_pembayaran = models.ImageField(upload_to='bukti_pembayaran/', null=True, blank=True)
    tanggal_bayar = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Pembayaran {self.penyewaan}"    

class Pengaturan(models.Model):
    kunci = models.CharField(max_length=50, unique=True)
    nilai = models.TextField(blank=True, null=True)
    nilai_gambar = models.ImageField(upload_to='pengaturan/', blank=True, null=True)

    class Meta:
        verbose_name = "Pengaturan"
        verbose_name_plural = "Pengaturan"

    def __str__(self):
        return self.kunci    