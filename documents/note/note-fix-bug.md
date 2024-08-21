# Note fix bug

Một số cách fix bug khi bị lỗi started fail

- Kiểm tra đã stop postgresql
- Kiểm tra danh sách các node đã được cấu hình đúng trong pg_hba.conf
- Khi restart có thể bị lỗi khi file data lưu patroni đã tồn tại trước đó (trong phần cài đặt là /data/patroni), có thể xóa đi và mkdir lại, chú ý chown và chmod

## Lỗi không có leader nào 

Lỗi xảy ra khi cấu hình sai pg_hba.conf, và khi sửa node nào thì node đó lại chờ bootstrap từ node leader, thành ra không có leader nào khả dụng. Hoặc có leader khả dụng thì leader đấy đang cấu hình sai thì bootstrap cũng lỗi config

```
vinh@node2:~$ patronictl -c /etc/patroni.yml list
+ Cluster: postgres (7404403235850823971) -----+----+-----------+
| Member | Host            | Role    | State   | TL | Lag in MB |
+--------+-----------------+---------+---------+----+-----------+
| node1  | 192.168.144.133 | Replica | stopped |    |   unknown |
| node2  | 192.168.144.135 | Replica | stopped |    |   unknown |
| node3  | 192.168.144.136 | Replica | stopped |    |   unknown |
+--------+-----------------+---------+---------+----+-----------+
```


Cách xử lý tạm thời: remove toàn bộ cluster và start lại từng node

```
vinh@node2:~$ patronictl -c /etc/patroni.yml remove postgres
+ Cluster: postgres (7404403235850823971) -----+----+-----------+
| Member | Host            | Role    | State   | TL | Lag in MB |
+--------+-----------------+---------+---------+----+-----------+
| node1  | 192.168.144.133 | Replica | stopped |    |   unknown |
| node2  | 192.168.144.135 | Replica | stopped |    |   unknown |
| node3  | 192.168.144.136 | Replica | stopped |    |   unknown |
+--------+-----------------+---------+---------+----+-----------+
```

Sau đó, khởi động lại 1 node bất kỳ, và kiểm tra lại trạng thái của cluster
