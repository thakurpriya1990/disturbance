FROM ubuntu:18.04 as builder_base_das
MAINTAINER asi@dbca.wa.gov.au
ENV DEBIAN_FRONTEND=noninteractive
ENV DEBUG=True
ENV TZ=Australia/Perth
ENV EMAIL_HOST="smtp.corporateict.domain"
ENV DEFAULT_FROM_EMAIL='no-reply@dbca.wa.gov.au'
#ENV NOTIFICATION_EMAIL='jawaid.mushtaq@dbca.wa.gov.au'
ENV NOTIFICATION_EMAIL='brendan.blackford@dbca.wa.gov.au'
ENV NON_PROD_EMAIL='brendan.blackford@dbca.wa.gov.au, walter.genuit@dbca.wa.gov.au, katsufumi.shibata@dbca.wa.gov.au, mohammed.ahmed@dbca.wa.gov.au, test_licensing@dpaw.wa.gov.au, jawaid.mushtaq@dbca.wa.gov.au'
ENV PRODUCTION_EMAIL=False
ENV EMAIL_INSTANCE='DEV'
ENV SECRET_KEY="ThisisNotRealKey"
ENV SITE_PREFIX='das-apiary'
ENV SITE_DOMAIN='dbca.wa.gov.au'
ENV OSCAR_SHOP_NAME='Parks & Wildlife'
ENV BPAY_ALLOWED=False
RUN apt-get update \
  && apt-get upgrade -y \
  && apt-get install -yq git mercurial gcc gdal-bin libsasl2-dev libpq-dev \
  python python-setuptools python-dev python-pip \
  imagemagick poppler-utils \
  libldap2-dev libssl-dev wget build-essential \
  libmagic-dev binutils libproj-dev tzdata postgresql-client
RUN pip install --upgrade pip
#RUN apt-get install -yq vim

# Install Python libs from requirements.txt.
FROM builder_base_das as python_libs_das
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
  # Update the Django <1.11 bug in django/contrib/gis/geos/libgeos.py
  # Reference: https://stackoverflow.com/questions/18643998/geodjango-geosexception-error
  && sed -i -e "s/ver = geos_version().decode()/ver = geos_version().decode().split(' ')[0]/" /usr/local/lib/python2.7/dist-packages/django/contrib/gis/geos/libgeos.py \
  && rm -rf /var/lib/{apt,dpkg,cache,log}/ /tmp/* /var/tmp/*


# Install the project (ensure that frontend projects have been built prior to this step).
FROM python_libs_das
COPY gunicorn.ini manage_ds.py ./
RUN touch /app/.env
COPY .git ./.git
#COPY ledger ./ledger
COPY disturbance ./disturbance
RUN python manage_ds.py collectstatic --noinput
EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["gunicorn", "disturbance.wsgi", "--bind", ":8080", "--config", "gunicorn.ini"]

