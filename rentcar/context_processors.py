from administrator.models import Pengaturan

def pengaturan_global(request):
    try:
        logo = Pengaturan.objects.filter(kunci='logo_toko').first()
        logo_url = logo.nilai_gambar.url if logo and logo.nilai_gambar else None
        
        favicon = Pengaturan.objects.filter(kunci='favicon').first()
        favicon_url = favicon.nilai_gambar.url if favicon and favicon.nilai_gambar else None
    except Exception:
        logo_url = None
        favicon_url = None
        
    return {
        'global_logo_toko': logo_url,
        'global_favicon': favicon_url
    }
