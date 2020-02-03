# Fondo-API [![](https://travis-ci.org/Fonmon/Fondo-Web.svg?branch=master)]()
Django REST API. It provides access to fund's information

## Run tests:
### Coverage HTML
`coverage run --branch --source='.' manage.py test && coverage html --omit="*env*,*tests*,api/wsgi.py,fondo_api/apps.py,manage.py,*migrations*"`

### Coverage plain
`coverage run --branch --source='.' manage.py test && coverage report -m --omit="*env*,*tests*,api/wsgi.py,fondo_api/apps.py,manage.py,*migrations*"`

## Postgres Docker
`docker run -d --name fondo_db -p 5432:5432 -e POSTGRES_DB=fondodev -e POSTGRES_USER=fondouser -e POSTGRES_PASSWORD=fondo postgres`