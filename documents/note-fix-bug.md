# Note fix bug

Một số cách fix bug khi bị lỗi started fail

- Kiểm tra đã stop postgresql
- Kiểm tra danh sách các node đã được cấu hình đúng trong pg_hba.conf
- Khi restart có thể bị lỗi khi file data lưu patroni đã tồn tại trước đó (trong phần cài đặt là /data/patroni), có thể xóa đi và mkdir lại, chú ý chown và chmod