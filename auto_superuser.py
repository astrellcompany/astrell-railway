import os
import django

# Tell Django where settings are
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "astrellcapitalinvest.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = "ejikesite"
password = "ejikesite105$"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        password=password,
        email=""
    )
    print("Superuser created successfully.")
else:
    print("Superuser already exists.")
