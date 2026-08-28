# THỊ BẠC TY — bộ máy quản lý và vận hành vốn

Thị Bạc Ty **không phải một chiến lược**. Nó là cả cỗ máy: quan sát thị
trường · phát hiện cơ hội · định giá · kiểm soát rủi ro · phân bổ vốn · thực
thi · kế toán · học từ kết quả.

```
                    THỊ BẠC TY
                         │
           ┌─────────────┴─────────────┐
           │                           │
      TRUNG ƯƠNG                    CÁC TY
    thi_bac_ty/                   bac/ ← ty đầu tiên
    Data · Risk · Capital         Phái sinh · Tín dụng ·
    Ledger · Execution            Chênh lệch · Thanh khoản ·
                                  Thanh lý · MEV · Cầu nối
```

Thứ đang chạy trong `bac/` là **`perpetual.funding_spread.v1`** — ty đầu
tiên đã hoạt động, không phải toàn bộ Thị Bạc Ty và cũng chưa phải toàn bộ
ty Phái Sinh.

## Luật chung của mọi ty

```
KHÔNG ty nào được tự quản toàn bộ vốn của hệ thống.
KHÔNG ty nào được tự dựng Rủi Ro Tổng riêng.
KHÔNG ty nào được tự quyết danh mục.

MỌI ty chỉ: phát hiện → đánh giá → xuất TỜ TRÌNH.
```

Không có luật này thì mười ba ty là mười ba đứa đều tưởng tiền trong ví là
của mình, và không đứa nào nhìn thấy tổng.

## Tờ trình — đồng tiền ngôn ngữ

Mọi ty nói với trung ương bằng đúng một kiểu: `thi_bac_ty.to_trinh.ToTrinh`.

    bac.models.CoHoi   thứ ty TỰ TÌM RA — nội bộ, đầy thuật ngữ funding
    ToTrinh            thứ ty TRÌNH LÊN — chung, mọi ty đều hiểu

`CoHoi` có `soMocLong`, `intervalShortGio` — những từ ty Tín Dụng không hiểu
và không cần hiểu. `bac/xuat_to_trinh.py` dịch giữa hai thứ, và **không viết
lại thuật toán nào**.

### Ba luật của hợp đồng

**1. KHÔNG BIẾT phải khác KHÔNG.** Ty Phái Sinh không chạm hợp đồng thông
minh nên `ruiRo.giaoThuc = None`, **không phải 0**. Ghi 0 là nói "đã xét,
không có rủi ro", rồi Rủi Ro Tổng cộng những số 0 ấy lại thành một danh mục
an toàn giả.

**2. Con số chưa đủ mô hình phải TỰ KHAI.** Khi trung ương xếp hạng:

    perp.funding_spread   18 bps   ← chặn trên, thiếu bốn khoản phí
    credit.lending_rate   11 bps   ← đã trừ đủ

kết luận "cái đầu tốt hơn" là kết luận SAI rút ra từ hai con số không cùng
đơn vị. `moHinhPhiDuChua` và `moHinhSucChuaDuChua` tồn tại để chặn đúng
chuyện đó.

**3. Hợp đồng tự soát mình.** `ToTrinh.kiem()` chạy không cần mạng, không
cần trung ương. Tờ trình sai khuôn chết ở CỬA TY, không trôi vào sổ đăng ký
rồi làm hỏng thống kê ba tháng sau.

### `netMoiGioBps` — thước so sánh giữa các ty

Không so `netUocBps` trần được:

    20 bps giữ 24 giờ   →  0,83 bps/giờ
     6 bps giữ  2 giờ   →  3,00 bps/giờ   ← thắng, vì vốn quay 12 lượt

Vẫn chưa phải thước cuối: nó chưa xét sức chứa (rót được bao nhiêu) và chưa
xét rủi ro. Người phân bổ vốn phải nhìn cả ba.

### Sức chứa còn THÔ, và nói thẳng là thô

`ToTrinh` đòi `sucChuaToiDaUsd` — rót thêm tới đâu thì chính cơ hội tự giết
mình. Sức chứa thật đo bằng **độ sâu sổ lệnh**, mà runtime chưa hỏi sổ lệnh
của cảng nào. `bac/suc_chua.py` tạm suy từ open interest (0,05%, lấy MIN hai
chân, có trần và sàn), và **luôn** khai `moHinhSucChuaDuChua = False`.

Vì sao không trả `None` cho xong: người phân bổ vốn gặp `None` thì không
sizing được gì, và mọi tờ trình của ty này thành vô dụng — trong khi ta vẫn
biết chắc một điều, **không phải vô hạn**.

### Chiều phụ thuộc, một chiều

    bac/  (ty)  ──import──►  thi_bac_ty/  (trung ương)

Trung ương không được import ngược, và có phép kiểm canh việc đó. Ngày trung
ương phải `import bac` để xử một trường hợp riêng là ngày hợp đồng đã hỏng:
chỗ phải sửa là hợp đồng, không phải thêm một nhánh `if`.

## Trung Ương — chín tầng, và vòng khép kín

`bac/` là MỘT ty. `thi_bac_ty/` là cỗ máy chia vốn đứng trên mọi ty. Thứ tự
này không đảo được: một ty không bao giờ nhìn thấy tổng danh mục, nên nó
không bao giờ được quyết chuyện của tổng.

```
THỊ TRƯỜNG
   │  các ty quét
   ▼
TỜ TRÌNH ──► THÔNG CHÍNH TY ──► SỔ ĐĂNG KÝ (PHAT_HIEN)
                                     │
                                     ▼
                               RỦI RO TỔNG  ◄── DANH MỤC
                              cho tối đa $X
                                     │
                                     ▼
                               PHÂN BỔ VỐN   (cấp TUẦN TỰ)
                                     │
                                     ▼
                          ĐIỀU PHỐI THỰC THI (máy trạng thái hai chân)
                                     │
                                     ▼
                                 SỔ CÁI ──► CHẨN ĐOÁN ──► XÉT THAM SỐ
                                                              │
                                     ┌────────────────────────┘
                                     ▼
                                THỊ TRƯỜNG
```

| tệp | việc |
|---|---|
| `to_trinh.py` | hợp đồng — đồng tiền ngôn ngữ giữa các ty |
| `khuon_ty.py` | khuôn một ty mới phải điền, và **chỉ** được điền |
| `thong_chinh.py` | sàn nhận tờ trình, chặn sai khuôn ngay ở cửa |
| `so_dang_ky.py` | vòng đời mọi tờ trình, và **cái phễu** |
| `danh_muc.py` | ba thước phơi nhiễm: ròng · thô · theo cảng |
| `rui_ro_tong.py` | trả về một **TRẦN**, không phải một chữ có/không |
| `phan_bo.py` | xếp hạng rồi cấp **tuần tự**, xét lại sau mỗi lần |
| `so_cai.py` | sổ chỉ-thêm; sửa sai chỉ có một đường là **đảo** |
| `thuc_thi.py` | máy trạng thái hai chân, có đường lùi |
| `cau_dao.py` | ngắt **tự động**, đóng lại **phải có người** |
| `doi_soat_vi_the.py` | sổ nhớ, danh mục quên — và ai đóng cái lệch ấy |
| `chan_doan_he.py` | bệnh của cả bộ máy, và đề xuất vặn tham số phân bổ |
| `chay_lai_he.py` | chạy lại phân bổ để **đo** đề xuất, không đoán |
| `cong_duyet.py` | bảy luật một đề xuất phải qua trước khi thành bản |
| `ban_tham_so.py` | tham số có số hiệu, có lịch sử, quay lui được |
| `trung_uong.py` | khép vòng, và ép mọi tầng đi đúng thứ tự |

### Sổ NHỚ, danh mục QUÊN — và 500 USD biến khỏi mẫu số

Đo ngày 28/08/2026 trên máy đang chạy: sổ đăng ký có **bốn tờ đứng
`DA_MO`**, mở từ 26/08, sổ cái ghi `CAP_VON` tổng **500 USD** cho đúng bốn
tờ ấy. Danh mục cùng lúc báo `soViThe: 0`, `daCamKetUsd: 0`,
`tiLeDungVon: 0`.

Cả hai đều đúng theo cách của mình, và đó mới là chỗ nguy:

    sổ đăng ký   nằm trên đĩa   → sống qua mọi lần khởi động lại
    danh mục     dựng trong RAM → `DanhMuc.__init__` đặt `viThe = {}`

Nên **mỗi lần khởi động lại là một lần vốn đã cam kết bốc hơi khỏi phép
tính trần**. Cùng họ với `von-ngoai-mu` nhưng ngược chiều: ở đó NAV thiếu
một phần nên trần rộng hơn sự thật; ở đây phần ĐÃ TIÊU bị quên nên tiền
rảnh rộng hơn sự thật. Trên NAV 1000 thì 500 bị quên là một nửa — và
không lỗi nào nổ, không dòng nhật ký nào báo, chỉ có một con số 0 trông
rất khoẻ.

Nó cũng không tự hết: trong cả hệ **không có đường nào chuyển sang
`DA_DONG`**. Vị thế mở ra thì ở lại `DA_MO` vĩnh viễn.

`doi_soat_vi_the.py` đo chỗ lệch ấy mỗi vòng, và xử lý theo **`moPhong`**:

| lớp thực thi | máy làm gì | vì sao |
|---|---|---|
| mô phỏng | ĐÓNG ở sổ, kèm `DONG_VI_THE` + `HOAN_VON` | vị thế chưa bao giờ tồn tại ngoài RAM; khởi động lại là nó biến mất **thật** |
| tiền thật | KHÔNG đóng gì, ngắt cầu dao `tuMo=False` | vị thế vẫn ở trên sàn sau khi runtime chết; tự đóng ở sổ là bịa ra một lần đóng chưa từng xảy ra |

Nhánh thứ hai chưa đi vào được từ mã thật (`DieuPhoiThucThi.moPhong` là
True cứng), nên phép kiểm dựng một lớp thực thi giả để đi vào nó — một
nhánh chỉ có văn xuôi bảo vệ là một nhánh chưa được bảo vệ.

Hai chi tiết đáng giữ:

- **Vốn đọc từ SỔ CÁI, không từ tờ trình.** `vonCanUsd` là vốn *xin*; Phân
  Bổ thường cấp ít hơn, và ở đây đã thật: bốn tờ xin 200 mỗi tờ, được cấp
  100·150·100·150. Lấy số xin thì thổi 500 thành 800.
- **Tờ không có `CAP_VON` nào thì vốn là `None`, không phải 0**, và một
  lỗ thì **cả tổng mù** — cùng luật với Router. Một tờ đứng `DA_MO` mà sổ
  cái không có dòng cấp vốn nào là chuyện đáng báo động hơn hẳn một tờ
  được cấp 0 đồng.

Cầu dao chỉ được nối vào **SAU** khi đã dọn: ngắt rồi gỡ ngay trong một
lượt khởi động thì `soLanNgat` cộng thêm một mỗi lần chạy lại, và chẩn
đoán `cau-dao-ngat-nhieu` (ngưỡng 5) sẽ kêu vì chính việc dọn dẹp thành
công.

    curl -X POST localhost:5188/api/doi-soat-vi-the

### Bảy việc một ty KHÔNG được làm

    ✗ giữ tiền, biết NAV, biết ty khác đang giữ gì
    ✗ tự đặt trần vốn cho mình          ✗ dựng Rủi Ro Tổng riêng
    ✗ gọi thẳng một ty khác             ✗ đặt lệnh
    ✗ ghi thẳng vào Sổ Cái              ✗ đóng/mở cầu dao

Bảy điều ấy thuộc Trung Ương, và không phải vì tập trung cho đẹp: mỗi điều
trong đó **cần nhìn thấy toàn bộ danh mục** — thứ mà theo định nghĩa không ty
nào nhìn thấy.

### Vì sao cấp vốn TUẦN TỰ, không song song

Hai tờ trình cùng chạm Binance. Xét riêng từng tờ trên danh mục hiện tại thì
cả hai đều lọt; cấp cả hai rồi cộng lại mới vượt trần cảng. Nên `phan_bo.py`
xếp hạng trước, rồi cấp từng tờ một và **gọi lại `rui_ro_tong.xet()` sau mỗi
lần cấp** trên danh mục đã cập nhật.

Cái giá là chậm hơn. Cái được là trần thật sự là trần.

### Vì sao Rủi Ro Tổng trả về một TRẦN

Trả nhị phân thì một cơ hội tốt xin $500 trong lúc chỉ còn chỗ cho $120 sẽ bị
vứt cả. Trả một trần thì nó được cấp $120, và `lyDoCat` nói rõ trần nào đã
chặn — người đọc cãi lại được.

### Cầu dao: ngắt tự động, đóng lại phải có NGƯỜI

Bất đối xứng có chủ ý. Máy phát hiện sự cố nhanh hơn người, nhưng máy không
phân biệt được *"sự cố đã qua"* với *"sự cố vẫn còn nhưng tín hiệu tạm im"* —
và cái thứ hai chính là lúc đóng lại thì mất tiền. Nên `dong_lai(ma, nguoi)`
không có mặc định cho `nguoi`.

Ngoại lệ duy nhất là những lý do đo được trực tiếp và không mơ hồ (đồng hồ đã
khớp lại): chúng khai `tuMo=True` và tự đóng. `sut-von` thì **không** — sụt
vốn là hậu quả, không phải tín hiệu; nó "hết" không có nghĩa là nguyên nhân
đã hết.

### Ngắt rồi thì vẫn quan sát

`mot_vong()` hỏi cầu dao **trước** khi phân bổ. Ngắt thì vẫn quét, vẫn ghi
nhận vào sổ đăng ký, vẫn chẩn đoán — chỉ không cam kết vốn. Dừng cả việc quan
sát là tự làm mình mù đúng lúc cần nhìn nhất.

### Cùng một cơ hội chỉ vào sổ MỘT lần mỗi giờ

Ty quét mỗi 30 giây; một chênh lệch funding sống hàng giờ. Không có cửa chống
trùng thì một cơ hội duy nhất vào sổ 120 lần mỗi giờ, và **cái phễu nói dối**:
mẫu số thành 86.400 "phát hiện" cho 30 cơ hội có thật, nên mọi tỉ lệ sống sót
đều chia cho một con số bịa. Xem `nhipGhiNhanGiay` và `_dau_van()`.

### Trung Ương chỉ ĐỀ XUẤT vặn tham số, không tự vặn

Khác hẳn vòng tiến hoá của ty. Ty tự vặn được vì nó **chạy lại băng** rồi đo
A/B trên cùng dữ liệu. Đổi tham số phân bổ thì không chạy lại được: muốn biết
một trần rộng hơn có tốt hơn không thì phải biết những cơ hội đã KHÔNG được
cấp diễn biến ra sao — mà chúng không được mở nên không có kết cục.

Không A/B được thì không tự nhận được. Người duyệt.

### Chạy lại quyết định PHÂN BỔ — và cái bẫy phải chặn trong thiết kế

`bac/chay_lai.py` chạy lại băng để đo funding THỰC NHẬN. `chay_lai_he.py`
chạy lại một thứ khác: **quyết định phân bổ**, trên chính những tờ trình Sổ
Đăng Ký đã lưu.

Nó **không** đo được lãi lỗ, và không giả vờ đo được — cơ hội bị từ chối thì
không được mở, nên nó không có kết cục. Cái nó đo là hình dạng phân bổ: rót
bao nhiêu, vào cơ hội tốt đến đâu (NET/giờ bình quân **theo vốn**, không
theo đầu cơ hội), dồn vào một cảng bao nhiêu, trần nào chặn nhiều nhất.

Nhờ đó `hoc()` không còn đưa ra đề xuất trần. Mỗi đề xuất kèm một phép đo
A/B trên dữ liệu thật.

Cái bẫy nằm ở chỗ chấm điểm: **nới hết mọi trần thì luôn rót được nhiều vốn
hơn và NET/giờ bình quân gần như luôn đẹp hơn.** Chấm điểm chỉ bằng hai con
số ấy là dạy vòng tiến hoá đúng một bài — tự tháo phanh. Nên `doi_chieu()`
từ chối tuyên bố người thắng khi B hơn mà độ tập trung cũng cao hơn; nó nói
thẳng *"đây là đổi rủi ro lấy lợi suất"* và để người quyết.

Và tập trung phải so bằng **tỉ trọng vốn đã rót**, không bằng USD tuyệt đối.
Bản đầu so USD, nên trong một hệ chỉ có MỘT ty thì rót thêm đồng nào cũng
làm `dayNhatTyUsd` tăng, và mọi bộ tham số rót nhiều hơn đều bị chấm là
"đậm hơn" — cái thước ấy không phân biệt được *rót nhiều* với *dồn một chỗ*.
Phép kiểm bắt được chuyện đó, không phải người đọc lại bắt được.

### Câu hỏi thành/bại của cả lớp trừu tượng này

> *Hai chiến lược hoàn toàn khác nhau có sống dưới cùng một Thị Bạc Ty không?*

`scripts/selftest.py` trả lời bằng một ty **cho vay** giả — không funding,
không mốc kết toán, không hai chân perp — chạy song song với ty phái sinh
thật, dưới cùng một Trung Ương, **không sửa một dòng nào trong `thi_bac_ty/`**.
Cả hai cùng vào sổ đăng ký, cùng bị `rui_ro_tong` xét, cùng được xếp hạng bằng
`netMoiGioBps`, và danh mục cộng phơi nhiễm chéo hai ngành.

Ngày phép kiểm ấy phải sửa `thi_bac_ty/` mới chạy được là ngày lớp trừu tượng
này hoá ra là giả.

## Xếp hạng bằng ĐÔ-LA MỖI GIỜ, không bằng phần trăm

Đây là chỗ bản đầu làm sai, và nó sai đúng theo cách bản đồ cảnh báo:

    DEX arb    lãi 0,40%    nhưng chỉ rót nổi $80
    Lending    lãi 7%/năm   nhưng rót được $100.000

Xếp theo phần trăm thì DEX thắng tuyệt đối. Nhân thêm một *hệ số* sức chứa
cũng không cứu — hệ số chỉ làm DEX thắng ít hơn, chứ vẫn thắng.

Nên `phan_bo.diem_chi_tiet()` tính:

    netMoiGioBps × rotDuocUsd     xấp xỉ đô-la mỗi giờ
    × tinCay                       ty tự chấm mình tin bao nhiêu
    × (1 − rủi ro)                 rủi ro không bù trừ, lấy mặt cao nhất
    × heSoKhoaVon                  khoá lâu là từ chối cơ hội khác

`rotDuocUsd` là chỗ chật nhất trong ba con số: ty xin bao nhiêu, thị trường
chứa bao nhiêu, và lúc này còn cho rót bao nhiêu. Hệ quả đúng như phải thế:
khi trần khả dụng nhỏ hơn cả hai, hai cơ hội quay về so bằng lợi suất — vì
lúc ấy sức chứa thừa không dùng tới được, và một thước tính công cho phần
thừa ấy là thước nói dối.

Hàm trả về CẢ NĂM thừa số chứ không chỉ con số cuối. Nhìn một con số trần
thì không ai biết cơ hội ấy thua vì rủi ro cao hay vì sức chứa mỏng.

## Khoá vốn và thanh khoản thoát — hai thứ `giuGio` không nói được

    giuGio               DỰ ĐỊNH giữ bao lâu
    khoaVonDenGiay       BUỘC phải giữ bao lâu
    thanhKhoanThoatUsd   RA được bao nhiêu

Một vị thế funding giữ 8 giờ nhưng thoát được bất cứ lúc nào. Một PT Pendle
90 ngày thì không có cách nào ra sớm, dù thị trường đã đổi. Vốn khoá 90 ngày
ở 10%/năm THUA vốn rút được ngay ở 7%/năm, vì trong 90 ngày ấy có thể xuất
hiện thứ tốt hơn mà ta không vào được — và chi phí đó **không nằm trong APR
của chính nó**.

Rủi Ro Tổng vì thế có hai cửa mới:

- `khoaVonToiDaGiay` — quá trần thì **TỪ CHỐI**, không cắt bớt. Cắt trần
  không rút ngắn thời gian khoá; rót ít hơn vẫn kẹt đúng ngần ấy tháng.
- thanh khoản thoát **cắt trần** xuống đúng chỗ ra được. Vào được $100.000
  không có nghĩa là ra được $100.000, và rót quá chỗ thoát được là tự dựng
  một vị thế mà chính mình không đóng nổi.

`0.0` khác `None`. 0 là "rút được ngay, đã kiểm"; None là "chưa biết". Coi
None thành 0 là thưởng cho sự mù.

## Đổi tham số phải đi qua CỔNG DUYỆT, và tham số có SỐ HIỆU

Vòng nguy hiểm mà cả chương này tồn tại để chặn:

    kết quả thị trường → AI phân tích → AI sửa tham số → chạy tiền thật

Vòng ấy hỏng không phải vì AI dở, mà vì nó không có chỗ nào để sai một cách
**nhìn thấy được**. Mỗi lượt tự vặn đều có vẻ hợp lý, và sau ba mươi lượt
thì tham số đã trôi rất xa mà không lượt nào là lượt sai rõ ràng.

Đường đúng, và nay đã đủ tám mắt:

    RESULT → DIAGNOSIS → PROPOSAL → OFFLINE TEST/REPLAY
           → ACCEPTANCE GATE → VERSIONED PARAMETER → LIVE

| mắt | ở đâu |
|---|---|
| RESULT | `so_cai.py` |
| DIAGNOSIS | `chan_doan_he.chan_doan_he()` |
| PROPOSAL | `chan_doan_he.de_xuat()` — nhiều nhất MỘT núm mỗi lượt |
| OFFLINE TEST | `chay_lai_he.doi_chieu()` trên tờ trình đã ghi |
| ACCEPTANCE GATE | `cong_duyet.xet_duyet()` — bảy luật |
| VERSIONED PARAMETER | `ban_tham_so.KhoThamSo` — chỉ thêm, quay lui được |
| LIVE | `trung_uong.ap_dung(nguoi)` — **đòi tên người** |

### Bảy luật của Cổng Duyệt

1. Không đo thì không duyệt — đề xuất không kèm phép chạy lại là một ý kiến.
2. Chưa đủ mẫu thì không duyệt.
3. Không núm nào chạm cửa AN TOÀN — kiểm lại từ danh sách gốc, **không tin**
   lớp lọc ở `chan_doan_he`.
4. Bước không vượt trần 25%.
5. Không ra ngoài khuôn `[min, max]`.
6. **Hoà thì không duyệt.** Đứng yên là kết quả hợp lệ.
7. **Tốt hơn nhờ ôm rủi ro đậm hơn thì không duyệt.** Luật quan trọng nhất:
   nới hết mọi trần thì luôn rót được nhiều vốn hơn, nên nhận nhánh này là
   dạy vòng tiến hoá rằng đường lên điểm là tự tháo phanh.

Qua cổng **KHÔNG** phải là đã áp dụng. Máy đo, máy đề xuất, máy chặn — máy
không tự ký. `ap_dung()` và `quay_lui()` đều đòi tên người, cùng luật với
`cau_dao.dong_lai()`.

Bản mới ghi kèm CHÍNH phép đo đã biện minh cho nó. Ba tháng sau, câu *"vì
sao trần cảng là 0,45"* trả lời được bằng một lệnh đọc sổ, không phải bằng
trí nhớ. Và quay lui không xoá bản sai — nó ghi một bản MỚI mang nội dung
bản cũ, cùng luật với `so_cai.dao()`.

## Ba tầng là ĐỘ NẶNG THỰC THI, không phải thang rủi ro

Bản đồ chia:

    LEVEL 1  Capital Yield    lending · PT · LP · staking
    LEVEL 2  Market Alpha     funding · basis · prediction
    LEVEL 3  Machine Alpha    MM · JIT · liquidation · MEV

Cách chia này hữu ích, nhưng **đừng đọc thành** `Level 1 = an toàn`. Lending
có thể dính exploit hợp đồng, oracle hỏng, depeg, nợ xấu. LP có tổn thất tạm
thời và dòng lệnh độc. Pendle có rủi ro kỳ hạn và rủi ro giao thức.

Thứ thang này thật sự đo là **độ nặng thực thi** — cần bao nhiêu hạ tầng, độ
trễ và cạnh tranh máy-với-máy. Thị Bạc Ty hiện ở tầng 2.

## NỢ KIẾN TRÚC ĐÃ BIẾT: hiện có HAI cỗ máy, không phải một

Đây là chỗ lệch lớn nhất so với bản đồ, và ghi ra đây để nó không tự biến
mất khỏi trí nhớ ai.

Bản đồ nói: Polymarket là **một engine** trong nhà máy, nộp cơ hội vào cùng
một Opportunity Bus, chịu cùng một Risk Engine và cùng một Capital
Allocator. Câu nguyên văn: *"tôi sẽ không xây 14 bot riêng biệt"*.

Thực tế trong kho lúc này:

    kham-thien-giam-runtime/kham/     ← cỗ máy ĐẦY ĐỦ, độc lập
        rui_ro.py · chan_rui_ro.py        rủi ro riêng
        ket_toan.py · so.py               sổ cái riêng
        vi.py · dat_lenh.py               ví riêng, LỚP ĐẶT LỆNH riêng
        bus.py · chan_doan.py             bus riêng, chẩn đoán riêng
        chay_lai.py · tien_hoa.py         chạy lại riêng, tiến hoá riêng

    thi-bac-ty-runtime/thi_bac_ty/    ← Trung Ương, KHÔNG biết cỗ máy kia
    thi-bac-ty-runtime/bac/           ← ty đầu tiên

`kham/` **không** import `thi_bac_ty`, và Trung Ương **không** biết
Polymarket tồn tại. Hai bộ máy chạy song song, mỗi bộ tự quản vốn của mình.

### Vì sao thế, và vì sao chưa sửa

Khâm Thiên Giám xây **trước** khi Thị Bạc Ty tồn tại. Bản đồ có luật riêng
cho đúng tình huống này: *"không bảo Claude chuyển toàn bộ repo sang kiến
trúc mới — làm vậy rất dễ phá thứ đang chạy"*. Nên viết lại nó bây giờ là
vi phạm chính luật đã cứu `bac/` khỏi bị viết lại.

### Nhưng phải nói rõ cái giá, vì nó KHÔNG bằng 0

Khâm Thiên Giám có `dat_lenh.py` và `vi.py`. Bốn cửa của nó mặc định đều
đóng, nên hôm nay không đồng nào chuyển. Nhưng ngày ai đó mở bốn cửa ấy,
sẽ có **tiền thật đi qua một cỗ máy mà Rủi Ro Tổng không nhìn thấy** — và
Rủi Ro Tổng tồn tại đúng để trả lời câu "cho tiền vào đây thì DANH MỤC ra
sao". Nó không trả lời được cho phần nó không thấy.

Hệ quả cụ thể: `tranMotCang`, `tranMotChuoi`, `sutVonToiDaPct` của Trung
Ương chỉ đúng trên phần vốn Thị Bạc Ty quản. Đừng đọc chúng như trần của
cả gia sản.

### TÌNH TRẠNG ngày 27/08/2026 — hai bước đã gỡ, một bước bị CHẶN

    1. Đừng dựng cỗ máy thứ ba                        ĐANG GIỮ
    2. Adapter `Ty` cho `kham/`                       XONG — `kham_ngoai/`
    3. `vi.py` vào Danh Mục                           XONG — `von_ngoai.py`
       `ket_toan.py` sang Sổ Cái                      XONG — `nhap_so_ngoai.py`
    4. `dat_lenh.py` chuyển sau cùng                  CHẶN — xem dưới

**Bước 2 xong**, và ranh giới đếm là phần khó nhất của nó:

    dangLam = True   cỗ máy kia đã lấy → `von_ngoai` đếm → adapter BỎ QUA
    dangLam = False  nó chỉ mới thấy   → adapter nộp tờ trình

Nộp cả hai là đếm CÙNG MỘT vị thế hai lần — một lần là vốn ngoài, một lần
là vốn Thị Bạc Ty vừa cấp — và `tranMotCang` khi ấy tưởng mình chặn ở 30%
trong khi thực tế là 60%. Điều `khong-dem-hai-lan` trong hiến pháp giữ ranh
giới ấy, và phép cấy lỗi ngược làm nó đỏ.

Adapter đọc qua HTTP, **không import `kham`** — hai runtime là hai tiến
trình, hai vòng đời. Cỗ máy kia tắt thì ty khai là mù chứ không báo "không
có cơ hội"; hai câu ấy trông giống hệt nhau nếu không ai nói ra.

Kèm theo bước 2, họ thứ TÁM ra đời: `tien-doan`. Thị trường tiên đoán
không nhét vừa bảy họ cũ — không có tài sản cơ sở để phái sinh từ đó, cũng
không có hai nơi để so giá. Nhét bừa vào `chenh-lech` cho khỏi sửa hợp đồng
thì `_pheu_theo_ho()` gộp nó với chênh lệch stablecoin, và cái phễu ấy nói
dối về cả hai.

**Bước 3 xong, và hoá ra không phải sửa file cung khác chút nào** —
`ketToan` đã có sẵn trong `/api/trang-thai`.

Chuyển `ket_toan.py` theo nghĩa đen thì không làm được: hai runtime là hai
tiến trình, và bắt cỗ máy kia ghi thẳng vào SQLite của Thị Bạc Ty là buộc
chúng thành một. Nhưng **mục đích** đạt được — một sổ của sự thật — bằng
cách ĐỌC rồi ghi, y hệt lối `von_ngoai.py` đọc ví.

Chia việc: `von_ngoai` giữ phần **TIỀN** (phơi nhiễm chỉ-đọc trong Danh
Mục), `nhap_so_ngoai` giữ phần **SỰ KIỆN** (bút toán kết toán).

Hai chuyện phải đúng, và cái thứ hai mới khó:

1. **Không đếm hai lần.** Bên kia đưa cùng một bản ghi ở mọi lượt hỏi. Ghi
   lại mỗi lượt là nhân lãi lỗ lên gấp số lượt hỏi. Khoá ổn định
   `<nguồn>:<slug>:<luc>`.
2. **Bỏ sót phải TỰ LỘ RA.** `/api/trang-thai` chỉ đưa **12 bản ghi gần
   nhất**. Kết toán hơn 12 lần giữa hai lượt hỏi thì phần giữa mất hẳn, và
   mất trong im lặng — sổ vẫn cân, vẫn không lỗi, chỉ thiếu tiền. Nên sổ
   nhập theo dõi `daKetToan` của bên kia và đếm phần rơi vào `soBoSot`.
   Bên kia không công bố tổng số thì `boSotDoDuoc=False`: *"không thiếu"*
   và *"không biết có thiếu không"* phải nói khác nhau.

Cột tiền để **0** có chủ ý — bên kia công bố KẾT QUẢ chứ không công bố lãi
lỗ từng lần, và ghi một con số bịa vào cột tiền là làm hỏng đúng thứ sổ cái
sinh ra để giữ.

**Bước 4 bị CHẶN, và chặn có chủ ý.** `dat_lenh.py` chỉ chuyển được khi
Điều Phối Thực Thi có lớp ký lệnh thật. Lớp ấy không tồn tại và không được
phép tồn tại: `DieuPhoiThucThi.moPhong` là `True` cứng, không cấu hình nào
mở được. Nên bước 4 không phải "chưa làm" — nó là **"không làm được từ phía
này"**, và hai câu ấy phải nói khác nhau.

### Việc phải làm, theo thứ tự, khi quay lại chỗ này

1. **Đừng dựng cỗ máy thứ ba.** Ty tiếp theo cắm vào `khuon_ty.Ty`, không
   dựng runtime riêng. Đây là điều quan trọng nhất trong cả mục này.
2. Cho `kham/` một adapter `Ty` — quét và trình lên Thông Chính, giữ nguyên
   phần định giá của nó. Đúng lối `bac/ty_perp.py` đã đi: chỗ nối mỏng,
   không viết lại thuật toán.
3. Chuyển `ket_toan.py` sang `thi_bac_ty/so_cai.py`, và `vi.py` vào Danh
   Mục. Làm bước này TRƯỚC khi mở bất kỳ cửa đặt lệnh nào.
4. `dat_lenh.py` là lớp cuối cùng chuyển, và chỉ khi Điều Phối Thực Thi có
   lớp ký lệnh thật.

## Ty thứ hai: TÍN DỤNG — và nó đã chứng minh kiến trúc

`tin_dung/` là engine #2, và mục đích của nó không phải kiếm tiền: nó là
**phép thử**. Perpetual là phái sinh, hai chân trên hai sàn, thu tại mốc
kết toán. Lending là tín dụng, một chân, lãi chảy liên tục, không mốc nào.

Chạy thật ngày 26/08/2026, hai ty dưới một Thị Bạc Ty:

    họ            thô  cổng ty  RR tổng  cấp vốn   đang giữ
    phai-sinh      30        0        0        0    $0.00
    tin-dung       90        3        3        3  $600.00

    cảng : {aave-v3: 600}                     ← gộp theo GIAO THỨC
    chuỗi: {Polygon: 200, Base: 200, Arbitrum: 200}   ← tách theo CHUỖI

Danh Mục cộng phơi nhiễm chéo hai ngành mà không ai phải dạy nó, vì cả hai
ty chỉ nói bằng `ToTrinh`.

### Ba lỗi ty thứ hai làm lộ ra, và hai trong ba nằm ở TRUNG ƯƠNG

**1. Vân tay cơ hội bỏ sót CHUỖI.** `_dau_van()` lấy `bên@cảng`. Với bốn
sàn perp thì không sao — mỗi sàn một cảng. Nhưng `aave-v3 USDC trên
Ethereum` và `aave-v3 USDC trên Polygon` cùng một vân tay, nên cái thứ hai
bị bỏ **trong im lặng** như một bản trùng. Ba tờ trình nộp lên, một tờ vào
sổ, và không gì báo.

**2. `dang_ky()` soi LỚP thay vì THỰC THỂ.** `type(ty).kiem_khai()` khiến
một ty được bọc — chẳng hạn để cho nó nhịp quét riêng — bị từ chối vì một
lý do chẳng liên quan gì tới nó. Nay hỏi `ty.kiem_khai()`: Trung Ương quan
tâm ty **trả lời được gì**, không quan tâm nó thuộc lớp nào.

**3. `asyncio.run()` từ trong vòng lặp.** `Ty.quet()` đồng bộ theo hợp
đồng, nhưng `Runtime.mot_vong()` là `async`. Đáng nói là hệ thống chịu
được: cổng chặn ngoại lệ trong `mot_luot()` giữ ty này không kéo theo ty
kia, và `loiCuoi` nói ra chính xác chuyện gì hỏng.

Không lỗi nào tìm ra được bằng cách đọc lại mã. Cả ba cần một ty thứ hai
**thật**, khác ngành, cắm vào và chạy.

### Ba lỗi hiệu chỉnh của chính ty tín dụng

- **Rủi ro giao thức suy từ TVL của POOL.** Một lỗi trong Aave v3 ảnh
  hưởng MỌI thị trường Aave v3 — nên rủi ro hợp đồng là của giao thức, và
  phải cộng TVL toàn giao thức.
- **Thang TVL bão hoà.** `sqrt(50M/TVL)` chặn trên 1,0 cho ra đúng 1,00 với
  mọi thứ dưới $50M; vì `rui_ro_tong` lấy MAX, cửa TVL vô tình thành "chỉ
  nhận giao thức trên $50M" — một luật không ai khai.
- **Rủi ro thanh khoản = dùng vốn, tuyến tính.** Dùng vốn 80% ở một thị
  trường cho vay là LÀNH MẠNH; nó chính là thứ sinh ra lãi. Chấm 0,80 là
  loại sạch mọi thị trường đang hoạt động và chỉ nhận thị trường không ai
  vay — tức là thị trường không trả lãi.

### Chỗ dễ tự lừa nhất của ty này: gas là chi phí CỐ ĐỊNH

    $200 gửi Ethereum, gas vào+ra $12 → 600 bps → ở 4%/năm phải giữ 5 THÁNG
    $50.000 cùng thị trường ấy      → 2,4 bps  → hoà sau nửa ngày

Cùng một APY, hai cỡ vốn, hai kết luận ngược nhau. Nên mỗi cơ hội mang
theo `hoaVonSauGio`, và token thưởng **không** vào NET — tính nó vào là
cách nhanh nhất để bảng xếp hạng bị chiếm bởi những thị trường đang mua
thanh khoản bằng token của chính mình.

## Vốn NGOÀI: thấy được, không quản được

Bước đầu tiên và rẻ nhất để gỡ món nợ hai-cỗ-máy: **thấy trước, quản sau.**

`thi_bac_ty/von_ngoai.py` đọc một runtime khác qua HTTP — chỉ đọc, không
đặt lệnh, không import. Vốn ngoài vào **NAV** nhưng không vào `viThe`: Thị
Bạc Ty không mở nó và không đóng được nó, nên không được giả vờ ngược lại.

Vì sao phải vào NAV: mọi trần của Rủi Ro Tổng tính theo NAV, và một NAV
thiếu phần vốn đang phơi ra ở nơi khác là NAV nói dối **theo hướng nguy
hiểm** — trần rộng hơn sự thật.

Không đọc được thì `von-ngoai-mu` **ngắt cầu dao**, vì đó là "ta không còn
chắc mình đang nhìn đúng thế giới" ở dạng thuần khiết nhất. Lý do này tự
mở lại — đọc lại là biết ngay.

Mặc định `vonNgoai: {}` (tắt), vì bật lên mà cỗ máy kia không chạy thì cầu
dao ngắt vĩnh viễn. **Luật phải giữ: trước khi mở bất kỳ cửa đặt lệnh nào
của Khâm Thiên Giám, BẬT khoá này lên.** Xem `bac/config.py`.

Đây là bước 1 trong bốn bước gỡ nợ. Ba bước còn lại — adapter `Ty` cho
`kham/`, chuyển `ket_toan.py` sang Sổ Cái, chuyển `dat_lenh.py` — vẫn chưa
làm, và vẫn theo đúng thứ tự ấy.

## CHÍN ty, NĂM họ — và ba engine còn chặn

    ho            ty                ma
    phai-sinh     bac/              perpetual.funding_spread.v1
    phai-sinh     co_so/            basis.cash_carry.v1
    phai-sinh     quyen_chon/       options.put_call_parity.v1
    tin-dung      tin_dung/         lending.rate_rotation.v1
    tin-dung      lai_suat/         yield.pendle_pt.v1
    chenh-lech    on_dinh/          stablecoin.cross_venue.v1
    chenh-lech    dex_arb/          dex.round_trip.v1
    thanh-khoan   lp_amm/           amm.fee_farming.v1
    tien-doan     kham_ngoai/       prediction.polymarket.v1

Năm nguồn alpha khác hẳn nhau, và bản đồ nói đúng lúc có nhiều loại việc
khác hẳn nhau thì Người Phân Bổ Vốn mới thật sự có việc — trước đó nó chỉ
đang xếp hạng những thứ giống nhau.

Ba họ còn trống: `thanh-ly`, `mev`, `cau-noi`. Hai họ đầu chặn vì dữ liệu
không công khai; `cau-noi` thì cố ý — Router là **hạ tầng**, không phải ty,
và nó không xin vốn.

Chú ý `quyen_chon/` và `dex_arb/`: chúng là hai engine đầu tiên **không dự
báo gì cả**. Ngang giá là một đẳng thức; vòng đổi là một phép đo khứ hồi.
Bảy ty còn lại đều phải giả định một thứ sẽ giữ nguyên.

### Ty lãi suất là ty đầu tiên dùng `khoaVonDenGiay` với số THẬT

PT Pendle trả lãi cố định tới ngày đáo hạn. Ngày ấy đọc được từ `poolMeta`
(`"For buying PT-sUSDe-22OCT2026"`), nên `khoaVonDenGiay` là một con số đo
được chứ không phải một trường để trống.

Hệ quả thấy ngay khi chạy thật, và nó ĐÚNG: mọi PT đáo hạn sau 30 ngày đều
bị `rui_ro_tong.khoaVonToiDaGiay` **TỪ CHỐI** — 12 tờ trình, mỗi tờ một
dòng "khoá vốn 2193 giờ > trần 720 giờ". Không phải vì 8%/năm là xấu, mà vì
khoá vốn 91 ngày là từ chối mọi cơ hội tốt hơn xuất hiện trong 91 ngày ấy,
và chi phí đó **không nằm trong con số 8%**.

Người vận hành thấy đúng đánh đổi ấy và tự quyết có nới trần không. Đó là
việc của người, không phải của máy.

**PT chứ không phải LP.** DefiLlama trả cả hai dạng cho mỗi thị trường
Pendle; LP có tổn thất tạm thời và hệ toán khác hẳn (đó là thread #8). Lẫn
hai thứ là bịa ra một con số không mô tả cái nào.

### Ty chênh lệch: `$0,97` KHÔNG phải arbitrage

Cửa quan trọng nhất của ty ấy là `lechNeoToiDaBps`. Chênh lệch càng lớn thì
càng có khả năng đây không phải sai giá tạm thời mà là thị trường đang định
giá lại rủi ro của chính đồng tiền ấy — và bên đứng ra "ăn chênh lệch" sẽ
là bên ôm đồng đang chết.

Cửa thứ hai đáng nói: **thời gian giao dịch ≠ chu kỳ vốn**. Lệnh xong trong
vài giây, nhưng sau một lượt tồn kho lệch — sàn rẻ hết USDT, sàn đắt đầy
USDC — và muốn làm lượt nữa phải chờ chênh lệch đảo chiều hoặc chuyển vốn
giữa hai sàn, mà runtime này chưa chuyển được. Khai `giuGio` bằng vài giây
là cho NET mỗi giờ nhảy lên hàng nghìn bps và chiếm sạch bảng xếp hạng
bằng một con số mình không đạt được.

### `chuoi_chung/` — hạ tầng của một HỌ, không phải của Trung Ương

    thi_bac_ty/     TRUNG ƯƠNG — không biết "TVL" hay "dùng vốn" là gì
    chuoi_chung/    hạ tầng cho ty ĐỌC CHUỖI — biết TVL, không biết chiến lược
    tin_dung/ · lai_suat/ · on_dinh/ · bac/    các ty

Khi ty đọc-chuỗi thứ hai xuất hiện, hai lựa chọn đều sai: chép thang rủi ro
sang (hai bản sao sẽ lệch nhau đúng vào ngày ai đó hiệu chỉnh một bản), hay
để ty mới import ty cũ (điều luật chung cấm). Chỗ thứ ba mới đúng, và bản
đồ đã vẽ sẵn nó: **SHARED INFRASTRUCTURE**.

## HIẾN PHÁP — luật vận hành, viết dưới dạng CHẠY ĐƯỢC

`thi_bac_ty/hien_phap.py` giữ **31 điều** luật vận hành của cả bộ máy. Mỗi
điều mang bốn thứ: câu luật, **chuyện đã xảy ra dạy ra nó**, nguồn, và một
phép canh.

### Vì sao không phải một tệp nguyên tắc

Kho này đã tự chứng minh rằng nguyên tắc nằm trong văn xuôi thì không giữ
được gì. `bac/rui_ro.py` từng khai ba cửa mà `xet()` không hề đọc tới, và
buồng lái bày chúng dưới nhãn *"đang có hiệu lực"* suốt nhiều tuần. Không ai
nói dối — luật ở một chỗ, mã ở chỗ khác, và hai chỗ ấy trôi xa nhau mà không
gì báo.

Đúng dạng ấy lặp lại **bốn lần** chỉ trong một phiên: docstring cầu dao khai
"ba trong mười" trong khi mã nối bốn; `trung_uong` khai "không nhảy cóc"
trong khi `_hop_le` cho nhảy cóc; lớp bọc che `kiem_khai` rồi che tiếp
`vonToiThieuKinhTeUsd` của ty thật.

Nguyên tắc chỉ nằm trong văn xuôi **chính là** kiểu hỏng mà cả runtime này
sinh ra để bắt: hệ thống nói về chính mình một điều không đúng.

### Điều KHÔNG canh được phải KHAI RA là không canh được

Đây là phần quan trọng nhất, và là thứ một tệp nguyên tắc không làm được.

Một hiến pháp mà điều nào cũng trông như đang có hiệu lực thì **tệ hơn không
có**: người đọc tưởng mình được che ba mươi mốt điều trong khi thật ra
được che hai mươi lăm. `soat()` tách rõ hai nhóm và in cả
`soKhongCanhDuoc`.

    31 điều · canh được 25 · KHÔNG canh được 6 · vi phạm 0

Sáu điều không canh được phần lớn là **quan điểm đánh giá**, không phải bất
biến cơ học: *"đừng đo bộ máy bằng số đô ở giai đoạn vốn nhỏ"*, *"từ chối
giỏi quan trọng hơn phát hiện nhiều"*, *"basis không phải thu nhập"*. Không
hàm nào canh được chúng, và giả vờ canh được sẽ tệ hơn. Ba điều còn lại
(`von-ngoai-bat-san`, `khong-dem-hai-lan`, `bi-danh-khong-phai-ban-sao`) cần
`thi_bac_ty/` nạp một ty để canh — mà điều `trung-uong-khong-biet-ty` cấm
đúng chuyện đó, nên chúng được canh ở tầng dưới, trong `scripts/selftest.py`.

### Viết hiến pháp lộ ra tám luật chưa ai canh

Lần đầu chạy: 14 canh được, **11 không**. Soi lại thì tám trong mười một là
canh được — chỉ là chưa ai canh **trên toàn hệ**. Ví dụ hợp đồng `CUA`: từng
ty có phép kiểm riêng, nhưng không gì bảo đảm ty THỨ NĂM cũng giữ nó, cho
tới khi nó bày ra một cửa giả.

Và hai phép canh đầu của tôi **yếu**: một cái đọc chuỗi trong mã nguồn nên
vẫn xanh khi câu `if` đã bị vô hiệu; một cái chỉ chạy một vòng nên không
chạm tới kiểu thoái hoá thật *"cầu dao đang ngắt thì thôi quét cho đỡ tốn"*.
Cấy chín lỗi ngược vào bắt được cả chín — sau khi sửa hai phép canh ấy.

### Xem nó

    curl -s localhost:5188/api/hien-phap              tóm tắt
    curl -s 'localhost:5188/api/hien-phap?day_du=true' đủ, kèm VÌ SAO từng điều

Buồng lái hiện ô hiến pháp ở đầu tab Thị Bạc Ty, và một vi phạm làm nó đỏ.
`scripts/selftest.py` cũng chạy `soat()`, nên vi phạm làm build đỏ.

## $100 chạy được CẢ HỆ, nhưng không engine nào bị ép vào lệnh

Tách hai thứ mà người ta hay gộp:

    PHẦN MỀM ĐANG CHẠY   ≠   VỐN ĐANG LÀM VIỆC

Bốn engine quét 24/7 bất kể vốn bao nhiêu. Vốn chỉ quyết ở đúng một chỗ —
chỗ cấp. Chia $100 cho bốn engine là mỗi cái $25, và ở $25 thì phí, gas, cỡ
lệnh tối thiểu ăn sạch: bốn engine cùng lỗ thay vì một engine có lãi.

### Mỗi engine tự khai ngưỡng kinh tế của CHÍNH NÓ

`Ty.vonToiThieuKinhTeUsd` là **bắt buộc** — ty nào không khai thì chết ở cửa
đăng ký. Một ty không biết ngưỡng của chính nó sẽ đều đặn trình lên những cơ
hội mà phí ăn sạch, để trung ương loại hộ; chuyển việc ấy sang trung ương là
bắt trung ương biết chi phí của từng ngành, thứ nó không biết và không nên
biết.

| engine | ngưỡng | vì sao chính con số ấy |
|---|---|---|
| `perpetual.funding_spread` | $100 | hai chân, mỗi chân phải qua cỡ lệnh tối thiểu của sàn — một chân bị từ chối là vị thế MỘT CHIỀU |
| `stablecoin.cross_venue` | $200 | edge vài bps, nhạy phí nhất; cỡ vốn cứu được phần vụn, không cứu được phí tỉ lệ |
| `lending.rate_rotation` | $500 | gas là chi phí CỐ ĐỊNH: $0,10 khứ hồi trên L2 là 2 bps ở $500 |
| `yield.pendle_pt` | $1.000 | mua PT là một lượt swap có TRƯỢT GIÁ, và vốn khoá tới đáo hạn |

Đây **không phải** `phanBo.toiThieuMotLanUsd`. Sàn ấy là của HỆ, chung cho
mọi ty; $25 đủ cho chênh lệch stablecoin mà không đủ cho cho vay.

### Ba chế độ, và máy KHÔNG được tự ép lên cao hơn

    QUAN_SAT   quét, trình, ghi sổ — nhưng KHÔNG BAO GIỜ được cấp vốn
    GIAY       được cấp trên SỔ GIẤY, đo như thật
    THAT       tiền thật — chưa với tới được, vì lớp ký lệnh chưa tồn tại

Chế độ suy tất định từ hai con số: `NAV × tranMotCoHoi` và ngưỡng của ty.
Chạy thật:

    NAV    $100  →  perp:QUAN_SAT  stable:QUAN_SAT  lending:QUAN_SAT  yield:QUAN_SAT
    NAV  $1.000  →  perp:GIAY      stable:QUAN_SAT  lending:QUAN_SAT  yield:QUAN_SAT
    NAV  $5.000  →  perp:GIAY      stable:GIAY      lending:GIAY      yield:QUAN_SAT
    NAV $20.000  →  perp:GIAY      stable:GIAY      lending:GIAY      yield:GIAY

    → cần NAV $667 để có ÍT NHẤT một engine chạy được bằng tiền

Ở $100, cả bốn engine QUAN SÁT: hệ chạy đủ, quét đủ, ghi sổ đủ — và không
đồng nào bị ép vào một cơ hội mà phí ăn hết.

### Cấp ĐỦ, hoặc KHÔNG CẤP

`rui_ro_tong` cắt trần xuống dưới ngưỡng kinh tế thì **từ chối**, không cấp
nửa vời. Cấp $150 cho một engine cần $1.000 là tệ hơn không cấp: vốn bị giữ
chỗ, một slot vị thế bị tiêu, và lãi không bù nổi phí cố định — ta trả tiền
để học một điều đã biết trước.

Và hợp đồng chặn một mâu thuẫn nữa: **ty xin ít hơn ngưỡng nó tự khai** là
tờ trình tự mâu thuẫn. Ty phải hoặc xin đủ, hoặc hạ ngưỡng nó khai.

## Hiệu năng đo bằng đường NAV, không bằng một APR nhân thẳng

Vốn thật đi qua `100 × 1,12 × 1,31 × 0,92 × 1,22 × 1,05`, chứ không phải
`100 × 1,5^5`. Một năm âm ở giữa không chỉ làm chậm — nó ăn vào cái nền mà
mọi năm sau nhân lên từ đó.

    CAGR                 lợi suất gộp thật, không phải trung bình cộng
    SỤT VỐN TỐI ĐA       đáy sâu nhất tính từ ĐỈNH TRƯỚC ĐÓ, không từ vốn gốc
    THỜI GIAN DƯỚI ĐÁY   bao lâu chưa về lại đỉnh cũ

Hai con số sau quyết định người ta có giữ nổi hệ thống qua một đợt xấu hay
không, và không APR nào nói được chúng.

Dưới bảy ngày dữ liệu, mọi trường tỉ suất trả `None` — quy 0,3% của nửa
ngày ra năm cho một con số vô nghĩa mà trông rất thuyết phục.

### Chi phí hạ tầng là đối thủ THẬT của vốn nhỏ

    VPS + RPC + API  ~$10/tháng  =  $120/năm
    $100 vốn kiếm 20%/năm        =  $20        → vẫn ÂM

    vốn cần để hoà hạ tầng:  10% → $1.200 · 20% → $600 · 50% → $240

Nên ở giai đoạn này, đánh giá bộ máy bằng số đô kiếm được là đánh giá sai
thứ. Cái đáng đo là **chất lượng quyết định**, và `+$10` có thể là kết quả
rất đáng giá nếu nó chứng minh được một engine có kỳ vọng dương.

### Đối chiếu giấy ↔ thật: chỗ đã có sẵn, số thì chưa

Nếu sổ giấy ra +18% mà tiền thật ra +2% thì mô phỏng đang nói dối, và biết
được điều ấy đáng giá hơn cả hai con số. Nhưng bản này **chưa có lệnh thật
nào** — `thuc_thi.moPhong` là True cứng. Nên `doi_chieu_giay_that()` trả về
*"chưa đối chiếu được"* kèm lý do, chứ không trả một con số 0 giả vờ là kết
quả. Chỗ ấy có sẵn cho ngày lớp ký lệnh tới.

## SÁU ENGINE CÒN LẠI — ba đã dựng, ba còn chặn

Đây là mục quan trọng nhất của cả chương, vì thứ dễ làm nhất lúc này là
dựng sáu scanner nữa cho có đủ mười ba, rồi gọi đó là xong.

Sáu engine dưới đây **không thiếu công sức, chúng thiếu hạ tầng**. Dựng
scanner cho một thứ không thực thi được là sinh ra những con số không ai
hành động được — đúng định nghĩa hệ thống rác.

| engine | thứ kho này KHÔNG có |
|---|---|
| DEX Arbitrage | RPC, pool state, gas oracle, transaction simulator |
| Automated LP / Uniswap v4 | pool state, mô hình tổn thất tạm thời, deploy hook |
| Liquidation | RPC hoặc subgraph theo TỪNG vị thế, flash liquidity |
| Options / Volatility | Deribit, mặt IV, máy delta-hedging |
| JIT Market Making | kết nối orderbook độ trễ thấp, quyền vào JIT auction |
| MEV | mempool, quan hệ builder/relay, đóng bundle |

Bốn ty đang chạy đều đọc **HTTP công khai, không khoá, không ví**. Sáu cái
trên đòi một lớp hạ tầng khác hẳn: nút chuỗi, khoá ký, và với ba cái cuối
là cả độ trễ tính bằng mili giây.

### CẬP NHẬT 27/08/2026 — bảng trên đã SAI, và cách nó sai mới là bài học

Bảng ấy đúng lúc viết. Rồi Router ra đời cùng ngày, mang theo báo giá swap
LI.FI và gas RPC bốn chuỗi — và **hai trong sáu dòng thôi bị chặn**. Không
ai sửa bảng, vì bảng là văn xuôi, và văn xuôi hỏng theo đúng một cách: thế
giới đổi mà câu văn không đổi.

Nên sổ đăng ký nay **chạy được**: `dong_co_chua_co/so_dang_ky.py`. Mỗi
engine mang điều kiện chặn của chính nó dưới dạng hàm canh, và một lượt
chạy nói ra trạng thái thật:

    node                     trạng thái   ghi chú
    quyen-chon               DA_DUNG      `quyen_chon/ty_ngang_gia.py`
    dex-arb                  DA_DUNG      `dex_arb/ty_vong_doi.py`
    lp-v3                    DA_DUNG      `lp_amm/ty_cap_thanh_khoan.py`
    thanh-ly                 CHAN         health factor từng khoản vay
    jit                      CHAN         mempool · quan hệ builder
    mev                      CHAN         mempool · builder · độ trễ

**Không còn engine nào ở `QUET_DUOC`** — mọi engine quét được đã được dựng.
Ba engine còn chặn đều chặn vì cùng một loại lý do: chúng cần dữ liệu KHÔNG
công khai (mempool) hoặc dữ liệu mức từng-khoản-vay mà không nguồn miễn phí
nào cho. Đó không phải việc chưa làm; đó là việc không làm được từ đây.

Sổ TỰ biết trạng thái ĐÃ DỰNG bằng cách nạp thử gói ty. Dòng ở lại kèm
lịch sử chứ không bị xoá — xoá tay thì mất luôn câu "nó từng bị chặn vì gì,
và cái gì gỡ ra".

Đọc lượt chạy mới nhất: `curl -s localhost:5188/api/dong-co-chua-co?day_du=true`

**Ba trạng thái, và phân biệt chúng mới là điểm.** `QUET_DUOC` nghĩa là
quét được NGAY, chỉ chưa thực thi được — mà cả runtime đang `moPhong=True`,
nên **không ty nào trong CHÍN ty hiện có thực thi gì cả**. "Chưa thực thi
được" vì thế không phải lý do để không dựng; nếu nó là lý do thì chín ty
đang chạy cũng lẽ ra không được tồn tại.

Cái thật sự phân biệt `QUET_DUOC` với `CHAN` là **dữ liệu công khai không
cần khoá**. Không có dữ liệu thì scanner chỉ là một cái vỏ luôn trả rỗng —
và cái vỏ ấy tệ hơn không có, vì nó làm phễu có thêm một dòng vĩnh viễn
bằng không và người đọc tưởng đã phủ engine ấy.

**Và một dòng bị gộp oan.** Quyền chọn nằm chung rổ "thiếu hạ tầng" với JIT
và MEV, nhưng Deribit công bố mặt IV **công khai, không cần khoá**. Nó là
việc CHƯA LÀM, không phải việc KHÔNG LÀM ĐƯỢC — và gộp hai câu ấy vào một
rổ là giấu mất việc dễ nhất trong sáu.

Bản đồ cũng xếp chúng ở cuối vì lý do ấy, và §14 nói thẳng: *"nhưng KHÔNG
làm thêm lúc này"*. Còn §21 nói cái đích đúng không phải "mười ba chiến
lược đều kiếm tiền" mà là:

    quét 13 họ → phát hiện 100 cơ hội → TỪ CHỐI 95 → rót vốn vào 5

Một hệ thống **từ chối giỏi** quan trọng hơn một hệ thống phát hiện nhiều.
Bốn ty hiện tại từ chối rất giỏi, và mỗi lần từ chối đều nói được vì sao.

### Thứ nên làm trước khi thêm engine

1. ~~**Cross-chain Router**~~ — XONG 27/08, `chuyen_von/`. Nó gỡ được
   `chuyen-von-giua-chuoi`, `chuyen-von-giua-san` và `gas-vao-ra` cho ba
   ty; phí rút CEX thì KHÔNG đọc được nên nằm ở bảng đo tay có hạn.
2. ~~**Gỡ nợ hai-cỗ-máy** bước 2–3~~ — XONG 27/08, `kham_ngoai/` và
   `thi_bac_ty/nhap_so_ngoai.py`.
3. **Lớp ký lệnh** — thứ DUY NHẤT còn chặn, và nó chặn có chủ ý:
   `DieuPhoiThucThi.moPhong` là `True` cứng, không cấu hình nào mở được.
   Mọi điều kiện `ky-lenh-onchain` trong sổ engine đều chờ nó, và chúng sẽ
   còn chờ.

## Thứ tự triển khai — §19 THAY THẾ thứ tự cũ

Bản khảo sát đầu xếp `Polymarket → Perp → Hyperliquid/Drift → Liquidation →
…`. Bản phản biện §19 **đổi nó**, vì Perpetual đã code trước nên không cần
quay lại Polymarket:

    1. Perpetual Funding Spread    XONG
    2. THỊ BẠC TY CORE             XONG
    3. Lending                     XONG  (tin_dung/)
    4. Stablecoin Arb              XONG  (on_dinh/)
    5. Basis                       XONG  (co_so/)
    6. Yield                       XONG  (lai_suat/)
    7. DEX Arb                     XONG  (dex_arb/ — vòng đổi khứ hồi)
    8. LP                          XONG  (lp_amm/ — CHỈ cặp neo)
    9. Liquidation                 CHẶN  — không liệt kê được người vay
    10. Options                    XONG  (quyen_chon/ — ngang giá)
    11. JIT                        CHẶN  — mempool
    12. MEV                        CHẶN  — mempool · builder · độ trễ

Mười hai mục, **chín xong**. Ba mục còn lại chặn vì cùng một loại lý do:
chúng cần dữ liệu KHÔNG công khai. Đó là *không làm được từ đây*, khác hẳn
*chưa làm* — và `dong_co_chua_co/so_dang_ky.py` giữ ranh giới ấy bằng phép
canh chứ không bằng văn xuôi.

**Cross-chain và Uniswap v4 KHÔNG nằm trong dãy này.** Chúng là hạ tầng, và
được thêm khi một engine khác cần — không phải theo lượt.

Vì sao Lending là engine thứ hai chứ không phải Basis: đây là một **phép thử
kiến trúc**. Perpetual là phái sinh, Lending là tín dụng, hai thứ gần như
không giống nhau. Nếu cả hai cùng đi lọt qua Tờ Trình → Rủi Ro Tổng → Danh
Mục → Phân Bổ → Sổ Cái thì lớp trừu tượng là thật. Làm Basis ngay sau
Funding thì hai chiến lược quá giống nhau, và ta sẽ *tưởng* abstraction tốt
trong khi chưa kiểm được gì.

## Ty đầu tiên — chênh lệch funding


Ty coi việc buôn bán giữa các cảng: xét hàng, thu thuế, và **đối chiếu giá
giữa các cảng** với nhau. Runtime này làm đúng việc ấy trên hợp đồng vĩnh cửu.

    PERPETUAL FUTURES
            │
            └── FUNDING SPREAD
                     ├─ Hyperliquid
                     ├─ Binance
                     ├─ OKX
                     └─ Bybit

Cùng một tài sản, cùng một lúc, mỗi sàn trả một mức funding khác nhau. LONG
nơi thấp, SHORT nơi cao, delta ≈ 0, thu chênh lệch. Không đoán giá lên xuống.

**Chỉ đọc dữ liệu CÔNG KHAI. Không đặt lệnh nào. Lớp đặt lệnh chưa được viết.**

## Chạy

```powershell
$py = "D:\SUNSWaGz 2027\Python 3.12.10\python.exe"
& $py -m pip install -r requirements.txt

& $py run.py                   # buồng lái ở http://localhost:5188
& $py -m bac.snapshot          # quét một lượt, ghi lát cắt, rồi thoát
& $py scripts/selftest.py      # 1009 phép kiểm số học, KHÔNG cần mạng
& $py scripts/sinh-icon.py     # vẽ lại 5 icon cho cung tĩnh
```

| lệnh | làm gì |
|---|---|
| `python run.py` | vòng lặp nền + buồng lái, ghi sổ mỗi lượt |
| `python -m bac.snapshot` | một lượt rồi ghi `thi-bac-ty/assets/js/v/cang-phi.js` |
| `python scripts/selftest.py` | toán, không mạng, không chạm sổ thật |
| `pythonw dichvu/chay-nen.py` | chạy nền 24/7, log xoay vòng, ghi PID |
| `dichvu\bat.ps1` · `dung.ps1` · `trang-thai.ps1` | bật / tắt / xem bản chạy nền |

Buồng lái **chỉ sống ở localhost** và không bao giờ lên site. Cung tĩnh
`thi-bac-ty/` (cổng 5187) là thứ lên GitHub Pages — nó **quan sát**, runtime
**điều khiển**. Đó là hai giao diện khác nhau, cố ý.

### Lát cắt sinh KHI CẦN, rồi phải COMMIT — và một lần chữa sai chiều

Tiêu đề của `cang-phi.js` từng hứa `python run.py — ghi mỗi vòng lặp`. Câu
ấy chép từ Tử Cấm Thành, nơi nó đúng thật (`trader/loop.py` gọi
`snapshot.write` sau MỌI vòng). Ở đây không lời gọi nào tồn tại —
`ghi_lat_cat` chỉ có hai chỗ gọi: nút trong buồng lái và `python -m
bac.snapshot`.

Lần chữa đầu đi sai chiều: thêm lời gọi vào `_vong_lap()` cho khớp lời
hứa. Cái bị bỏ sót là **trang công khai đọc bản ĐÃ COMMIT** — ghi ra đĩa
30 giây một lần không đẩy được một byte nào lên site; thứ đẩy là
`git commit`, và việc ấy vẫn do người làm. Đổi lại được đúng hai thứ, cả
hai đều xấu:

- một file **được git theo dõi luôn ở trạng thái bẩn** trong mọi cây có
  runtime chạy — và `git add thi-bac-ty/` của phiên lo cung ấy sẽ nuốt
  một ảnh chụp ngẫu nhiên vào commit của họ;
- `git merge --ff-only` ở cây chính **hỏng ngay** lần đầu có commit chạm
  tới file này. Đã xảy ra thật, mười phút sau khi thêm lời gọi.

Nên lời hứa được sửa chứ không phải mã: sinh khi CẦN, rồi COMMIT. Bài học
chung là **đừng chữa mã cho khớp một lời hứa mà chưa hỏi lời hứa ấy có
đúng thiết kế không** — ở đây câu văn đúng cho runtime khác, và chép sang
là chép cả một quyết định không thuộc về mình.

Phép kiểm canh hai chiều bằng **AST**, không bằng khớp chuỗi: tiêu đề hứa
ghi mỗi vòng thì vòng lặp phải GỌI thật, và ngược lại. Bản đầu tìm
`"ghi_lat_cat" in nguồn` và lỗi cấy `pass  # ghi_lat_cat(self)` đã đi lọt
— lần thứ ba kiểu hỏng ấy lọt qua một phép kiểm khớp chuỗi ở đây.

## Hai phép tính, và vì sao lẫn chúng là mất tiền

### 1 · Chuẩn hoá — để SO SÁNH hai cảng

Mỗi cảng kết toán theo một chu kỳ riêng, và OKX còn đổi chu kỳ được giữa
chừng (8h → 4h → 2h → 1h tuỳ điều kiện thị trường). Con số sàn công bố mà
không kèm chu kỳ là một con số vô nghĩa:

```
Binance      +0,080% / 8 giờ   →  0,010% / giờ
Hyperliquid  +0,015% / 1 giờ   →  0,015% / giờ   ← cao hơn
```

Nhìn số thô thì Binance lớn gấp năm. Sau chuẩn hoá thì ngược lại. Đây là lỗi
một scanner sơ sài mắc ngay ở dòng đầu, và nó **không hề giống lỗi** — mọi
con số vẫn hợp lệ, chỉ bảng xếp hạng là sai thứ tự.

### 2 · Đếm mốc — để biết GIỮ NGẦN ẤY THÌ THU BAO NHIÊU

Chuẩn hoá xong vẫn **chưa được nhân với số giờ giữ**. Funding không chảy liên
tục; nó là một khoản trả **tại một mốc**. Sàn kết toán 8 giờ trả vào 00:00,
08:00, 16:00 UTC — không trả gì vào 03:47.

```
Vào 00:05, thoát 04:05 — giữ 4 giờ, funding 0,01%/8h
  nhân theo giờ:  0,01% × (4/8) = 0,005%      ← nghe hợp lý
  đếm theo mốc:   0,000%                      ← chưa qua mốc nào

Vào 07:55, thoát 08:05 — giữ 10 PHÚT
  đếm theo mốc:   0,010%                      ← thu trọn một chu kỳ
```

Cùng một cặp sàn, cùng một mức funding, hai câu trả lời lệch nhau vô hạn lần.
`bac/dongho.py` làm phép thứ hai; `moi_gio()` chỉ dùng cho phép thứ nhất, và
hai hàm ấy cố ý không gọi lẫn nhau.

### 3 · Rồi mới trừ

```
funding thực thu   (đếm theo mốc, hai chân đếm RIÊNG)
  − phí taker vào    × 2 chân
  − phí taker ra     × 2 chân
  − trượt giá        × 4 lần khớp
  ─────────────────────────────
  = NET EDGE
```

**Bốn khoản chưa trừ**, và phải biết là chưa: chi phí vay coin, phí chuyển
vốn giữa sàn, rủi ro basis khi hai mark rời nhau lúc thoát, và vốn bị khoá.
Nên NET ở đây là **chặn trên**, không phải lợi nhuận.

## Trần vốn CHƯA có hiệu lực — và vì sao nó không nằm chung với cửa

`config.json` có khối `von` với `moiCoHoiUsd`, `toiDaUsd`, `donBayToiDa`, và
một cờ `coHieuLuc: false` nói thẳng: **ba con số này chưa chặn gì cả**. Không
có lớp đặt lệnh thì không có vị thế nào để mà giới hạn, kể cả trên sổ giấy.

Chúng từng nằm trong khối `ruiRo`, nên buồng lái bày chúng dưới nhãn *"Cửa
rủi ro đang có hiệu lực"* — ba cái cửa không chặn gì, hiện ra như đang chặn.
Không lỗi nào báo, vì mọi con số đều hợp lệ.

Nay `rui_ro.py` khai một tuple `CUA` là **hợp đồng**: mọi khoá trong đó phải
được `xet()` thật sự đọc, và `xet()` không được đọc khoá nào ngoài đó. Phép
kiểm canh cả hai chiều bằng một dict do thám — cấy thử một cửa giả vào thì
hai phép nổ ngay.

## Tám cửa rủi ro

`bac/rui_ro.py` là Python thuần, tất định, có quyền phủ quyết. Mỗi cửa nằm đó
vì một cách mất tiền cụ thể:

| cửa | chặn cái gì |
|---|---|
| `grossToiThieuBpsNgay` | chênh lệch quá mỏng, không đáng chạm vào |
| `netToiThieuBps` | phí ăn hết biên — càng làm càng lỗ |
| `doiHoiItNhatMotMoc` | **giữ hết cửa sổ mà không mốc nào rơi vào → thu = 0** |
| `lechMarkToiDaBps` | hai mark rời nhau → không còn delta-neutral |
| `doiHoiHaiMark` | thiếu mark một bên → *không biết* có lệch hay không |
| `tuoiToiDaGiay` | dữ liệu cũ → đang cược vào một thế giới đã qua |
| `nhanUocLuongMoc` | mốc phải đoán → sai số nằm ngoài tầm đo |
| `lechDongHoToiDaGiay` | **đồng hồ máy lệch giờ sàn** → mọi phép đếm mốc sai theo |

Cửa thứ ba và thứ bảy là hai cửa mà một scanner chỉ nhân `spread × giờ`
**không thể có** — nó không biết mốc nằm ở đâu.

Cửa thứ tám thêm vào sau khi đo được **đồng hồ máy chậm 6,94 phút** so với cả
ba sàn (21/08/2026). Nó hỏng theo hai đường, cả hai im lặng: phép đếm mốc so
giờ SÀN với giờ MÁY nên gần biên là lật hẳn kết quả; và `tuoi_giay()` kẹp hiệu
âm về 0, biến "dấu thời gian ở tương lai" thành "vừa mới tinh" — cửa
`tuoiToiDaGiay` đứng đó suốt mà không chặn nổi gì, kể cả khi cấy vào một báo
giá cũ 10 phút. Xem `bac/dong_ho.py`.

Gặp cơ hội bị chặn, buồng lái gom **đủ mọi lý do** chứ không dừng ở cái đầu.
Dừng sớm thì người vận hành nới một ngưỡng, chạy lại, gặp lý do thứ hai, nới
tiếp — và không bao giờ thấy bức tranh đầy đủ.

## Bốn cảng, bốn cách công bố khác nhau

| cảng | funding | chu kỳ lấy từ đâu | mark |
|---|---|---|---|
| Hyperliquid | `metaAndAssetCtxs` → `funding` | **1 giờ**, cố định | `markPx` |
| Binance | `premiumIndex` → `lastFundingRate` | `fundingInfo` (chỉ symbol đã điều chỉnh), mặc định 8h | `markPrice` |
| OKX | `funding-rate` → `fundingRate` | `nextFundingTime − fundingTime` | `mark-price` |
| Bybit | `tickers` → `fundingRate` | `instruments-info.fundingInterval`, **đơn vị PHÚT** | `markPrice` |

Ba cái bẫy đã gỡ, và cả ba đều hỏng im lặng:

- **Bybit trả chu kỳ bằng PHÚT.** Đọc 480 rồi coi là giờ thì funding/giờ nhỏ
  đi 60 lần, Bybit tụt xuống cuối mọi bảng và không bao giờ được ghép cặp.
  Không lỗi nào báo — chỉ là một cảng tự nhiên biến mất khỏi kết quả.
- **OKX ticker `last` không phải mark.** Bản đầu lấy `last` rồi so với
  `markPrice` của Binance: một bên là giá khớp cuối nhảy theo từng lệnh lẻ,
  bên kia là giá dùng để thanh lý. Độ lệch tính ra là hỗn hợp của lệch thật
  và tiếng ồn vi cấu trúc, rồi cửa `lechMarkToiDaBps` chặn nhầm hoặc thả nhầm
  theo.
- **Hyperliquid ghép meta với ctxs theo CHỈ SỐ.** Lệch một nấc là gán funding
  của SOL cho BTC — mọi con số vẫn hợp lệ. Dùng `zip(..., strict=True)` để nổ
  ngay lúc ghép thay vì lệch nhãn từ đó về sau.

Một cảng chết **không** kéo theo ba cảng còn sống: `Cang.bao_gia()` nuốt lỗi
vào `SucKhoe` rồi trả danh sách rỗng. Nhưng buồng lái hiện **MÙ MỘT MẮT** ở
dải trên cùng — vì bảng đủ ba cảng còn lại trông y hệt "thị trường không có
chênh lệch".

## Sổ quét ghi CẢ lượt trống

Một tuần không cơ hội nào là một **phát hiện** (chênh lệch đã đóng, hoặc phí
đã ăn hết biên), không phải một tuần không có dữ liệu. Sổ chỉ ghi lượt "có
hàng" sẽ dựng nên một lịch sử toàn ngày đẹp trời.

Từ đó tính được **độ dai** — thứ phân biệt hai chuỗi có cùng giá trị hiện tại:

```
30 → 21 → 12 → 3 → 0        chênh lệch đang tắt, vào là muộn
25 → 28 → 22 → 31 → 27      chênh lệch dai, đáng săn
```

`/api/do-dai` trả `tiLeDuong` — bao nhiêu phần lượt quét thấy NET còn dương.
NET 12 bps mà `tiLeDuong` 0,2 là một cú loé; NET 8 bps mà 0,9 thì đáng giá
hơn, dù con số nhỏ hơn.

## Chế độ và ba cửa

```
quan-sat   chỉ đo, không mở vị thế nào     ← mặc định
giay       cân trên số liệu thật, tiền giả
that       lệnh rời khỏi máy               ← CHƯA MỞ ĐƯỢC
```

Một lệnh thật cần **cả ba cửa cùng mở**, ở ba nơi khác nhau về bản chất:

1. `config.json` → `che: "that"`
2. `config.json` → `datLenh.toiXacNhanDaDocRuiRo: true`
3. `.env` → khoá API của ít nhất một sàn

Và một **cửa thứ tư không mở được bằng cấu hình**: lớp đặt lệnh chưa tồn tại.
`ly_do_khong_that()` in ra đúng cửa nào đang đóng, không rơi trong im lặng.

## Đào tạo — bốn tầng, và thứ tự phụ thuộc là bắt buộc

```
1. CHẠY NỀN     tích băng 24/7          dichvu/chay-nen.py
       ↓
2. BĂNG GHI     nguyên liệu thô         bac/bang.py
       ↓
3. CHẠY LẠI     đo funding THỰC NHẬN    bac/chay_lai.py
       ↓
4. CHẨN + TIẾN HOÁ   vặn ngưỡng có bằng chứng   bac/chan_doan.py · bac/tien_hoa.py
```

Không nhảy cóc được. Sổ ở `so.py` ghi **kết luận**; băng ghi **nguyên liệu**:

    sổ    "hôm qua ta đã quyết thế nào"
    băng  "nếu ngưỡng khác đi thì ta ĐÃ quyết thế nào"

Thiếu băng thì mọi lần vặn ngưỡng đều là đổi số cho vui.

### Chạy lại đo được thứ mà ảnh chụp không đo được

`thuBps` là DỰ ĐOÁN: giả định rate hiện tại giữ nguyên tới lúc kết toán.
`thuThucBps` là ĐO ĐƯỢC: tra ngược từ băng, tại TỪNG MỐC kết toán, lấy đúng
rate sàn công bố lúc ấy.

Khoảng cách giữa hai con số là **funding decay**, và nó là thứ đáng học nhất.
`chan_doan` gọi nó là `du-doan-lac-quan` khi lệch quá 2 bps trung bình — lúc
đó mô hình không xui, nó lạc quan có hệ thống.

**Ba chỗ xấp xỉ, và cả ba đều làm kết quả ĐẸP HƠN sự thật:** rate tại mốc lấy
từ khung gần nhất (không phải rate sàn thật sự áp); không mô phỏng khớp lệnh;
không mô phỏng vốn bị kẹt. Nên `netThucBps` là **chặn trên**.

### `netBps` là CHẶN TRÊN, và mỗi cơ hội tự khai điều đó

Mỗi `CoHoi` mang theo:

```
moHinhPhiDuChua = false
phiConThieu     = [vay-coin, chuyen-von, basis-luc-thoat, von-bi-khoa]
```

Không phải để trang trí. Khi Thị Bạc Ty có chiến lược thứ hai, bảng xếp hạng
sẽ đặt cạnh nhau:

    funding spread   18 bps   ← chặn trên, còn thiếu bốn khoản
    chiến lược khác  11 bps   ← đã trừ đủ

và kết luận *"funding tốt hơn"* là kết luận **sai**, rút ra từ hai con số
không cùng đơn vị. Không có cờ này thì không cách nào biết mà tránh — chính
cỗ máy sẽ bị đánh lừa bởi số liệu của chính nó.

Mỗi cơ hội cũng mang `maChienLuoc = "perp.funding_spread.v1"`. Hiện chưa phân
biệt được gì vì mới có một chiến lược; giữ vì cái giá là một dòng, còn cái
giá của việc thêm SAU là đi gắn nhãn ngược cho mọi băng đã ghi.

### Bốn luật chặn bốn cách tự lừa

| luật | chặn gì |
|---|---|
| cửa AN TOÀN không nằm trong `NUT_VAN` | đường nhanh nhất tới điểm cao là **tắt đèn báo** — nó sẽ tìm ra ngay |
| phí không phải núm vặn | vặn phí xuống là tự vẽ ra lợi nhuận |
| một lượt vặn ĐÚNG MỘT núm | vặn hai núm rồi khá lên thì không biết núm nào có công |
| nhận chỉ khi ≥30 mẫu **và** cải thiện > 0,15 bps | không thì "tiến bộ" mỗi ngày mà tổng lại không đi đâu |

`doiHoiHaiMark`, `doiHoiItNhatMotMoc`, `nhanUocLuongMoc`,
`lechDongHoToiDaGiay` cố ý **không** vặn được. Chúng không phải ngưỡng hiệu
năng — chúng là câu "ta không biết đủ để vào lệnh".

### File `.ps1` PHẢI lưu UTF-8 CÓ BOM

Windows PowerShell 5.1 đọc `.ps1` không BOM theo bảng mã ANSI. Chữ tiếng Việt
vỡ, và ký tự nhiều byte nuốt luôn dấu nháy — lỗi báo ra là
`The string is missing the terminator` ở một dòng chẳng liên quan gì.

Đã cắn ngay lượt chạy đầu của `bat.ps1`. Cùng bẫy đã ghi sẵn ở hai runtime
kia; kiểm bằng:

```powershell
Get-ChildItem dichvu\*.ps1 | ForEach-Object {
  $b = [IO.File]::ReadAllBytes($_.FullName)[0..2]
  "{0}  {1}" -f $_.Name, (($b -join ',') -eq '239,187,191')
}
```

### Bao lâu mới có mẫu đầu tiên

Với nhịp 30 giây và cửa sổ giữ 8 giờ: băng phải phủ **hết** cửa sổ mới hậu
kiểm được một cơ hội. Một phiên chạy tay vài chục phút sinh ra **đúng 0 mẫu**
— bảng vẫn xanh, sổ tiến hoá ghi "chưa đủ mẫu", và không có gì sai cả; chỉ là
chưa có gì để học. Đó là lý do `dichvu/chay-nen.py` tồn tại.

    POST /api/chay-lai                 chạy lại băng, tham số hiện tại
    POST /api/doi-chieu?nut=…&gtA=…&gtB=…   so hai giá trị trên CÙNG băng
    POST /api/tien-hoa?thu=true        xem sẽ vặn gì, không ghi gì
    GET  /api/duong-tien-hoa           sổ tiến hoá gộp
    GET  /api/bang                     băng có bao nhiêu khung, có lành không

Hoặc mở buồng lái, tab **Đào tạo**.

## Buồng lái — MƯỜI đường, ba tầng, và trang gốc thuộc TRUNG ƯƠNG

`localhost:5188/` **không thuộc về bất kỳ ty nào.** Trước 28/08/2026 trang
gốc là bảng chẩn đoán của riêng ty chênh funding — bps, mốc L+S, lệch
mark — nên một động cơ trong mười ba chiếm cửa vào của cả bộ máy, và
người mở nó ra phải giải mã mới biết máy có ổn không.

| tầng | trả lời câu gì | ở đâu |
|---|---|---|
| 1 | máy có ổn không · tiền ở đâu · lời lỗ · ai đang chạy | `/` |
| 2 | vì sao — vốn, vị thế, cơ hội, rủi ro, nguồn dữ liệu | `/von` `/vi-the` `/co-hoi` `/rui-ro` `/du-lieu` |
| 3 | mổ máy — bps thô, lệch mark, RPC, log | `/dong-co/<mã>` |

    /            trung tâm — BÂY GIỜ, năm ô, mạch tám chặng, việc cần người
    /dong-co     mười ba động cơ, SÁU trạng thái quy về một hệ
    /von         NAV · vốn ngoài · năm lát cắt phơi nhiễm
    /vi-the      danh mục ↔ sổ đăng ký, và chỗ chúng lệch nhau
    /co-hoi      tờ trình CẢ CHÍN TY trong một bảng, và phễu
    /loi-lo      KHÔNG trộn tiền thật với mô phỏng
    /rui-ro      cầu dao · trần Rủi Ro Tổng · hiến pháp
    /du-lieu     sơ đồ hạ tầng + sức khoẻ từng nguồn
    /so-cai      bút toán, tờ trình theo ty, nhật ký
    /he-thong    vòng chạy · lớp thực thi · bản tham số

Ba luật của lớp giao diện, và cả ba đều có phép kiểm canh:

1. **Trang trắng không được im lặng.** Một hàm vẽ ném giữa chừng để lại
   thân trang rỗng nhìn y hệt máy chết — nên chỗ đáng lẽ là nội dung sẽ
   hiện chính lỗi ấy, kèm câu *"máy VẪN đang chạy"*.
2. **Màu là trạng thái.** Sáu màu trạng thái không dùng vào việc gì khác,
   kể cả làm màu nhấn. Sơ đồ hạ tầng vì thế **không mượn** chúng: nó chỉ
   có hai dấu — đỏ là hỏng, nét đứt là **chưa đo được**, và nét đứt ấy
   phân biệt "đo" (bốn cảng perp, RPC gas, LI.FI có bộ đếm thật) với
   "suy" (Deribit, DefiLlama, Polymarket — chỉ suy từ ty của chúng).
3. **Số thô của tầng ba không được leo lên tầng một.** `markPx`,
   `lechMarkBps`, `aprPhanTram`, `mocL` chỉ sống ở `/dong-co/...`.

Dựng thử KHÔNG chỉ là kiểm cú pháp: một harness DOM giả chạy cả mười ba
đường trên **dữ liệu thật**, và trên cả những trạng thái *không* đang xảy
ra — cảng chết, ty ném lỗi, vị thế mồ côi chưa đối soát. Chúng là đúng
những ô mà buồng lái tồn tại để hiện; dựng chỉ trên ảnh chụp "mọi thứ đều
ổn" thì chúng chưa bao giờ được vẽ lần nào.

## Lộ trình — V0.6 là mốc duy nhất chạm tới tiền

| | xây gì | được làm gì |
|---|---|---|
| **V0.1** | quét công khai, chuẩn hoá, đếm mốc, 8 cửa, sổ SQLite | xong |
| **V0.2** | băng ghi · chạy lại · chẩn đoán · tiến hoá · chạy nền | ← **đang ở đây** |
| V0.3 | độ dai dài hạn (half-life, z-score, regime) | biết chênh lệch nào dai |
| V0.4 | sổ lệnh thật → trượt giá thật, không phải tham số | NET hết là ước lượng |
| V0.4 | sổ giấy 24/7 + phân bổ lãi lỗ theo nguồn | biết tiền đến từ đâu |
| V0.5 | testnet + **máy trạng thái hai chân** + kill switch | tập vào lệnh mà không mất gì |
| V0.6 | vốn thật rất nhỏ + đối soát vị thế từ SÀN | mốc đầu tiên chạm tiền |
| V0.7 | Capital Router — xếp hạng và phân bổ vốn | |

**Vì sao máy trạng thái hai chân đứng trước tiền thật.** Không được viết
kiểu này:

```python
short_binance()          # khớp
long_hyperliquid()       # TRƯỢT
```

Giữa hai dòng ấy, BTC giảm 1%. Vị thế đang từ delta-neutral thành **short
một chiều** — *legging risk*, và đó là cách mất tiền nhanh nhất trong nghề
này. Phải là một máy trạng thái có đường lùi:

```
CHỜ → DUYỆT → GIỮ VỐN → MỞ CHÂN A → MỞ CHÂN B → ĐÃ PHÒNG HỘ → GIỮ
                              │
                        chân B hỏng
                              │
                    ┌─────────┼─────────┐
                 thử lại   sàn khác   ĐÓNG GẤP
```

Không dòng nào trong đường ấy được để model quyết định.

## AI nằm ở đâu

**Không nằm trong vòng ký lệnh.** Bản V0.1 không gọi model lần nào.

Về sau, model chỉ được gọi **khi có bất thường** — không phải mỗi tick:

```
vòng lặp Python 24/7          gần như $0
        │
   ┌────┴────┐
BÌNH THƯỜNG  BẤT THƯỜNG
   │              │
không gọi     gọi MỘT lần
```

Và khi gọi thì quyền của nó là `QUAN SÁT · TRA CỨU · GIẢI THÍCH · ĐỀ XUẤT` —
không bao giờ `KÝ · RÚT · VƯỢT CỬA RỦI RO`.

## Bản đồ mã

```
bac/
  dongho.py     đếm mốc kết toán      ← lõi, đọc trước
  dong_ho.py    lệch đồng hồ máy/sàn  ← đọc ngay sau
  models.py     BaoGia · CoHoi
  can_loi.py    ghép cặp, trừ phí, ra NET
  rui_ro.py     bảy cửa, tất định, phủ quyết
  san/          bốn cảng + sổ sức khoẻ
  so.py         SQLite: mọi lượt quét, kể cả lượt trống
  vong.py       vòng lặp nền, hỏi bốn cảng SONG SONG
  server.py     buồng lái :5188
  snapshot.py   cầu nối sang cung tĩnh

  bang.py       băng ghi nguyên liệu  ← tầng đào tạo
  chay_lai.py   hậu kiểm funding thực
  chan_doan.py  bệnh đo được
  tien_hoa.py   vặn ngưỡng có bằng chứng

  xuat_to_trinh.py  CoHoi → ToTrinh    ← chỗ nối lên trung ương
  ty_perp.py        cắm vào khuôn Ty   ← mỏng có chủ ý

chuoi_chung/      hạ tầng của HỌ đọc chuỗi — không phải ty, không phải trung ương
  thang.py        TVL → rủi ro giao thức · dùng vốn → rủi ro thanh khoản

tin_dung/         TY THỨ HAI — tín dụng, cắm vào cùng khuôn Ty
  config.py       mã chiến lược, cửa rủi ro, bảng gas
  models.py       ThiTruongVay · CoHoiVay
  nguon.py        DefiLlama, ghép hai đường
  rui_ro.py       cổng ty, hợp đồng CUA
  can_loi.py      trừ gas, tính hoà vốn
  ty_vay.py       chỗ nối lên Trung Ương

lai_suat/         TY THỨ BA — Pendle PT, lãi cố định khoá tới đáo hạn
  ty_lai_suat.py  ty đầu tiên dùng `khoaVonDenGiay` với số THẬT

on_dinh/          TY THỨ TƯ — chênh lệch stablecoin, HỌ THỨ BA
  config.py       chu kỳ vốn ≠ thời gian giao dịch
  nguon.py        bí danh → san_chung/giao_ngay.py
  ty_on_dinh.py   cửa DEPEG là cửa quan trọng nhất

phai_sinh_chung/  hạ tầng HỌ PHÁI SINH — ra đời khi có người dùng THỨ HAI
  dongho.py       đếm mốc kết toán (bac/ giữ bí danh)
  dong_ho.py      MỘT đồng hồ cho cả họ
  models.py       BaoGia — dùng chung bac/ và co_so/
  san/            bốn cảng perp

san_chung/        connector giao ngay — dùng chung giữa HAI họ
  giao_ngay.py    bid/ask ba sàn, ba hình dạng JSON

co_so/            TY THỨ NĂM — cash-and-carry
  ty_co_so.py     BASIS KHÔNG phải thu nhập; giữ 168h, không phải 8h

kham_ngoai/       TY THỨ SÁU — adapter Khâm Thiên Giám, HỌ THỨ TƯ
  ty_tien_doan.py chỉ DỊCH, không định giá lại · ranh giới đếm hai lần

quyen_chon/       TY THỨ BẢY — ngang giá call/put Deribit
  ty_ngang_gia.py KHÔNG mô hình nào; và một thừa số đang TRƠ, có khai ra

dex_arb/          TY THỨ TÁM — vòng đổi khứ hồi trên một chuỗi
  ty_vong_doi.py  cổng dùng mức BẢO ĐẢM, không dùng kỳ vọng

lp_amm/           TY THỨ CHÍN — cấp thanh khoản, HỌ THỨ NĂM
  ty_cap_thanh_khoan.py  cờ bên thứ ba là LỜI KHAI — tự đọc ký hiệu

chuyen_von/       ROUTER — hạ tầng, KHÔNG phải ty, không xin vốn
  diem.py         một chặng mù thì CẢ TUYẾN mù
  bang_do.py      phí rút CEX gõ tay, có xuất xứ và có HẠN 45 ngày
  gas.py          gas bốn chuỗi từ RPC công khai
  cau_noi.py      LI.FI · bảng token đã đối chiếu, thập phân theo từng cặp
  dinh_tuyen.py   cửa DUY NHẤT ty nên gọi

dong_co_chua_co/  sổ engine CHƯA dựng — điều kiện chặn viết dạng CHẠY ĐƯỢC
  so_dang_ky.py   CHAN · QUET_DUOC · SAN_SANG · DA_DUNG, tự nạp thử gói ty

thi_bac_ty/       TRUNG ƯƠNG — không bao giờ import bac/
  to_trinh.py     hợp đồng            ← đọc trước
  khuon_ty.py     khuôn một ty mới    ← đọc ngay sau
  thong_chinh.py  sàn nhận tờ trình
  so_dang_ky.py   vòng đời + cái phễu
  danh_muc.py     ba thước phơi nhiễm
  rui_ro_tong.py  trả về một TRẦN
  phan_bo.py      xếp hạng, cấp tuần tự
  so_cai.py       sổ chỉ-thêm, sửa bằng ĐẢO
  thuc_thi.py     máy trạng thái hai chân
  cau_dao.py      ngắt tự động, đóng lại phải có người
  hien_phap.py    30 ĐIỀU luật vận hành, mỗi điều kèm phép canh
  che_van_hanh.py QUAN_SAT · GIAY · THAT theo từng ty, và chi phí hạ tầng
  hieu_nang.py    CAGR · sụt vốn tối đa · đối chiếu giấy↔thật
  nguon.py        Data World v0.1 — kỷ luật chung khi đọc một nguồn
  von_ngoai.py    vốn ở cỗ máy KHÁC: thấy được, không quản được
  nhap_so_ngoai.py kết toán cỗ máy khác vào MỘT sổ; bỏ sót tự lộ
  chan_doan_he.py bệnh của cả bộ máy
  chay_lai_he.py  chạy lại quyết định phân bổ, đo đề xuất
  cong_duyet.py   bảy luật một đề xuất phải qua
  ban_tham_so.py  tham số có SỐ HIỆU, quay lui được
  trung_uong.py   khép vòng            ← đọc sau cùng
```

Hỏi bốn cảng **song song không phải để nhanh**: hỏi tuần tự cách nhau vài
trăm mili giây là bốn ảnh chụp ở bốn thời điểm, rồi đem so như thể cùng lúc.
Trong một cú biến động, mark của cảng hỏi trước và cảng hỏi sau lệch nhau chỉ
vì thứ tự hỏi.

## Ty thứ năm: CƠ SỞ — và một khoản lãi KHÔNG được phép cộng vào

`co_so/` mua giao ngay và bán khống perp **cùng một sàn, cùng một mã**. Nó
là ty thứ hai của họ `phai-sinh`, nên nó là ty đầu tiên chứng minh được
điều mà bốn ty trước chỉ nói: **hai ty cùng họ dùng chung hạ tầng mà không
ty nào gọi ty nào.**

### Basis đo được, nhưng KHÔNG phải thu nhập

Perp đắt hơn giao ngay 30 bps thì đó là 30 bps *ai đó sẽ trả cho ta* — nếu
hai giá hội tụ. Với hợp đồng có đáo hạn thì chúng buộc phải hội tụ, và
basis đúng là thu nhập. **Perp không đáo hạn.** Không có ngày nào bắt hai
giá gặp nhau, nên cộng basis vào NET là ghi vào sổ một khoản chưa ai hứa
trả.

Nên `netBps = gross − phí`, và `gross` chỉ gồm **funding thu tại các mốc
kết toán trong cửa sổ giữ**. `basisBps` vẫn được đo, vẫn hiện ra, nhưng nó
vào phần **rủi ro** chứ không vào phần lãi:

- basis âm quá sâu → mua giao ngay đắt hơn giá thanh lý của chân short:
  một khoản lỗ trả trước, không phải cơ hội
- basis dương quá rộng → hoặc một trong hai giá sai, hoặc thị trường đang
  định giá một rủi ro ta chưa nhìn ra

### Phí là BỐN lần taker, và đó là con số quyết định

Hai chân, mỗi chân vào rồi ra: `2 × 2 = 4`. Ở Binance 5 bps taker thì phí
khứ hồi là **20 bps** — một khoản **cố định**, trả một lần, không chia
theo thời gian giữ.

Đó là lý do `giuGio` của ty này là **168 giờ** chứ không phải 8 như ty
chênh funding. Ở mức funding đo được lúc viết chương này (+0,0011%/giờ):

| giữ | số mốc | gross | phí | NET |
|---|---|---|---|---|
| 8 giờ | 1 | +0,86 bps | 20 bps | **−19,1 bps** |
| 7 ngày | 21 | +18,2 bps | 20 bps | **−1,8 bps** |
| 30 ngày | 90 | +78,1 bps | 20 bps | **+58,1 bps** |

Cash-and-carry là chiến lược **giữ**. Đặt cửa sổ 8 giờ cho nó rồi kết
luận "không có cơ hội" là đo sai thước, không phải đọc đúng thị trường.

### Nhưng cửa sổ dài mua bằng một GIẢ ĐỊNH mạnh hơn

`gross` = mức funding **hiện tại** × số mốc trong cửa sổ. Với một mốc, đó
gần như một sự thật. Với chín mươi mốc, đó là một **dự báo ba tháng đội
lốt một phép nhân** — funding đảo dấu thường xuyên, và khi nó đảo thì
chính ta là bên trả.

Không có cách nào làm giả định ấy đúng hơn bằng số học. Cái làm được là
**không giấu nó**:

- `_tin_cay()` trừ dần theo `log2(số mốc)`, tối đa −0,30
- `bangChung` in thẳng câu *"GIẢ ĐỊNH: mức funding hiện tại giữ nguyên
  suốt 21 mốc. Nó không giữ nguyên."*

Trung Ương nhân `tinCay` vào `netMoiGioBps` khi xếp hạng, nên một cơ hội
7 ngày phải **thật sự** tốt hơn mới thắng được một cơ hội 8 giờ.

### Một ảnh chụp, một thời điểm

`TyCoSo.quet()` tự đọc giao ngay, nhưng **không tự hỏi perp** — nó nhận
`runtime` và đọc lại `runtime.baoGia` của chính lượt quét ấy.

Hỏi lần nữa là hai ảnh chụp ở hai thời điểm rồi ghép như thể cùng lúc:
đúng lỗi mà `dong_ho.py` sinh ra để chặn giữa bốn cảng, chỉ khác là lần
này giữa hai **ty**. Cửa `tuoiToiDaGiay` lấy `max()` tuổi của hai vế, nên
nếu nhịp ty bị đặt thưa hơn nhịp chung thì nó tự chặn chứ không lặng lẽ
dùng giá cũ.

### Hai gói hạ tầng ra đời ở đây, và cả hai đều KHÔNG phải ty

    phai_sinh_chung/   đồng hồ, lịch mốc, BaoGia, bốn cảng perp
    san_chung/         connector giao ngay (bid/ask ba sàn)

Chúng ra đời **khi có người dùng thứ hai**, không dựng sẵn từ đầu: một lớp
trừu tượng rút từ một người dùng duy nhất sẽ phải viết lại ở người dùng
thứ hai. `bac/` và `on_dinh/` giữ bí danh trỏ tới thân hàm mới — bí danh,
không phải bản sao, và có phép kiểm canh đúng chữ `is`.

Lần tách này lộ ra một lỗi trong chính hiến pháp: `_goi_ty()` khi ấy nhận
diện ty bằng **danh sách loại trừ**, nên `phai_sinh_chung/` vừa sinh ra đã
bị coi là một ty, và điều `ty-khong-goi-ty` báo `bac` đang gọi ty khác
trong khi `bac` chỉ đang dùng hạ tầng của họ mình. Nay nhận diện theo
**cấu trúc** — có lớp nào kế thừa `khuon_ty.Ty` không — nên gói mới tự
phân loại đúng, không đòi ai nhớ cập nhật danh sách.

## Câu treo trên tường

> **NET EDGE mới là alpha.** Funding thô thì không.
>
> **Funding trả theo MỐC.** Giữ 4 giờ trên sàn kết toán 8 giờ có thể thu được
> đúng bằng không.
>
> **Signal đúng ≠ trade có lãi.** Ở giữa hai thứ đó là phí, trượt giá, và một
> chân lệnh không khớp.
