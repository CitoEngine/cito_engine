FROM ubuntu:14.04.2

MAINTAINER K.G.R Vamsi

# Install MySQL Server in a Non-Interactive mode. Default root password will be "root"
RUN echo "deb http://www.rabbitmq.com/debian/ testing main" >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y wget \
    && wget -O- https://www.rabbitmq.com/rabbitmq-release-signing-key.asc |sudo apt-key add - \
    && apt-get install -y debconf-utils python python-pip git build-essential libmysqlclient-dev python-dev rabbitmq-server --force-yes \
    && echo mysql-server-5.5 mysql-server/root_password password password | debconf-set-selections \
    && echo mysql-server-5.5 mysql-server/root_password_again password password | debconf-set-selections \
    && apt-get install -y mysql-server-5.5 -o pkg::Options::="--force-confdef" -o pkg::Options::="--force-confold" --fix-missing \
    && apt-get install -y net-tools --fix-missing \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/CitoEngine/cito_engine.git /cito_engine

RUN pip install -r cito_engine/requirements.txt

RUN mkdir -p /opt/citoengine/conf/ \
     && mv cito_engine/app/settings/citoengine.conf-example /opt/citoengine/conf/citoengine.conf

# Populate the database
RUN service mysql start \
    && mysql -uroot -ppassword -e "create database citoengine;" \
    && python cito_engine/app/manage.py migrate

WORKDIR /cito_engine

EXPOSE 8000

ENTRYPOINT ["sh","bin/docker_app_run.sh"]

