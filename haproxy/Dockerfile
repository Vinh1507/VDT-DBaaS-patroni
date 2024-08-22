FROM haproxy:latest

USER root

# Install confd
RUN apt-get update && apt-get install -y wget && \
    wget https://github.com/kelseyhightower/confd/releases/download/v0.16.0/confd-0.16.0-linux-amd64 -O /usr/local/bin/confd && \
    chmod +x /usr/local/bin/confd

# Copy confd configuration and templates
COPY confd /etc/confd

# Copy HAProxy configuration file
COPY haproxy.cfg /etc/haproxy/haproxy.cfg

# Copy HAProxy entrypoint script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set environment variables
ENV ETCDCTL_API=3

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# HAProxy default command
CMD ["haproxy", "-f", "/etc/haproxy/haproxy.cfg", "-p", "/var/run/haproxy.pid", "-D"]