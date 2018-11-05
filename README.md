# Fondo-API
Django REST API. It provides access to fund's information

## Run tests:
### Coverage HTML
`coverage run --branch --source='.' manage.py test && coverage html --omit="*env*,*tests*,api/wsgi.py,fondo_api/apps.py,manage.py,*migrations*,fondo_api/routing.py"`

### Coverage plain
`coverage run --branch --source='.' manage.py test && coverage report -m --omit="*env*,*tests*,api/wsgi.py,fondo_api/apps.py,manage.py,*migrations*,fondo_api/routing.py"`
