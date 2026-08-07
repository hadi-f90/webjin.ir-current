

import os
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(APP_DIR, '.env'), override=True)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# import os
# import sys

# sys.path.insert(0, os.path.dirname(__file__))

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()


# import os
# import sys

# sys.path.insert(0, os.path.dirname(__file__))

# # Load .env before Django settings
# from pathlib import Path
# env_path = Path(__file__).resolve().parent / '.env'
# if env_path.is_file():
#     from dotenv import load_dotenv
#     load_dotenv(env_path)

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()