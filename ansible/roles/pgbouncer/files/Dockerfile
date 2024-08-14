# Sử dụng edoburu/pgbouncer làm image base
FROM edoburu/pgbouncer:latest

USER root

RUN mkdir -p /var/log/postgresql \
    && chmod 755 /var/log/postgresql
# (Tuỳ chọn) Thiết lập thêm các lệnh khác nếu cần

# Cấu hình entrypoint hoặc CMD nếu cần
# CMD ["pgbouncer", "/etc/pgbouncer/pgbouncer.ini"]
