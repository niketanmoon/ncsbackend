# ncsbackend
## Create an environment
```pyenv virtualenv 3.X.X envname```

## Now install dependencies 
```pip install -r requirements.txt```

## Create file called local_settings.py where settings.py file resides
```DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ncswallet",
        "USER": "ncswallet",
        "PASSWORD": "root",
        "HOST": "localhost",
    }
}```

## Migrate 
```python manage.py migrate```

## createsuperuser
```python manage.py createsuperuser```

## runserver
```python manage.py runserver```