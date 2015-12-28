#
# Consul Couchbase
#
FROM 		couchbase/server:community
MAINTAINER 	Valentin Dubois <veacks.net>

ENV CB_USERNAME Administrator
ENV CB_PASSWORD password

COPY bin/* /usr/local/bin/

EXPOSE 8091 8092 11207 11210 11211 18091 18092
VOLUME /opt/couchbase/var

RUN apt-get update && apt-get install -y python-pip python-dev build-essential
RUN pip install --upgrade pip

RUN pip install netifaces httplib2

ENTRYPOINT ["consul-couchbase-start"]
CMD ["couchbase-server"]
