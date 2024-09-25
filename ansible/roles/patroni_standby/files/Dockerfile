FROM postgres:14.8

ARG PGHOME=/patroni
ARG PGDATA=$PGHOME/data

# TODO: set env to config patroni.yml
ENV PATH=${PATH}:/usr/lib/postgresql/14/bin

# install dependencies
RUN apt-get update -y && apt-get install -y python3-pip python3-six && apt-get install pgbackrest -y

# install patroni by pip
COPY requirements.txt $PGHOME
WORKDIR $PGHOME
RUN pip3 install --break-system-packages -r requirements.txt --proxy=http://10.61.11.42:3128

# cleanup
RUN apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/* /root/.cache

# setup localdef
RUN localedef -i en_US -f UTF-8 en_US.UTF-8

# specify command
CMD ["/usr/local/bin/patroni", "$PGHOME/patroni.yml"]