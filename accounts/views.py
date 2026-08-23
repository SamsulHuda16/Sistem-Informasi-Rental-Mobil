from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from administrator.models import CustomUser, Mobil, Pengaturan


def landing_page(request):
    """Halaman depan publik — katalog mobil, langsung bisa sewa tanpa login."""
    mobils = Mobil.objects.all().order_by('nama_mobil')
    jumlah_keranjang = len(request.session.get('keranjang_penyewaan', []))
    
    # Dapatkan pengaturan latar belakang hero
    bg_setting = Pengaturan.objects.filter(kunci='hero_background').first()
    hero_bg_url = bg_setting.nilai_gambar.url if bg_setting and bg_setting.nilai_gambar else '/media/hero_bg.jpg'
    
    # Dapatkan pengaturan latar belakang katalog
    bg_katalog_setting = Pengaturan.objects.filter(kunci='katalog_background').first()
    katalog_bg_url = bg_katalog_setting.nilai_gambar.url if bg_katalog_setting and bg_katalog_setting.nilai_gambar else ''
    
    return render(request, 'accounts/landing.html', {
        'mobils': mobils,
        'jumlah_keranjang': jumlah_keranjang,
        'hero_bg_url': hero_bg_url,
        'katalog_bg_url': katalog_bg_url,
    })


def login_view(request):
    """Login khusus Admin."""
    # Jika sudah login sebagai admin, langsung ke dashboard admin
    if request.user.is_authenticated and hasattr(request.user, 'role'):
        if request.user.role == 'administrator':
            return redirect('admin_dashboard')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)

            if user.role == "administrator":
                return redirect("admin_dashboard")

            else:
                # Pelanggan tidak bisa login — tolak dan kembali ke landing
                logout(request)
                messages.error(request, "Halaman login ini hanya untuk Admin.")
                return redirect("login")

        messages.error(request, "Username atau Password salah.")

    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("landing")
