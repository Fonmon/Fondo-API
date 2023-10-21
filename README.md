# Fondo-API [![](https://codebuild.us-east-2.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiQlZtSUV0L1YwTEg4UDBkaHpvc0lCcE0yTkQ1blFMSFQxbGxJMUZ3R0xjOEY4T3dpcGVpMkNWUWtSSzk2VGYyZStVSlJsUC9VWkhTcXQvNHgwb3I0ckswPSIsIml2UGFyYW1ldGVyU3BlYyI6IjhqdXhESFJmTmZsQXk4QTkiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)]()
Django REST API. It provides access to fund's information

## Run tests:
### Coverage HTML
`coverage run --branch --source='.' manage.py test && coverage html --omit="*env*,*tests*,api/wsgi.py,fondo_api/apps.py,manage.py,*migrations*"`

### Coverage plain
`coverage run --branch --source='.' manage.py test && coverage report -m --omit="*env*,*tests*,api/wsgi.py,fondo_api/apps.py,manage.py,*migrations*"`

## Docker containers
`docker run -d --name fondo_db -p 5432:5432 -e POSTGRES_DB=fondodev -e POSTGRES_USER=fondouser -e POSTGRES_PASSWORD=fondo postgres`

`docker run --name redis -p 6379:6379 -d redis`
