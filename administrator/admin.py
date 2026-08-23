from django.contrib import admin
from .models import (
    CustomUser,
    Mobil,
    Penyewaan,
    Pengembalian,
    Pembayaran,
    HistoriJabatan,
    Pengaturan
)

@admin.register(Penyewaan)
class PenyewaanAdmin(admin.ModelAdmin):
    list_display = (
        'pelanggan',
        'mobil',
        'tanggal_sewa',
        'tanggal_kembali',
        'status'
    )

    list_filter = ('status',)
    search_fields = ('pelanggan__username', 'mobil__nama_mobil')
     
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.status == 'disetujui':
            obj.mobil.tersedia = False
            obj.mobil.save()


admin.site.register(CustomUser)
admin.site.register(Mobil)
admin.site.register(Pengembalian)
admin.site.register(Pembayaran)
admin.site.register(HistoriJabatan)
admin.site.register(Pengaturan)