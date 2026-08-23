from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),

    path('laporan/', views.laporan_penyewaan, name='laporan_penyewaan'),

    path('mobil/', views.data_mobil, name='data_mobil'),

    path('mobil/tambah/', views.tambah_mobil, name='tambah_mobil'),
    path('mobil/edit/<int:id>/', views.edit_mobil, name='edit_mobil'),
    path('mobil/hapus/<int:id>/', views.hapus_mobil, name='hapus_mobil'),

    path('penyewaan/', views.data_penyewaan, name='data_penyewaan'),

    path('penyewaan/setujui/<int:id>/', views.setujui_penyewaan, name='setujui_penyewaan'),
    path('penyewaan/tolak/<int:id>/', views.tolak_penyewaan, name='tolak_penyewaan'),
    path('penyewaan/hapus/<int:id>/', views.hapus_penyewaan, name='hapus_penyewaan'),
    path('penyewaan/selesai/<int:id>/', views.selesai_penyewaan, name='selesai_penyewaan'),

    path('pengembalian/', views.data_pengembalian, name='data_pengembalian'),
    path('pengembalian/tambah/<int:id>/', views.tambah_pengembalian, name='tambah_pengembalian'),
    path('pengembalian/hapus/<int:id>/', views.hapus_pengembalian, name='hapus_pengembalian'),

    path('pembayaran/', views.data_pembayaran, name='data_pembayaran'),
    path('pembayaran/lunas/<int:id>/', views.lunas_pembayaran, name='lunas_pembayaran'),
    path('pembayaran/hapus/<int:id>/', views.hapus_pembayaran, name='hapus_pembayaran'),

    path('pelanggan/', views.data_pelanggan, name='data_pelanggan'),
    path('pelanggan/verifikasi/<int:id>/', views.verifikasi_pelanggan, name='verifikasi_pelanggan'),
    path('pelanggan/edit/<int:id>/', views.edit_pelanggan, name='edit_pelanggan'),
    path('pelanggan/hapus/<int:id>/', views.hapus_pelanggan, name='hapus_pelanggan'),

    path('petugas/', views.data_petugas, name='data_petugas'),
    path('petugas/tambah/', views.tambah_petugas, name='tambah_petugas'),
    path('petugas/edit/<int:id>/', views.edit_petugas, name='edit_petugas'),
    path('petugas/hapus/<int:id>/', views.hapus_petugas, name='hapus_petugas'),
    path('petugas/ubah-role/<int:id>/', views.ubah_role_petugas, name='ubah_role_petugas'),
    path('pengaturan/', views.pengaturan, name='pengaturan'),
]
