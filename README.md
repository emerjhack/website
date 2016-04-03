# EmerjHack Website
This is the website for EmerjHack.

## Dependencies

* pip install django==1.9.4
* pip install django-ipware==1.1.3
* pip install requests==2.9.1
* pip install psycopg2==2.6.1 # For production only

### Environment variables

#### Development

* DJANGO_SECRET_KEY=???
* DJANGO_EMAIL_HOST_USER=???
* DJANGO_EMAIL_HOST_PASSWORD=???
* DJANGO_BASE_URL=http://127.0.0.1:8000/
* DJANGO_PRODUCTION=FALSE

#### Production

* DJANGO_SECRET_KEY=???
* DJANGO_EMAIL_HOST_USER=???
* DJANGO_EMAIL_HOST_PASSWORD=???
* DJANGO_BASE_URL=https://what-is-qa.emerjhack.com/
* DJANGO_PRODUCTION=TRUE
* DJANGO_DB_NAME=???
* DJANGO_DB_USER=???
* DJANGO_DB_PASS=???
* DJANGO_DB_HOST=???
* DJANGO_DB_PORT=???

