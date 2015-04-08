SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    'django.contrib.sessions',
    "bread",
    "tests",
]
TEMPLATE_DIRS = [
    'bread/templates',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}
