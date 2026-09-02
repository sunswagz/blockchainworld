# Sức khoẻ xưởng — 02/09/2026 21:32 UTC · lượt 587

Xưởng chạy được: mọi node trong sổ đều `ok` ở lượt gần nhất, trừ đúng một.

**Đáng lo — `dong-dau`.** Ngã lúc 21:19:59, `vi: khoa-sai`, `chuoiLoi` 1. Sáng
nay 11:37:03 nó còn `ok`, nên đây là hỏng mới trong ngày. Sai khoá không tự lành
theo lượt: nhịp 6 giờ nghĩa là nó sẽ ngã lại y như vậy.

**Ngoài nó ra, không có gì:** không node nào `chuoiLoi >= 2`, không node nào trễ
quá gấp đôi `nhip`. Xa hạn nhất là `do-kho` (4,9 ngày / nhịp 168) và nhóm nhịp 24
chạy 01/09 19:05 — đều còn trong hạn.

**Chạy đều mà `lucDoi` đứng yên** — nguồn phía sau có thể đã đứng:
- `tri-thuc`: `lucDoi: null`, `doi: false`, 0 giây mỗi lượt — chạy nhiều lượt, chưa từng ghi đổi lần nào.
- `tien-hoa-dqt`: chạy 02/09, `lucDoi` 30/08; chú thích "0 điểm yếu" tự giải thích.
- `hoang-thanh`: `lucDoi` 14/08 — nhưng `nhip: 0`, chạy tay, không phải node tự động.

**Cần kiểm, chưa phải báo động:** `kham-thien-giam`, `thi-bac-ty`, `tu-cam-thanh`,
`giao-hang` không có dòng nào trong `state.json` — cả bốn đều khai `nhip: 0`.

**VIỆC NÊN LÀM TRƯỚC: xem khoá của `dong-dau`.** Nó là node duy nhất đang ngã, và
`khoa-sai` là loại lỗi lượt sau không chữa hộ.
