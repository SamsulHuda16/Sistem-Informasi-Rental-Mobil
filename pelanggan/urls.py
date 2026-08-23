from django.urls import path
from . import views

urlpatterns = [
    path('mobil/', views.daftar_mobil, name='daftar_mobil'),
    path('sewa/', views.sewa_mobil, name='sewa_mobil'),
    path('keranjang/', views.keranjang_penyewaan, name='keranjang_penyewaan'),
    path('keranjang/hapus/<str:item_id>/', views.hapus_keranjang, name='hapus_keranjang'),
    path('pembayaran/', views.checkout_penyewaan, name='checkout_penyewaan'),
    path('riwayat/', views.riwayat_penyewaan, name='riwayat_penyewaan'),
]
