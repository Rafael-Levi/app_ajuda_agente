import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")  # ajuste se o nome for outro
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
first_name = os.environ.get("DJANGO_SUPERUSER_FIRST_NAME", "")
last_name = os.environ.get("DJANGO_SUPERUSER_LAST_NAME", "")

if not User.objects.filter(username=username).exists():
    print(f"Criando superusuário '{username}'...")
    user = User.objects.create_superuser(username=username, email=email, password=password)
    user.first_name = first_name
    user.last_name = last_name
    user.save()
else:
    print(f"Superusuário '{username}' já existe. Pulando criação.")
