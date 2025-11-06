import os
from dotenv import load_dotenv

# 1. Cargar variables de entorno primero
load_dotenv()

# 2. Configurar entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lilis.settings')

import django
django.setup()

# 3. Importar Django una vez configurado
from django.core.mail import send_mail
from django.conf import settings

# 4. Probar envío
send_mail(
    'Prueba',
    'Correo de prueba desde Django.',
    settings.DEFAULT_FROM_EMAIL,
    ['drixtcorp@gmail.com'],
    fail_silently=False
)
