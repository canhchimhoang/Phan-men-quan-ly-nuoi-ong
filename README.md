# Hệ thống quản lý việc nuôi ong (Flutter + SQLite)

Ứng dụng Android/iPhone, dữ liệu lưu ngay trên điện thoại bằng SQLite. Dữ liệu mẫu lấy từ file
"phần mềm quản lý nuôi ong.xlsx" (3 tổ ong, 5 lần thăm, 3 vị trí) và được nạp tự động ở lần mở đầu tiên.

**Tài khoản mẫu:** `admin` / `123456`

## Chức năng
| Màn hình | Nội dung |
|---|---|
| Đăng nhập | Ảnh nền chú ong bay giữa thiên nhiên (làm mờ), kiểm tra dữ liệu nhập, hiện/ẩn mật khẩu, ghi nhớ đăng nhập, đăng ký tài khoản, quên mật khẩu (câu hỏi bảo mật), đăng xuất |
| Quản lý tổ ong | Thêm / sửa / xóa tổ ong (mã tự tăng `ong_0004`…), chọn vị trí từ danh mục |
| Vị trí tổ ong | Danh mục vị trí nhập riêng: thêm / sửa / xóa |
| Thăm tổ ong | Thêm / sửa / xóa lần thăm: lần thăm thứ n (tự gợi ý), ngày, tình trạng, mật / phấn hoa / keo (gram), tách đàn |
| Tra cứu | Tìm tổ ong hoặc lần thăm theo từ khóa (không phân biệt hoa/thường và dấu tiếng Việt) |
| Thống kê, báo cáo | Thẻ *Bộ lọc* (tên tổ, lần thăm thứ n, ngày thăm, tình trạng), thẻ *Theo tổ ong* (tổng mật/phấn hoa/keo từng tổ), thẻ *Theo thời gian* (từ ngày … đến ngày …) |
| Nhắc lịch thăm | Đặt ngày giờ cho từng tổ, app gửi thông báo đúng giờ (kể cả khi đã đóng app); có nút gửi thử thông báo |

## Build file APK

### Cách 1 – GitHub Actions (không cần cài gì trên máy)
1. Tạo một repository GitHub mới, đẩy toàn bộ thư mục này lên nhánh `main`.
2. Vào tab **Actions** → workflow **Build APK** sẽ tự chạy (hoặc bấm *Run workflow*).
3. Khi xong, tải file `quan-ly-nuoi-ong-apk` ở cuối trang chạy → giải nén ra `app-release.apk` → chép vào điện thoại Android và cài
   (cho phép "Cài ứng dụng không rõ nguồn gốc").

### Cách 2 – Trên máy tính đã cài Flutter SDK + Android Studio
```bash
python3 tools/patch_android.py     # sinh android/, thêm quyền thông báo, bật desugaring
flutter pub get
dart run flutter_launcher_icons     # (tùy chọn) icon ứng dụng
flutter build apk --release
# kết quả: build/app/outputs/flutter-apk/app-release.apk
```
Chạy thử trên giả lập: mở Android Studio → Device Manager tạo máy ảo → `flutter run`.
(Trên Windows dùng `python tools\patch_android.py`.)

## Cấu trúc mã nguồn
```
lib/
  main.dart                 khởi động, theme, ngôn ngữ tiếng Việt
  db/app_database.dart      SQLite: bảng, dữ liệu mẫu, truy vấn, thống kê
  models/models.dart        lớp dữ liệu
  services/                 session.dart (đăng nhập), notification_service.dart (nhắc lịch)
  screens/                  các màn hình
  widgets/common.dart       ô chọn, ô ngày, định dạng, thẻ dùng chung
assets/images/              login_bg.png (nền ong bay), app_icon.png
tools/patch_android.py      chuẩn bị thư mục android
```

## Lưu ý
- Cột ngày trong file Excel bị lẫn định dạng (VD "02/11" bị đọc thành 11/02). Dữ liệu mẫu đã chuẩn hóa về ngày/tháng/năm: tổ 2 tạo 02/11/2026, tổ 3 tạo 10/11/2026; lần thăm 09/11, 10/11, 15/11, 16/11.
- Bảng tổ ong trong Excel có dòng STT 4 để trống, bỏ qua.
- Android 13+ hỏi quyền thông báo lần đầu mở màn hình Nhắc lịch. Nếu không cấp quyền báo thức chính xác, thông báo có thể trễ vài phút.
- iPhone: cần máy Mac + Xcode để build; thông báo khi app đang mở trên iOS có thể cần cấu hình thêm `AppDelegate`.
