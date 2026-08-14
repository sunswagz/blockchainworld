# blockchainworld

Repo chứa Cổng Thành (`index.html` ở gốc) và năm cung, mỗi cung là một
webapp tĩnh độc lập có `index.html` riêng:

    cong-bo/  dai-quan-trac/  do-sat-vien/  kinh-thanh/  tang-thu-cac/

## Chạy song song nhiều phiên

Repo này thường có 2–4 phiên Claude Code chạy cùng lúc, mỗi phiên một
git worktree riêng, mỗi phiên lo một cung:

    claude --worktree cong-bo

Các cung tách thư mục hẳn nên file nguồn không đụng nhau. Chỗ duy nhất
thật sự dùng chung là `.git` và các file ở gốc repo — nên toàn bộ luật
dưới đây xoay quanh đúng hai thứ đó.

### Phạm vi sửa

- Chỉ sửa file bên trong thư mục cung được giao cho phiên này.
- **Không bao giờ `git add -A` hay `git add .`** — chỉ add đúng thư mục
  cung. Phiên khác có thể đang viết dở file của nó; `git add -A` sẽ nuốt
  luôn nửa việc chưa xong của họ vào commit của bạn.
- Không đụng file dùng chung ở gốc repo: `index.html`, `sw.js`,
  `manifest.webmanifest`, `assets/`, `scripts/`, `package.json`,
  `server.js`, `.github/workflows/`. Cần sửa thì dừng lại hỏi trước.
- Không merge, không rebase, không push lên `main`. Commit và push lên
  đúng nhánh worktree hiện tại; việc gộp để người dùng làm.

### File do workflow tự sinh — đừng sửa tay

Bốn đường dẫn này bị ghi đè mỗi 6 giờ bởi `refresh-data.yml` và
`scan-observatory.yml`, hai workflow commit thẳng vào `main`. Sửa tay là
chắc chắn conflict lúc merge:

    kinh-thanh/assets/js/data/live.js
    do-sat-vien/assets/js/data.js
    cong-bo/assets/js/
    tang-thu-cac/assets/js/data.js

Muốn đổi số liệu thì sửa script sinh ra chúng trong `scripts/`, không sửa
file kết quả. (Và sửa `scripts/` là file dùng chung — hỏi trước.)

Vì bot đẩy vào `main` liên tục, worktree phải nhánh từ `origin/main` chứ
không phải HEAD local. Đó là mặc định (`worktree.baseRef: fresh`); đừng
đổi sang `head`.

### Cổng dev

`server.js` phục vụ từ **gốc repo**, không phải từ thư mục cung — nên một
server là đủ để mở cả năm cung (`/cong-bo/`, `/kinh-thanh/`, …). Vì vậy
cổng cấp theo **luồng đang chạy**, không phải theo cung:

    5173  luồng 1 (mặc định — để cho bản checkout chính)
    5174  luồng 2
    5175  luồng 3
    5176  luồng 4

Luôn truyền cổng, đừng để mặc định:

    node server.js 5174

Dải 5173–5176 dành riêng cho repo này. Thêm bao nhiêu cung nữa cũng không
cần thêm cổng — số cổng đi theo số terminal mở song song, không theo số app.

### Không chạy trong phiên song song

    npm run dist     npm run deploy     npm run pin

Ba lệnh này dựng lại toàn bộ `dist/` và pin lên IPFS cho cả site. Chỉ chạy
sau khi đã gộp xong về `main`.

## Bẫy: paths filter làm deploy hỏng lặng lẽ

`deploy-pages.yml` và `deploy-ipfs.yml` chỉ chạy khi push vào `main` **và**
file thay đổi khớp danh sách `paths`. Danh sách đó liệt kê thủ công từng
cung, vì sau khi tách thư mục thì `assets/**` chỉ còn khớp assets của Cổng
Thành.

Thêm cung mới mà quên thêm đường dẫn của nó vào `paths` của **cả hai** file
thì: push thành công, không có lỗi nào, không có workflow nào chạy, và bản
trên site vẫn là bản cũ. Không có gì báo cho bạn biết.

Nhánh worktree không kích hoạt deploy — đúng như thiết kế, deploy xảy ra
lúc gộp vào `main`.
