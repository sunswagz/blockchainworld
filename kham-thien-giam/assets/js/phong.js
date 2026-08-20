/* ═══════════════════════════════════════════════════════════════
   Sổ bảy phòng của Khâm Thiên Giám — VIẾT TAY, sửa như mã nguồn.

   File này KHÔNG do bot sinh. Nó là phần giảng giải: cỗ máy làm gì, và
   vì sao mỗi bước lại làm như vậy. Số liệu sống nằm ở `v/dai-chiem.js`
   do runtime ở máy ghi ra — hai file cố ý tách nhau, vì một cái đổi khi
   người viết lại còn cái kia đổi mỗi lượt chạy.

   Thêm phòng: thêm một khối vào PHONG. `app.js` tự dựng thanh bên và
   tuyến hash từ mảng này, không phải sửa hai chỗ.
   ═══════════════════════════════════════════════════════════════ */

window.PHONG = [
  {
    ma: "dai-chiem",
    ten: "Đài Chiêm",
    phu: "tính ra bầu trời đáng lẽ phải thế nào",
    icon: '<circle cx="12" cy="12" r="8.6"/><path d="M12 3.4v17.2M3.4 12h17.2"/><circle cx="12" cy="12" r="3.1"/>',
    tom: "Cỗ máy không hỏi “42¢ có rẻ không”. Nó tự tính ra outcome đáng giá bao nhiêu, rồi mới nhìn sang chợ.",
    doan: [
      {
        h: "Câu hỏi bị đặt sai",
        p: "Một market “BTC lên hay xuống trong 5 phút” trông đơn giản tới mức người ta hỏi nhầm câu. Câu hỏi tự nhiên là <b>“Bitcoin sắp lên hay xuống?”</b> — và đó là câu hỏi của người đánh cược, không phải của cỗ máy.",
        p2: "Cỗ máy hỏi câu khác hẳn: <b>“Thứ đáng giá 54¢ này, tôi có mua được với giá thấp hơn 54¢ đủ nhiều để sống sót sau phí không?”</b> Nó không cần biết Bitcoin đi đâu."
      },
      {
        h: "Trước công thức, phải biết cửa nào là cửa làm việc",
        canh: true,
        p: "Đây là chỗ bản đầu của cỗ máy sai, và sai về <b>cấu trúc</b> chứ không phải sai một con số. Một khung Up/Down có <b>hai cửa</b>, và chúng không trùng nhau:",
        cong: [
          "[eventStart − 300s , eventStart]    ĐẶT CƯỢC   ← chỗ bot làm việc",
          "[eventStart        , endDate   ]    QUAN SÁT   ← sổ đóng băng"
        ],
        p2: "Bản đầu nhắm vào cửa quan sát. Đo thật bằng WebSocket, bám bốn khung qua ranh giới, ghi mỗi 11 giây:",
        cong2: [
          "09:12:12  khung eventStart 09:10  →  101/0   thang chờ, không yết giá",
          "09:12:12  khung eventStart 09:15  →   92/7   UP 0.930, giá CHẠY thật"
        ],
        p3: "Hệ quả nếu nhắm sai cửa: cỗ máy chỉ nhìn thấy <b>thang chờ</b> — một dải lệnh trải từ 0,1¢ tới 99,9¢ với hơn một triệu cổ. Nhìn số thì đó là thanh khoản khổng lồ; thực chất không mức nào là báo giá thật. Và mọi lệch giá nó thấy đều là ảo."
      },
      {
        h: "Công thức",
        cong: [
          "z = [ ln(S/K) − σ²τ/2 ] / ( σ√τ )",
          "P(UP) = Φ(z)"
        ],
        bang: [
          ["S", "giá hiện tại"],
          ["K", "giá lúc mở khung — chính là lằn ranh"],
          ["τ", "số giây còn lại"],
          ["σ", "độ lệch chuẩn log-return mỗi giây"],
          ["Φ", "phân phối tích luỹ chuẩn"]
        ],
        p: "Giả định là log-giá đi ngẫu nhiên <b>không xu hướng</b>. Đó là giả định bảo thủ nhất có thể: nó không cho mô hình mượn một niềm tin về hướng đi mà nó không có bằng chứng."
      },
      {
        h: "Cái bẫy τ → 0",
        canh: true,
        p: "Còn 0,2 giây thì σ√τ gần bằng 0, z bắn ra vô cực, và P(UP) thành <b>đúng 1,0000000000</b>. Mô hình tuyên bố chắc chắn 100% <b>đúng vào lúc nó biết ít nhất</b> — vì một tick cuối cùng vẫn lật được kết quả.",
        p2: "Chặn bằng hai lớp: sàn cho τ, và làm phẳng kết quả về trong [2%, 98%]. Một lớp chỉ chữa mẫu số; lớp kia chữa cả kết quả."
      },
      {
        h: "Bất định phải đi kèm, luôn luôn",
        p: "Trả về một con số P trần trụi là nói dối bằng cách bỏ sót. σ được ước lượng từ quá khứ và dùng cho tương lai; trong một cú sập thì σ đo được vẫn là σ của lúc bình yên.",
        p2: "Nên mỗi lần định giá đều mang theo <b>bất định</b>, và Risk Engine trừ thẳng nó vào lợi thế. Bất định lớn hơn khoảng cách từ P tới 50% nghĩa là mô hình đang nói “tôi không biết” bằng một con số trông như đang biết."
      },
      {
        h: "Và riêng binary ngắn hạn có thêm một thứ nữa",
        p: "Sai số tham số không đo được thứ nguy hiểm nhất của hợp đồng 5 phút. Bản đầu tiên của mô hình cho ra một bảng nói ngược sự thật: bất định <b>tụt dần</b> khi tới gần kết quả — vì trong đuôi phân phối thì mật độ nhỏ nên đạo hàm theo σ cũng nhỏ.",
        p2: "Thêm <b>rủi ro nhảy giá</b> đo đúng câu “giá đang cách lằn ranh bao xa so với thứ một cú nhảy dịch được”. Nó tự phân biệt hai tình huống mà một hằng số không phân biệt nổi:",
        ds: [
          "<b>Ngay trên lằn ranh, còn 3 giây</b> → bất định ~0,23. Đúng: đó là tung đồng xu, bất kể mô hình nói gì. Chính là cú “UP 95¢ → 5¢”.",
          "<b>Cách 3σ, còn 3 giây</b> → bất định ~0,003. Cũng đúng: một cú nhảy cỡ một giây không với tới. Vị thế này thật sự an toàn."
        ]
      }
    ]
  },

  {
    ma: "so-lenh",
    ten: "Sổ Lệnh",
    phu: "chỗ lợi thế trên giấy chết trong thực chiến",
    icon: '<path d="M4 5h16M4 9h10M4 13h16M4 17h7"/>',
    tom: "Không phép đo nào ở đây trả về “giá” mà không hỏi “bao nhiêu cổ”. Best ask là để hiển thị, không phải để tính lợi thế.",
    demo: "vwap",
    doan: [
      {
        h: "Phép trừ ai cũng làm, và nó sai",
        p: "Mô hình nói 55¢. Best ask là 46¢. Bảng điều khiển hiện <b>EDGE = 9¢</b> và ai nhìn cũng thấy hợp lý.",
        p2: "Con số đó đúng cho <b>đúng 80 cổ phần đầu tiên</b>. Sổ lệnh có 80 cổ ở 46¢, 200 cổ ở 48¢, 400 cổ ở 50¢, 1.000 cổ ở 53¢. Muốn nhiều hơn 80 thì phải ăn lên các mức trên."
      },
      {
        h: "Giá thật là VWAP",
        cong: [
          "(80×0.46 + 200×0.48 + 400×0.50) / 680  =  0.4894"
        ],
        p: "Lợi thế thật ở 680 cổ còn <b>6,1¢</b>, không phải 9¢. Muốn cả 1.680 cổ trong sổ thì VWAP lên 0,5136 và lợi thế chỉ còn <b>3,6¢</b>.",
        p2: "Khối lượng vừa nhân lên 21 lần thì lợi thế mỗi cổ vừa mất 60%. Đây là chỗ phần lớn chiến lược trông đẹp trên biểu đồ chết khi gặp tiền thật."
      },
      {
        h: "Nên cơ hội không bao giờ chỉ là một con số",
        p: "Một cơ hội <b>10¢ nhưng chỉ khớp được $4</b> kém hơn hẳn một cơ hội <b>1,2¢ khớp được $20.000</b>. Nên mỗi cơ hội đều mang theo ba thứ nữa:",
        ds: [
          "<b>sức chứa</b> — gom được nhiều nhất bao nhiêu cổ mà lợi thế vẫn dương",
          "<b>xác suất khớp</b> — taker gần như chắc; maker phải đợi người tới ăn",
          "<b>nửa đời</b> — cơ hội sống được bao nhiêu mili-giây trước khi chợ ăn mất"
        ]
      },
      {
        h: "Mấy cái tên kêu, và thứ nằm dưới",
        p: "Dashboard người ta khoe hay có <span class='ma'>BOOK MEMBRANE</span>, <span class='ma'>PRESSURE FIELD</span>, <span class='ma'>LIQUIDITY MAP</span>. Nguyên liệu vẫn là đúng một sổ L2, và từ nó tính ra được:",
        ds2: ["spread", "độ sâu", "lệch bid/ask", "microprice", "áp lực mua", "áp lực bán", "độ dốc thanh khoản", "tác động giá", "trượt giá dự tính"],
        p2: "Tên đặt đẹp không tạo ra lợi thế. Nhưng <b>microprice viết sai dấu</b> thì mọi tín hiệu dựa trên nó đảo chiều, và nó không bao giờ ném lỗi — nên phép kiểm giữ cả hai chiều: bid dày thì microprice phải nằm <i>trên</i> mid, ask dày thì nằm <i>dưới</i>."
      }
    ]
  },

  {
    ma: "can-loi",
    ten: "Cân Lợi",
    phu: "năm khoản trừ, bỏ khoản nào cũng ra số đẹp hơn và sai hơn",
    icon: '<path d="M12 3.5v17M5 8h14"/><path d="M5 8 2.5 14a3.2 3.2 0 0 0 5 0z"/><path d="M19 8l-2.5 6a3.2 3.2 0 0 0 5 0z"/>',
    tom: "Câu treo trên tường: correlation không phải alpha, signal không phải alpha, latency không phải alpha. Net executable edge mới là alpha.",
    demo: "phi",
    doan: [
      {
        h: "Bằng chứng đắt giá nhất",
        canh: true,
        p: "Nghiên cứu OpenMarket (07/2026) ghép <b>727 triệu bản ghi</b> Polymarket–Binance ở mức mili-giây, 43 đặc trưng vi cấu trúc, walk-forward đàng hoàng. Họ <b>xác nhận</b> Polymarket phản ứng trễ sau Binance, trung vị khoảng <b>347 ms</b>.",
        p2: "Và mô hình của họ <b>vẫn không tạo được lợi thế giao dịch ngoài mẫu sau phí và trượt giá</b>. Tín hiệu có thật, độ trễ có thật, và cả hai cộng lại vẫn ra một chiến lược lỗ. Chỗ chênh lệch nằm đúng ở phép trừ dưới đây."
      },
      {
        h: "Năm khoản trừ",
        cong: [
          "netEdge(q) = fairValue",
          "           − vwap(q)          giá THẬT cho q cổ",
          "           − phí(q)           maker 0, taker theo giá",
          "           − trượt giá",
          "           − bất định mô hình",
          "           − biên an toàn     chỗ trả giá cho thứ chưa nghĩ ra"
        ],
        p: "Với sổ lệnh ở phòng bên: “EDGE 9¢” thành <b>+5,2¢</b> ở 80 cổ, <b>+2,2¢</b> ở 680 cổ, và <b>ÂM</b> nếu ăn cả sổ."
      },
      {
        h: "Maker hay taker đủ để lật lãi thành lỗ",
        p: "Polymarket không thu phí maker và có chương trình maker rebate; phí taker trên crypto market phụ thuộc giá và cao nhất quanh mức 50¢, về gần 0 ở hai đầu bảng.",
        p2: "Nên cặp <b>UP 32,9¢ + DOWN 66,2¢ = 99,1¢</b> cho gross 0,9¢ mỗi cặp. Lao vào ăn cả hai chân bằng lệnh thị trường là mất sạch vào phí taker và trượt giá — một giao dịch <b>lỗ</b> trong khi bảng điều khiển khoe “+0,9¢ arbitrage”. Cũng đúng cặp ấy mà đặt limit chờ khớp thì kinh tế học khác hẳn."
      }
    ]
  },

  {
    ma: "kho-doi",
    ten: "Kho Đối",
    phu: "chỗ bot sống chết sau cú khớp đầu tiên",
    icon: '<path d="M3.5 20.5h17M5.5 20.5V10h5v10.5M13.5 20.5V6h5v14.5"/>',
    tom: "Bot định hướng có một chân. Bot thị trường tiên đoán có hai chân phải khớp — và vấn đề lớn nhất bắt đầu sau cú khớp đầu tiên.",
    doan: [
      {
        h: "Kịch bản",
        cong: [
          "đặt  UP 45¢ + DOWN 49¢   →  cặp 94¢, nhìn như arbitrage",
          "UP    khớp 100%",
          "DOWN  khớp  18%",
          "chợ dịch, DOWN thành 56¢",
          "",
          "bây giờ không có arbitrage nào cả."
        ],
        p: "Còn lại là <b>82% một vị thế định hướng trần trụi</b> mà không ai định mở. Mô hình định giá không hề sai. Hỏng nằm ở khâu thi hành."
      },
      {
        h: "Nên tồn kho phải tách làm ba",
        bang: [
          ["đã ghép cặp", "min(UP, DOWN) — payoff đã cố định, chỉ còn hỏi giá cặp"],
          ["định hướng", "UP − DOWN — thiên lệch có chủ ý"],
          ["chưa phòng hộ", "chân chờ chân kia — <b>rủi ro thật</b>, và đang chạy đồng hồ"]
        ],
        p: "Phần thứ ba có đồng hồ riêng, và quá hạn chờ thì runtime ngừng mở vị thế mới cho tới khi dọn xong."
      },
      {
        h: "“Đã phòng hộ 91%” là một con số nói dối",
        canh: true,
        p: "Giữ cả hai chiều <b>không</b> tự động nghĩa là an toàn. Giá vốn UP 55¢ + DOWN 49¢ = <b>$1,04 một cặp</b>, mà cặp đó chỉ trả về đúng $1 khi kết toán.",
        p2: "Phần “đã phòng hộ” ấy đang khoá sẵn <b>4¢ lỗ</b>, và phần định hướng còn lại phải gỡ đủ chừng ấy trước khi cả vị thế mới hoà. Nên bảng điều khiển ở đây khoe <b>giá cặp</b> chứ không khoe phần trăm đã phòng hộ."
      },
      {
        h: "Và bốn market nhỏ có thể là một cược to",
        p: "BTC 5m, BTC 15m, ETH 5m, SOL 5m — bốn hợp đồng riêng, mỗi cái $800. Nếu cả bốn cùng long thì thực chất đó là <b>một cược $3.200 vào crypto</b>, và lúc cả thị trường lao xuống thì cả bốn cùng chết.",
        p2: "Trần đặt trên từng market không chặn được tình huống đó. Nên có thêm trần theo <b>nhóm tài sản</b>, và phơi nhiễm gộp được đo qua ma trận tương quan chứ không cộng thẳng."
      }
    ]
  },

  {
    ma: "sau-ngon",
    ten: "Sáu Ngón Nghề",
    phu: "sáu chiến thuật cắm vào một nền máy",
    icon: '<path d="M6 20V9M10 20V4M14 20v-9M18 20V7"/><path d="M3 20h18"/>',
    tom: "Không xây sáu con bot. Xây một nền máy rồi cắm sáu chiến thuật vào — chúng dùng chung mọi phép đo nên so sánh được với nhau.",
    ngon: [
      {
        t: "Lệch giá định hướng",
        d: "Mô hình định giá cao hơn chợ đang bán. Mua bên đó.",
        r: "Ngón cơ bản nhất. Chỉ chạy khi mô hình tự nhận là rõ ràng."
      },
      {
        t: "Cặp theo thời",
        d: "Gom DOWN lúc rẻ, đợi chợ đảo rồi gom UP lúc rẻ. Cặp chưa từng tồn tại cùng lúc trong sổ — bot dựng nó từ hai thời điểm.",
        r: "<b>Bẫy lớn nhất:</b> mua DOWN ở 27¢ chưa phải arbitrage. Nó là vị thế DOWN trần trụi cho tới khi UP được mua. BTC cứ đi lên tới hết giờ thì UP rẻ không bao giờ tới."
      },
      {
        t: "Cặp tức thì",
        d: "UP + DOWN cùng lúc dưới $1 ngay trong sổ. Payoff cố định ngay khi hai chân khớp.",
        r: "Hiếm, và hiếm là đúng — nếu dễ thì đã không còn. Vẫn phải trừ phí: cặp 99,1¢ bằng lệnh thị trường là giao dịch lỗ."
      },
      {
        t: "Định hướng có phòng hộ",
        d: "260 UP + 235 DOWN = 235 cặp cộng 25 UP định hướng. Lõi đã cố định, phần nhỏ là chỗ mô hình được nói.",
        r: "Chỉ mở khi giá cặp hiện tại còn dưới trần. Cặp đang khoá lỗ mà đắp thêm là đào sâu hố."
      },
      {
        t: "Tạo lập",
        d: "Yết limit hai bên quanh fair value, ăn spread, không đoán hướng. Maker không trả phí và có thể nhận rebate.",
        r: "Giá yết phải <b>lệch theo tồn kho</b>, không đối xứng. Đang thừa UP thì UP kém hấp dẫn đi, DOWN có giá trị hơn vì nó kéo tồn kho về cân."
      },
      {
        t: "Cận kết quả",
        d: "Mua bên gần chắc thắng ở 98,7¢, đợi về $1. Lãi 1,3¢ mỗi lượt.",
        r: "<b>Ngón nguy hiểm nhất.</b> Điểm hoà vốn là tỉ lệ thắng <b>98,7%</b>. Thắng 99% thì có lãi nhưng mỏng dính; tụt xuống 98% là lỗ. Cả chiến lược sống trên một dải rộng đúng một điểm phần trăm — mà sai số đo tỉ lệ thắng từ vài trăm lượt còn rộng hơn thế."
      }
    ],
    doan: [
      {
        h: "Và bốn nguyên nhân thua không phải rủi ro thị trường",
        canh: true,
        p: "Ngón cận-kết-quả thua vì một cú BTC ở giây chót — nhưng cũng vì <b>sai nguồn giá kết toán</b>, <b>sai giá mở</b>, <b>hiểu sai luật kết toán</b>, hoặc <b>không kịp huỷ một lệnh limit</b>.",
        p2: "Bốn cái sau là rủi ro <b>vận hành</b>, và không mô hình xác suất nào bắt được chúng. Đó là lý do tỉ lệ thắng 99,7% trên một bảng điều khiển không nói lên điều gì về an toàn."
      }
    ]
  },

  {
    ma: "quan-vi",
    ten: "Đài Quan Ví",
    phu: "quan sát được gì thì nói cái đó",
    icon: '<circle cx="12" cy="12" r="3"/><path d="M2 12s3.6-6.5 10-6.5S22 12 22 12s-3.6 6.5-10 6.5S2 12 2 12z"/>',
    tom: "Nhìn các ví tần suất cao trên Polymarket. Không suy ra động cơ, không gán chiến lược, không sao chép lệnh của ai.",
    doan: [
      {
        h: "Một giới hạn không vượt qua được",
        canh: true,
        p: "Trên Polymarket, <b>đặt và huỷ lệnh diễn ra off-chain</b>. Nên dữ liệu blockchain của một ví không đủ để dựng lại toàn bộ vòng đời báo giá của nó. Ta thấy được các lần <b>KHỚP</b>, không thấy được các lần <b>YẾT rồi HUỶ</b>.",
        p2: "Hệ quả rất cụ thể: nói được “ví này khớp cả hai chiều trong 93% số market nó tham gia”. <b>Không</b> nói được “ví này là market maker” — vì phần lớn hoạt động của một market maker nằm ở những lệnh chưa bao giờ khớp."
      },
      {
        h: "Nên mỗi nhãn đều khai rõ nó nói được tới đâu",
        nhan: [
          {
            t: "Khớp hai chiều",
            co: "Ví này thường giữ cả UP lẫn DOWN trong cùng một market.",
            khong: "KHÔNG suy ra được đây là arbitrage hay market making."
          },
          {
            t: "Săn cận kết quả",
            co: "Phần lớn lệnh vào ở giá trên 90¢, tức sát lúc kết quả rõ.",
            khong: "KHÔNG suy ra được lãi hay lỗ — ngón này lãi đều rồi mất lớn một lần, và một lát cắt không thấy được lần đó."
          },
          {
            t: "Chuyên khung ngắn",
            co: "Hoạt động gần như chỉ ở market 5 và 15 phút.",
            khong: "KHÔNG suy ra được có dùng bot hay không — tần suất cao là gợi ý mạnh, không phải bằng chứng."
          },
          {
            t: "Tần suất cao",
            co: "Số lệnh quan sát được trong cửa sổ này rất lớn.",
            khong: "Cửa sổ API có giới hạn, nên đây là SÀN DƯỚI của hoạt động thật, không phải tổng."
          }
        ]
      },
      {
        h: "Và một chỗ dễ đọc nhầm con số của người khác",
        p: "Ảnh chụp một danh sách toàn chữ WIN <b>không</b> chứng minh 28.620 lệnh đều thắng — một danh sách đã lọc thì chỉ nói lên rằng bộ lọc hoạt động.",
        p2: "Chính những ảnh được đem đi khoe cũng tự mâu thuẫn: một ảnh ghi “giá vào toàn bộ chỉ 2–10 cent” trong khi ảnh kế bên hiện 43,6¢ / 53,9¢ / 59,7¢. Và một tài khoản được gọi là máy in tiền lại hiện <b>tỉ lệ thắng 51,0%</b> ngay trên ảnh.",
        p3: "51% mà vẫn lãi lớn thì <b>không</b> phải nghịch lý — đó là điều bình thường khi kỳ vọng dương. Nghịch lý chỉ xuất hiện khi người ta tưởng tỉ lệ thắng là thước đo."
      }
    ]
  },

  {
    ma: "truong-thi",
    ten: "Trường Thi",
    phu: "trước khi tin, phải đối chiếu",
    icon: '<path d="M3.5 20.5h17M6 20.5V13M10.5 20.5V8M15 20.5v-9M19.5 20.5V4"/>',
    tom: "Mô hình nói 60% thì thực tế những lần nói 60% thắng bao nhiêu phần trăm? Chưa trả lời được câu đó thì chưa ai được dùng Kelly.",
    doan: [
      {
        h: "Kelly khuếch đại chính sai lầm của mô hình",
        p: "Kelly phân số là cách chia vốn hợp lý — <b>với điều kiện</b> xác suất đúng. Mô hình nói 60% mà thực tế những lần ấy chỉ thắng 52% thì Kelly phóng to đúng khoảng lệch đó, và càng tự tin sai thì càng đặt to.",
        p2: "Nên Kelly bị <b>khoá cứng</b> cho tới khi đủ mẫu đã đối chiếu. Trước đó runtime chỉ dùng lô sàn cố định. Mô hình tự tin 99% cũng không mở được cửa này."
      },
      {
        h: "Ranh giới trung tâm",
        cong: [
          "Chiến thuật ĐỀ XUẤT.  Risk Engine QUYẾT.",
          "",
          "Độ tin cậy chỉ dùng để TỪ CHỐI,",
          "không bao giờ dùng để NỚI."
        ],
        p: "Risk Engine là Python thuần, không gọi model, và có quyền phủ quyết tuyệt đối. Nó chặn theo mười một cửa: cầu dao, sức khoẻ nguồn, sổ lệnh quá cũ, đồng hồ lệch, sắp hết giờ, trần vốn mỗi market, trần vốn mỗi nhóm tài sản, trần tiền nằm trần một chân, chân quá hạn chờ, trần lệnh thật, và lợi kỳ vọng sau khi siết."
      },
      {
        h: "Băng ghi phải làm trước mô hình",
        p: "Không lưu sổ lệnh và tick ngay từ đầu thì ba tháng nữa dù muốn nghiên cứu cũng <b>không có ký ức thế giới nào để chạy lại</b>. Mô hình viết sau lúc nào cũng được; dữ liệu thì không quay lại.",
        p2: "Và không có chạy lại thì không có cách nào biết một thay đổi là <b>tốt hơn</b> hay chỉ là <b>khác đi</b>."
      },
      {
        h: "Lộ trình — và mốc duy nhất chạm tới tiền",
        lotrinh: [
          ["P0", "Băng ghi Binance + Polymarket + đồng hồ", "không giao dịch"],
          ["P1", "Sổ lệnh CLOB, tìm khung, dữ liệu kết toán", "không giao dịch"],
          ["P2", "Fair value nền + hiệu chỉnh", "không giao dịch"],
          ["P3", "Net executable edge + VWAP + phí + sức chứa", "không giao dịch"],
          ["P4", "Chạy lại lịch sử theo sự kiện", "không chạy thật"],
          ["P5", "Tồn kho + rủi ro chân + tương quan", "sổ giấy"],
          ["P6", "Lệch giá định hướng + cặp theo thời", "sổ giấy"],
          ["P7", "Giá trị tương đối + tạo lập + cận kết quả", "sổ giấy"],
          ["P8", "Đài Quan Ví", "chỉ nghiên cứu"],
          ["P9", "Champion/Challenger từng chiến thuật", "chạy bóng"],
          ["P10", "Thật, rất nhỏ, nếu MỌI cửa đều đạt", "trần cứng"]
        ],
        p: "Mốc P10 đứng sau P4 và P9 là có lý do: chưa đo được net edge thật sau phí thì chưa biết mình có gì trong tay."
      }
    ]
  }
];
