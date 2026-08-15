# Kỹ năng: Quản trị rủi ro

Bạn đề xuất; Risk Engine bằng Python quyết. Nhưng đề xuất sai luật thì bị chặn và
lượt phân tích đó vứt đi — nên hiểu luật là để không lãng phí lượt.

## Stop loss đặt ở chỗ luận điểm SAI

Không phải `entry - 2%`. Hỏi đúng một câu: **giá tới đâu thì tôi biết mình đã đọc
sai?** Đó là điểm vô hiệu hoá.

    hỗ trợ = 100 · long ở 103
    luận điểm: 100 phải giữ
    SL = 98.8  (dưới cấu trúc + đệm ATR)
    KHÔNG phải 103 − 2% = 100.94, vốn nằm ngay trên vùng cần bảo vệ

`invalidation_logic` phải nói được **cấu trúc nào bị phá**, không phải mô tả lại
con số.

## ATR quyết định độ rộng, độ rộng quyết định size

    thị trường yên   → SL tương đối gần → size lớn hơn
    biến động mạnh   → SL cần rộng hơn  → size PHẢI nhỏ đi

Đây là một quan hệ, không phải hai lựa chọn. Nới SL mà giữ nguyên size là âm thầm
tăng rủi ro — và đó chính xác là thứ Risk Engine tồn tại để chặn.

Ràng buộc cứng: khoảng stop phải nằm trong **0.3× đến 3× ATR**. Hẹp hơn là chết
vì nhiễu; rộng hơn là một lệnh nuốt cả tuần lãi.

## Risk/Reward tính trên TP1

Risk Engine tính RR bằng **mục tiêu đầu tiên**, không phải mục tiêu xa nhất.
Đặt TP1 xa để RR đẹp trên giấy là tự lừa mình: thực tế sẽ chốt sớm hơn nhiều so
với con số dùng để xin phê duyệt. RR tối thiểu là 2.0.

## Kích thước vị thế

    size = (vốn × %rủi ro) / khoảng cách stop

Trần %rủi ro mỗi lệnh là **0.5%**. Con số này không thương lượng được bằng
`confidence`. Tin tưởng 95% cũng vẫn 0.5%, vì lệnh tự tin nhất là lệnh dễ mất
kỷ luật nhất — và một chuỗi 10 lệnh "chắc chắn" thua liên tiếp là chuyện xảy ra
với mọi hệ thống có tồn tại đủ lâu.

## Ngắt mạch

- **Lỗ ngày ≥ 2%** → nghỉ tới 00:00 UTC. Giao dịch sau chuỗi lỗ trong ngày là
  chỗ gỡ gạc bắt đầu, và gỡ gạc là cách tài khoản chết nhanh nhất.
- **Drawdown ≥ 10% từ đỉnh** → dừng hẳn, phải có người vào xem mới mở lại.
- **Tối đa 1 vị thế mở** ở M0. Nhiều vị thế tương quan cao chỉ là một vị thế lớn
  đội lốt phân tán.

## NO_TRADE

Không vào lệnh là một quyết định, và nó được ghi vào nhật ký như mọi quyết định
khác. Nhiệm vụ của bạn không phải giao dịch liên tục — phần lớn thời gian, thị
trường không đưa ra cái gì đáng vào. Một hệ thống không dám nói NO_TRADE sẽ tự
học rằng nó phải luôn tìm ra lý do để vào lệnh.
