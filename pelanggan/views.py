from django.shortcuts import render, redirect
from django.contrib import messages
from administrator.models import Mobil, Penyewaan, Pembayaran, CustomUser
from datetime import datetime
from django.utils import timezone
from decimal import Decimal
from django.db import transaction
import uuid


def _get_or_create_guest_user():
    """Ambil atau buat akun 'guest' sebagai placeholder FK untuk penyewaan tamu."""
    guest, _ = CustomUser.objects.get_or_create(
        username='__guest__',
        defaults={
            'role': 'pelanggan',
            'is_active': False,
            'is_verified': False,
            'email': 'guest@rental.local',
        }
    )
    return guest


def daftar_mobil(request):
    """Halaman katalog semua mobil — publik, tanpa login."""
    mobils = Mobil.objects.all().order_by('nama_mobil')
    jumlah_keranjang = len(request.session.get('keranjang_penyewaan', []))
    return render(request, 'pelanggan/daftar_mobil.html', {
        'mobils': mobils,
        'jumlah_keranjang': jumlah_keranjang,
    })


def sewa_mobil(request):
    """Form penyewaan mobil — publik, tanpa login."""
    mobils = Mobil.objects.filter(tersedia=True)

    if request.method == 'POST':
        mobil_id = request.POST.get('mobil')
        tanggal_sewa = request.POST.get('tanggal_sewa')
        tanggal_kembali = request.POST.get('tanggal_kembali')

        # Data identitas tamu
        nama_tamu = request.POST.get('nama_tamu', '').strip()
        nik_tamu = request.POST.get('nik_tamu', '').strip()
        no_telepon_tamu = request.POST.get('no_telepon_tamu', '').strip()
        email_tamu = request.POST.get('email_tamu', '').strip()

        if not nama_tamu or not nik_tamu:
            messages.error(request, "Nama pemesan dan NIK wajib diisi.")
            return redirect('sewa_mobil')

        try:
            mobil = Mobil.objects.get(id=mobil_id, tersedia=True)
        except Mobil.DoesNotExist:
            messages.error(request, "Mobil tidak tersedia.")
            return redirect('sewa_mobil')

        try:
            tgl_sewa = datetime.strptime(tanggal_sewa, '%Y-%m-%d')
            tgl_kembali = datetime.strptime(tanggal_kembali, '%Y-%m-%d')
        except (TypeError, ValueError):
            messages.error(request, "Tanggal penyewaan tidak valid.")
            return redirect('sewa_mobil')

        hari_ini = timezone.now().date()

        if tgl_sewa.date() < hari_ini:
            messages.error(request, "Tanggal sewa tidak boleh sebelum hari ini.")
            return redirect('sewa_mobil')

        if tgl_kembali.date() <= tgl_sewa.date():
            messages.error(request, "Tanggal kembali harus setelah tanggal sewa.")
            return redirect('sewa_mobil')

        lama_sewa = (tgl_kembali - tgl_sewa).days

        if lama_sewa <= 0:
            lama_sewa = 1

        # Perhitungan harga berjenjang (Bulanan, Mingguan, Harian)
        bulan = lama_sewa // 30
        sisa_hari = lama_sewa % 30
        minggu = sisa_hari // 7
        hari = sisa_hari % 7

        total_biaya = (
            (bulan * mobil.harga_bulanan) +
            (minggu * mobil.harga_mingguan) +
            (hari * mobil.harga_harian)
        )

        cart = request.session.get('keranjang_penyewaan', [])

        # Cek bentrok di keranjang
        for item in cart:
            if item['mobil_id'] == mobil.id and not (
                tanggal_kembali <= item['tanggal_sewa'] or tanggal_sewa >= item['tanggal_kembali']
            ):
                messages.error(request, "Mobil tersebut sudah ada pada periode yang bentrok di keranjang.")
                return redirect('keranjang_penyewaan')

        # Cek bentrok di database
        bentrok = Penyewaan.objects.filter(
            mobil=mobil,
            status__in=['diajukan', 'disetujui'],
            tanggal_sewa__lt=tgl_kembali.date(),
            tanggal_kembali__gt=tgl_sewa.date(),
        ).exists()
        if bentrok:
            messages.error(request, "Mobil sudah dipesan pada periode tersebut.")
            return redirect('sewa_mobil')

        # Simpan ke session dengan data tamu
        cart.append({
            'item_id': str(uuid.uuid4()),
            'mobil_id': mobil.id,
            'nama_mobil': mobil.nama_mobil,
            'tanggal_sewa': tanggal_sewa,
            'tanggal_kembali': tanggal_kembali,
            'lama_sewa': lama_sewa,
            'total_biaya': str(total_biaya),
            'nama_tamu': nama_tamu,
            'nik_tamu': nik_tamu,
            'no_telepon_tamu': no_telepon_tamu,
            'email_tamu': email_tamu,
        })
        request.session['keranjang_penyewaan'] = cart
        request.session.modified = True
        messages.success(request, "Mobil berhasil ditambahkan ke keranjang.")
        return redirect('keranjang_penyewaan')

    jumlah_keranjang = len(request.session.get('keranjang_penyewaan', []))
    return render(request, 'pelanggan/sewa_mobil.html', {
        'mobils': mobils,
        'jumlah_keranjang': jumlah_keranjang,
    })


def riwayat_penyewaan(request):
    """Riwayat penyewaan tamu — berdasarkan ID yang tersimpan di session."""
    penyewaan_ids = request.session.get('penyewaan_ids', [])
    penyewaans = Penyewaan.objects.filter(id__in=penyewaan_ids).order_by('-tanggal_sewa')
    jumlah_keranjang = len(request.session.get('keranjang_penyewaan', []))
    return render(request, 'pelanggan/riwayat_penyewaan.html', {
        'penyewaans': penyewaans,
        'jumlah_keranjang': jumlah_keranjang,
    })


def keranjang_penyewaan(request):
    """Keranjang penyewaan — publik, berbasis session."""
    items = request.session.get('keranjang_penyewaan', [])
    total = sum((Decimal(str(item['total_biaya'])) for item in items), Decimal('0'))
    jumlah_keranjang = len(items)
    return render(request, 'pelanggan/keranjang_penyewaan.html', {
        'items': items,
        'total': total,
        'jumlah_keranjang': jumlah_keranjang,
    })


def hapus_keranjang(request, item_id):
    """Hapus item dari keranjang berdasarkan UUID."""
    if request.method != 'POST':
        return redirect('keranjang_penyewaan')
    items = request.session.get('keranjang_penyewaan', [])
    items = [item for item in items if item.get('item_id') != item_id]
    request.session['keranjang_penyewaan'] = items
    request.session.modified = True
    return redirect('keranjang_penyewaan')


def checkout_penyewaan(request):
    """Checkout dan konfirmasi pembayaran — publik, tanpa login."""
    items = request.session.get('keranjang_penyewaan', [])
    if not items:
        messages.error(request, "Keranjang penyewaan masih kosong.")
        return redirect('sewa_mobil')

    if request.method == 'POST':
        metode = request.POST.get('metode_pembayaran')
        if metode not in {'Transfer Bank', 'E-Wallet', 'Tunai'}:
            messages.error(request, "Pilih metode pembayaran yang valid.")
            return redirect('keranjang_penyewaan')

        bukti_file = request.FILES.get('bukti_pembayaran')
        guest_user = _get_or_create_guest_user()

        try:
            with transaction.atomic():
                penyewaan_baru_ids = []
                for item in items:
                    mobil = Mobil.objects.select_for_update().get(id=item['mobil_id'], tersedia=True)
                    if Penyewaan.objects.filter(
                        mobil=mobil,
                        status__in=['diajukan', 'disetujui'],
                        tanggal_sewa__lt=item['tanggal_kembali'],
                        tanggal_kembali__gt=item['tanggal_sewa'],
                    ).exists():
                        raise ValueError("Mobil sudah dipesan pada periode tersebut.")

                    penyewaan = Penyewaan.objects.create(
                        pelanggan=guest_user,
                        mobil=mobil,
                        nama_tamu=item.get('nama_tamu', ''),
                        nik_tamu=item.get('nik_tamu', ''),
                        no_telepon_tamu=item.get('no_telepon_tamu', ''),
                        email_tamu=item.get('email_tamu', ''),
                        tanggal_sewa=item['tanggal_sewa'],
                        tanggal_kembali=item['tanggal_kembali'],
                        lama_sewa=item['lama_sewa'],
                        total_biaya=item['total_biaya'],
                        dengan_supir=False,
                        metode_pembayaran=metode,
                        status='diajukan'
                    )
                    Pembayaran.objects.create(
                        penyewaan=penyewaan,
                        jumlah=item['total_biaya'],
                        metode=metode,
                        status='menunggu',
                        bukti_pembayaran=bukti_file,
                    )
                    penyewaan_baru_ids.append(penyewaan.id)

        except (Mobil.DoesNotExist, ValueError) as exc:
            messages.error(request, str(exc) or "Salah satu mobil di keranjang sudah tidak tersedia.")
            return redirect('keranjang_penyewaan')

        # Simpan ID penyewaan ke session untuk fitur riwayat
        existing_ids = request.session.get('penyewaan_ids', [])
        existing_ids.extend(penyewaan_baru_ids)
        request.session['penyewaan_ids'] = existing_ids

        request.session['keranjang_penyewaan'] = []
        request.session.modified = True
        messages.success(request, "Pemesanan berhasil dikirim! Tunggu konfirmasi dari Admin.")
        return redirect('riwayat_penyewaan')

    jumlah_keranjang = len(items)
    return render(request, 'pelanggan/pembayaran.html', {
        'items': items,
        'total': sum((Decimal(str(i['total_biaya'])) for i in items), Decimal('0')),
        'jumlah_keranjang': jumlah_keranjang,
    })
