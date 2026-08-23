import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rentcar.settings")

import django

django.setup()

from administrator.models import CustomUser


accounts = [
    ("dummyadmin", "administrator", "dummyadmin123"),
    ("dummypetugas", "administrator", "dummypetugas123"),
    ("dummypelanggan", "pelanggan", "dummypelanggan123"),
]

for username, role, password in accounts:
    user, _ = CustomUser.objects.get_or_create(username=username)
    user.email = f"{username}@example.com"
    user.role = role
    user.set_password(password)
    
    if role == 'administrator':
        user.is_staff = True
        user.is_superuser = True
    else:
        user.is_staff = False
        user.is_superuser = False
        
    user.save()
    print(f"{username}: {password}")
