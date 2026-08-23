from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from accounts.decorators import role_required
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from datetime import datetime

from .models import (
    Mobil,
    Penyewaan,
    Pengembalian,
    Pembayaran,
    CustomUser,
    Pengaturan
)


@role_required('administrator')
def dashboard(request):
    total_mobil = Mobil.objects.count()
    mobil_tersedia = Mobil.objects.filter(tersedia=True).count()

    total_penyewaan = Penyewaan.objects.count()
    penyewaan_diajukan = Penyewaan.objects.filter(status='diajukan').count()
    penyewaan_disetujui = Penyewaan.objects.filter(status='disetujui').count()
    penyewaan_selesai = Penyewaan.objects.filter(status='selesai').count()

    total_pelanggan = CustomUser.objects.filter(role='pelanggan').count()

    total_pembayaran = Pembayaran.objects.count()
    pembayaran_lunas = Pembayaran.objects.filter(status='lunas').count()
    pembayaran_menunggu = Pembayaran.objects.filter(status='menunggu').count()

    # Efisien: gunakan aggregate bukan Python loop
    from django.db.models import Sum
    hasil = Pembayaran.objects.filter(status='lunas').aggregate(total=Sum('jumlah'))
    total_pendapatan = hasil['total'] or Decimal('0')

    # Ambil foto hero background untuk ditampilkan di dashboard
    setting_hero, _ = Pengaturan.objects.get_or_create(kunci='hero_background')

    # Cek apakah ada notifikasi foto baru yang baru diubah (dari session)
    foto_baru_diubah = request.session.pop('foto_hero_diubah', False)
    foto_diubah_oleh = request.session.pop('foto_hero_diubah_oleh', '')

    context = {
        'total_mobil': total_mobil,
        'mobil_tersedia': mobil_tersedia,
        'total_penyewaan': total_penyewaan,
        'penyewaan_diajukan': penyewaan_diajukan,
        'penyewaan_disetujui': penyewaan_disetujui,
        'penyewaan_selesai': penyewaan_selesai,
        'total_pelanggan': total_pelanggan,
        'total_pembayaran': total_pembayaran,
        'pembayaran_lunas': pembayaran_lunas,
        'pembayaran_menunggu': pembayaran_menunggu,
        'pembayaran_baru': pembayaran_menunggu,
        'penyewaan_baru': penyewaan_diajukan,
        'total_pendapatan': total_pendapatan,
        'setting_hero': setting_hero,
        'foto_baru_diubah': foto_baru_diubah,
        'foto_diubah_oleh': foto_diubah_oleh,
    }

    return render(request, 'administrator/dashboard.html', context)


@role_required('administrator')
def redirect_user(request):
    if request.user.role == 'administrator':
        return redirect('/administrator/')
    elif request.user.role == 'pelanggan':
        return redirect('/pelanggan/')

    return redirect('/admin/')


# ===========================
# LAPORAN
# ===========================

@role_required('administrator')
def laporan_penyewaan(request):
    penyewaans = Penyewaan.objects.all().order_by('-tanggal_sewa')

    return render(
        request,
        'administrator/laporan_penyewaan.html',
        {
            'penyewaans': penyewaans
        }
    )


# ===========================
# DATA MOBIL
# ===========================

@role_required('administrator')
def data_mobil(request):
    mobils = Mobil.objects.all().order_by('nama_mobil')

    return render(
        request,
        'administrator/data_mobil.html',
        {
            'mobils': mobils
        }
    )


@role_required('administrator')
def tambah_mobil(request):

    if request.method == "POST":
        # Bug #4 FIX: validasi input harga sebelum menyimpan
        nama_mobil = request.POST.get('nama_mobil', '').strip()
        merk = request.POST.get('merk', '').strip()
        nomor_polisi = request.POST.get('nomor_polisi', '').strip()
        harga_harian_raw = request.POST.get('harga_harian', '').strip()
        harga_mingguan_raw = request.POST.get('harga_mingguan', '').strip()
        harga_bulanan_raw = request.POST.get('harga_bulanan', '').strip()
        foto = request.FILES.get('foto')

        if not nama_mobil or not merk or not nomor_polisi:
            messages.error(request, 'Nama mobil, merk, dan nomor polisi wajib diisi.')
            return render(request, 'administrator/tambah_mobil.html')

        try:
            harga_harian = Decimal(harga_harian_raw)
            harga_mingguan = Decimal(harga_mingguan_raw)
            harga_bulanan = Decimal(harga_bulanan_raw)
            if harga_harian <= 0 or harga_mingguan <= 0 or harga_bulanan <= 0:
                raise ValueError("Harga harus lebih dari 0.")
        except (InvalidOperation, ValueError):
            messages.error(request, 'Format harga tidak valid. Masukkan angka yang benar.')
            return render(request, 'administrator/tambah_mobil.html')

        try:
            Mobil.objects.create(
                nama_mobil=nama_mobil,
                merk=merk,
                nomor_polisi=nomor_polisi,
                harga_harian=harga_harian,
                harga_mingguan=harga_mingguan,
                harga_bulanan=harga_bulanan,
                foto=foto,
                tersedia=True
            )
            messages.success(request, 'Mobil berhasil ditambahkan.')
            return redirect('data_mobil')
        except IntegrityError:
            messages.error(request, 'Nomor polisi sudah terdaftar.')
            return render(request, 'administrator/tambah_mobil.html')

    return render(request, 'administrator/tambah_mobil.html')


@role_required('administrator')
def edit_mobil(request, id):
    # Bug #5 FIX: gunakan get_object_or_404 agar mengembalikan 404, bukan 500
    mobil = get_object_or_404(Mobil, id=id)

    if request.method == "POST":
        nama_mobil = request.POST.get('nama_mobil', '').strip()
        merk = request.POST.get('merk', '').strip()
        nomor_polisi = request.POST.get('nomor_polisi', '').strip()
        harga_harian_raw = request.POST.get('harga_harian', '').strip()
        harga_mingguan_raw = request.POST.get('harga_mingguan', '').strip()
        harga_bulanan_raw = request.POST.get('harga_bulanan', '').strip()

        if not nama_mobil or not merk or not nomor_polisi:
            messages.error(request, 'Nama mobil, merk, dan nomor polisi wajib diisi.')
            return render(request, 'administrator/edit_mobil.html', {'mobil': mobil})

        try:
            harga_harian = Decimal(harga_harian_raw)
            harga_mingguan = Decimal(harga_mingguan_raw)
            harga_bulanan = Decimal(harga_bulanan_raw)
            if harga_harian <= 0 or harga_mingguan <= 0 or harga_bulanan <= 0:
                raise ValueError("Harga harus lebih dari 0.")
        except (InvalidOperation, ValueError):
            messages.error(request, 'Format harga tidak valid. Masukkan angka yang benar.')
            return render(request, 'administrator/edit_mobil.html', {'mobil': mobil})

        mobil.nama_mobil = nama_mobil
        mobil.merk = merk
        mobil.nomor_polisi = nomor_polisi
        mobil.harga_harian = harga_harian
        mobil.harga_mingguan = harga_mingguan
        mobil.harga_bulanan = harga_bulanan

        if request.FILES.get('foto'):
            mobil.foto = request.FILES['foto']

        try:
            mobil.save()
            messages.success(request, 'Data mobil berhasil diperbarui.')
            return redirect('data_mobil')
        except IntegrityError:
            messages.error(request, 'Nomor polisi sudah digunakan mobil lain.')
            return render(request, 'administrator/edit_mobil.html', {'mobil': mobil})

    return render(
        request,
        'administrator/edit_mobil.html',
        {
            'mobil': mobil
        }
    )


@role_required('administrator')
def hapus_mobil(request, id):

    if request.method != 'POST':
        return redirect('data_mobil')

    # Bug #5 FIX: get_object_or_404
    mobil = get_object_or_404(Mobil, id=id)
    mobil.delete()
    messages.success(request, 'Mobil berhasil dihapus.')
    return redirect('data_mobil')


# ===========================
# PENYEWAAN
# ===========================

@role_required('administrator')
def data_penyewaan(request):

    penyewaans = Penyewaan.objects.all().order_by('-tanggal_sewa')

    return render(
        request,
        'administrator/data_penyewaan.html',
        {
            'penyewaans': penyewaans
        }
    )


@role_required('administrator')
def setujui_penyewaan(request, id):

    if request.method != 'POST':
        return redirect('data_penyewaan')

    penyewaan = get_object_or_404(Penyewaan, id=id)

    # Pastikan pembayaran sudah lunas
    if not hasattr(penyewaan, 'pembayaran') or penyewaan.pembayaran.status != 'lunas':
        messages.error(
            request,
            'Penyewaan belum dapat disetujui. Tandai pembayaran sebagai Lunas terlebih dahulu.'
        )
        return redirect('data_penyewaan')

    # Bug #1 FIX: Hapus get_or_create duplikat — pembayaran sudah dibuat saat checkout pelanggan
    penyewaan.setujui()
    messages.success(request, 'Penyewaan berhasil disetujui.')

    return redirect('data_penyewaan')


@role_required('administrator')
def tolak_penyewaan(request, id):

    if request.method != 'POST':
        return redirect('data_penyewaan')

    penyewaan = get_object_or_404(Penyewaan, id=id)

    if penyewaan.status not in ('diajukan',):
        messages.error(request, 'Hanya penyewaan yang berstatus "Diajukan" yang dapat ditolak.')
        return redirect('data_penyewaan')

    penyewaan.status = 'ditolak'
    penyewaan.save()
    messages.success(request, 'Penyewaan berhasil ditolak.')
    return redirect('data_penyewaan')


@role_required('administrator')
def selesai_penyewaan(request, id):

    if request.method != 'POST':
        return redirect('data_penyewaan')

    penyewaan = get_object_or_404(Penyewaan, id=id)

    # Bug #2 FIX: hanya izinkan jika status 'disetujui'
    if penyewaan.status != 'disetujui':
        messages.error(
            request,
            'Hanya penyewaan yang berstatus "Disetujui" yang dapat diselesaikan.'
        )
        return redirect('data_penyewaan')

    penyewaan.selesai()
    messages.success(request, 'Penyewaan berhasil diselesaikan.')
    return redirect('data_penyewaan')


@role_required('administrator')
def hapus_penyewaan(request, id):
    if request.method != 'POST':
        return redirect('data_penyewaan')
    penyewaan = get_object_or_404(Penyewaan, id=id)
    mobil = penyewaan.mobil
    penyewaan.delete()
    if not Penyewaan.objects.filter(
        mobil=mobil,
        status__in=['diajukan', 'disetujui'],
    ).exists():
        mobil.tersedia = True
        mobil.save(update_fields=['tersedia'])
    messages.success(request, 'Penyewaan berhasil dihapus.')
    return redirect('data_penyewaan')


# ===========================
# PENGEMBALIAN
# ===========================

@role_required('administrator')
def data_pengembalian(request):

    pengembalians = Pengembalian.objects.all().order_by('-tanggal_pengembalian')

    return render(
        request,
        'administrator/data_pengembalian.html',
        {
            'pengembalians': pengembalians
        }
    )


@role_required('administrator')
def tambah_pengembalian(request, id):

    penyewaan = get_object_or_404(Penyewaan, id=id)

    # Satu penyewaan hanya boleh memiliki satu data pengembalian.
    if Pengembalian.objects.filter(penyewaan=penyewaan).exists():
        messages.warning(request, 'Pengembalian untuk penyewaan ini sudah tersimpan.')
        return redirect('data_pengembalian')

    if request.method == "POST":

        # Bug #3 FIX: validasi tanggal dan denda sebelum menyimpan
        tanggal_pengembalian_raw = request.POST.get('tanggal_pengembalian', '').strip()
        kondisi_mobil = request.POST.get('kondisi_mobil', '').strip()
        denda_raw = request.POST.get('denda', '0').strip()

        if not kondisi_mobil:
            messages.error(request, 'Kondisi mobil wajib diisi.')
            hari_ini = timezone.now().date()
            return render(request, 'administrator/tambah_pengembalian.html', {
                'penyewaan': penyewaan,
                'hari_ini': hari_ini.strftime('%Y-%m-%d'),
                'estimasi_denda': 0,
            })

        try:
            tgl_pengembalian = datetime.strptime(tanggal_pengembalian_raw, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, 'Format tanggal pengembalian tidak valid.')
            hari_ini = timezone.now().date()
            return render(request, 'administrator/tambah_pengembalian.html', {
                'penyewaan': penyewaan,
                'hari_ini': hari_ini.strftime('%Y-%m-%d'),
                'estimasi_denda': 0,
            })

        if tgl_pengembalian < penyewaan.tanggal_sewa:
            messages.error(request, 'Tanggal pengembalian tidak boleh sebelum tanggal sewa.')
            hari_ini = timezone.now().date()
            return render(request, 'administrator/tambah_pengembalian.html', {
                'penyewaan': penyewaan,
                'hari_ini': hari_ini.strftime('%Y-%m-%d'),
                'estimasi_denda': 0,
            })

        try:
            denda = Decimal(denda_raw) if denda_raw else Decimal('0')
            if denda < 0:
                raise ValueError("Denda tidak boleh negatif.")
        except (InvalidOperation, ValueError):
            messages.error(request, 'Format denda tidak valid. Masukkan angka yang benar.')
            hari_ini = timezone.now().date()
            return render(request, 'administrator/tambah_pengembalian.html', {
                'penyewaan': penyewaan,
                'hari_ini': hari_ini.strftime('%Y-%m-%d'),
                'estimasi_denda': 0,
            })

        try:
            Pengembalian.objects.create(
                penyewaan=penyewaan,
                tanggal_pengembalian=tgl_pengembalian,
                kondisi_mobil=kondisi_mobil,
                denda=denda,
                selesai=True
            )
        except IntegrityError:
            messages.warning(request, 'Pengembalian untuk penyewaan ini sudah tersimpan.')
            return redirect('data_pengembalian')

        penyewaan.selesai()
        messages.success(request, 'Pengembalian berhasil disimpan.')
        return redirect('data_pengembalian')

    hari_ini = timezone.now().date()
    estimasi_denda = 0
    if hari_ini > penyewaan.tanggal_kembali:
        terlambat_hari = (hari_ini - penyewaan.tanggal_kembali).days
        estimasi_denda = int(terlambat_hari * penyewaan.mobil.harga_harian)

    return render(
        request,
        'administrator/tambah_pengembalian.html',
        {
            'penyewaan': penyewaan,
            'hari_ini': hari_ini.strftime('%Y-%m-%d'),
            'estimasi_denda': estimasi_denda
        }
    )


@role_required('administrator')
def hapus_pengembalian(request, id):
    if request.method != 'POST':
        return redirect('data_pengembalian')
    pengembalian = get_object_or_404(Pengembalian, id=id)
    pengembalian.delete()
    messages.success(request, 'Data pengembalian berhasil dihapus.')
    return redirect('data_pengembalian')


# ===========================
# PEMBAYARAN
# ===========================

@role_required('administrator')
def data_pembayaran(request):

    pembayarans = Pembayaran.objects.all().order_by('-id')

    return render(
        request,
        'administrator/data_pembayaran.html',
        {
            'pembayarans': pembayarans
        }
    )


@role_required('administrator')
def lunas_pembayaran(request, id):

    if request.method != 'POST':
        return redirect('data_pembayaran')

    pembayaran = get_object_or_404(Pembayaran, id=id)

    pembayaran.status = 'lunas'
    pembayaran.tanggal_bayar = timezone.now()
    pembayaran.save()
    messages.success(request, 'Pembayaran berhasil ditandai lunas.')
    return redirect('data_pembayaran')


@role_required('administrator')
def hapus_pembayaran(request, id):
    if request.method != 'POST':
        return redirect('data_pembayaran')
    pembayaran = get_object_or_404(Pembayaran, id=id)
    pembayaran.delete()
    messages.success(request, 'Data pembayaran berhasil dihapus.')
    return redirect('data_pembayaran')


# ===========================
# PELANGGAN
# ===========================

@role_required('administrator')
def data_pelanggan(request):

    pelanggans = CustomUser.objects.filter(role='pelanggan')

    return render(
        request,
        'administrator/data_pelanggan.html',
        {
            'pelanggans': pelanggans
        }
    )


@role_required('administrator')
def verifikasi_pelanggan(request, id):

    if request.method != 'POST':
        return redirect('data_pelanggan')

    pelanggan = get_object_or_404(CustomUser, id=id)

    pelanggan.is_verified = True
    pelanggan.save()
    messages.success(request, 'Pelanggan berhasil diverifikasi.')
    return redirect('data_pelanggan')


@role_required('administrator')
def hapus_pelanggan(request, id):
    if request.method != 'POST':
        return redirect('data_pelanggan')
    pelanggan = get_object_or_404(CustomUser, id=id, role='pelanggan')
    pelanggan.delete()
    messages.success(request, 'Data pelanggan berhasil dihapus.')
    return redirect('data_pelanggan')


@role_required('administrator')
def edit_pelanggan(request, id):
    pelanggan = get_object_or_404(CustomUser, id=id, role='pelanggan')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        nik = request.POST.get('nik', '').strip() or None
        no_telepon = request.POST.get('no_telepon', '').strip() or None

        if not username:
            messages.error(request, 'Username wajib diisi.')
        elif CustomUser.objects.filter(username=username).exclude(id=id).exists():
            messages.error(request, 'Username sudah digunakan pelanggan lain.')
        elif nik and CustomUser.objects.filter(nik=nik).exclude(id=id).exists():
            messages.error(request, 'NIK sudah digunakan pelanggan lain.')
        else:
            pelanggan.username = username
            pelanggan.email = email
            pelanggan.first_name = first_name
            pelanggan.last_name = last_name
            pelanggan.nik = nik
            pelanggan.no_telepon = no_telepon
            pelanggan.save()
            messages.success(request, 'Data pelanggan berhasil diperbarui.')
            return redirect('data_pelanggan')

    return render(request, 'administrator/edit_pelanggan.html', {'pelanggan': pelanggan})

# ===========================
# ===========================
# ADMINISTRATOR
# ===========================

@role_required('administrator')
def data_petugas(request):
    petugas_list = CustomUser.objects.filter(role='administrator').order_by('username')
    return render(request, 'administrator/data_petugas.html', {'petugas_list': petugas_list})


@role_required('administrator')
def tambah_petugas(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        nik = request.POST.get('nik', '').strip() or None
        no_telepon = request.POST.get('no_telepon', '').strip() or None
        role = 'administrator'

        if not username or not password:
            messages.error(request, 'Username dan password wajib diisi.')
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan.')
        elif nik and CustomUser.objects.filter(nik=nik).exists():
            messages.error(request, 'NIK sudah digunakan.')
        else:
            user = CustomUser.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                nik=nik,
                no_telepon=no_telepon,
                role=role,
                is_staff=True,
                is_superuser=True
            )
            user.set_password(password)
            user.save()
            messages.success(request, 'Data Administrator berhasil ditambahkan.')
            return redirect('data_petugas')

    return render(request, 'administrator/tambah_petugas.html')


@role_required('administrator')
def edit_petugas(request, id):
    petugas = get_object_or_404(CustomUser, id=id, role='administrator')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        nik = request.POST.get('nik', '').strip() or None
        no_telepon = request.POST.get('no_telepon', '').strip() or None

        if not username:
            messages.error(request, 'Username wajib diisi.')
        elif CustomUser.objects.filter(username=username).exclude(id=id).exists():
            messages.error(request, 'Username sudah digunakan oleh pengguna lain.')
        elif nik and CustomUser.objects.filter(nik=nik).exclude(id=id).exists():
            messages.error(request, 'NIK sudah digunakan oleh pengguna lain.')
        else:
            petugas.username = username
            petugas.email = email
            petugas.first_name = first_name
            petugas.last_name = last_name
            petugas.nik = nik
            petugas.no_telepon = no_telepon
            if password:
                petugas.set_password(password)
            petugas.save()
            messages.success(request, 'Data administrator berhasil diperbarui.')
            return redirect('data_petugas')

    return render(request, 'administrator/edit_petugas.html', {'petugas': petugas})


@role_required('administrator')
def hapus_petugas(request, id):
    if request.method != 'POST':
        return redirect('data_petugas')
    petugas = get_object_or_404(CustomUser, id=id, role='administrator')
    if petugas.id == request.user.id:
        messages.error(request, 'Anda tidak dapat menghapus akun Anda sendiri.')
        return redirect('data_petugas')
    petugas.delete()
    messages.success(request, 'Data administrator berhasil dihapus.')
    return redirect('data_petugas')


@role_required('administrator')
def ubah_role_petugas(request, id):
    return redirect('data_petugas')


@role_required('administrator')
def pengaturan(request):
    setting, created = Pengaturan.objects.get_or_create(kunci='hero_background')
    setting_katalog, _ = Pengaturan.objects.get_or_create(kunci='katalog_background')
    setting_logo, _ = Pengaturan.objects.get_or_create(kunci='logo_toko')
    setting_favicon, _ = Pengaturan.objects.get_or_create(kunci='favicon')
    
    if request.method == "POST":
        foto = request.FILES.get('hero_background')
        if foto:
            setting.nilai_gambar = foto
            setting.save()
            request.session['foto_hero_diubah'] = True
            request.session['foto_hero_diubah_oleh'] = request.user.username
            messages.success(request, 'Gambar latar belakang Hero berhasil diperbarui.')
            
        foto_katalog = request.FILES.get('katalog_background')
        if foto_katalog:
            setting_katalog.nilai_gambar = foto_katalog
            setting_katalog.save()
            messages.success(request, 'Gambar latar belakang Katalog berhasil diperbarui.')
            
        foto_logo = request.FILES.get('logo_toko')
        if foto_logo:
            setting_logo.nilai_gambar = foto_logo
            setting_logo.save()
            messages.success(request, 'Logo Toko berhasil diperbarui.')
            
        foto_favicon = request.FILES.get('favicon')
        if foto_favicon:
            setting_favicon.nilai_gambar = foto_favicon
            setting_favicon.save()
            messages.success(request, 'Favicon berhasil diperbarui.')
            
        if not foto and not foto_katalog and not foto_logo and not foto_favicon:
            messages.warning(request, 'Pilih gambar terlebih dahulu sebelum menyimpan.')
        return redirect('pengaturan')

    return render(request, 'administrator/pengaturan.html', {
        'setting': setting,
        'setting_katalog': setting_katalog,
        'setting_logo': setting_logo,
        'setting_favicon': setting_favicon
    })

