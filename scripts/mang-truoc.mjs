/* ═══════════════════════════════════════════════════════
   ĐỌC KHAI BÁO MẠNG-TRƯỚC TỪ MỘT sw.js — một chỗ duy nhất.

   File nào được service worker phục vụ MẠNG-TRƯỚC thì miễn luật
   nâng CACHE_VERSION: sw đi lấy bản mới mỗi lần, cache chỉ là lưới
   đỡ lúc mất mạng. Bot ghi 4 lượt/ngày mà bắt nâng version 4
   lượt/ngày thì phép kiểm hoá thành tiếng ồn.

   `npm run kiem` và `npm run nang` đều cần biết điều đó, và trước
   file này CHÚNG CHÉP CÙNG MỘT REGEX ở hai nơi — đúng kiểu hai bản
   sao của một sự thật mà CLAUDE.md cấm. Nay một chỗ.

   ── VÌ SAO PHẢI BIẾT "KHÔNG ĐỌC ĐƯỢC" ─────────────────
   Chuyện đã xảy ra ngày 20/08/2026: `dai-quan-trac/sw.js` khai
   mạng-trước bằng một MẢNG rồi lặp qua nó —

       var MANG_TRUOC = ["/assets/js/scan.js", …];
       if (MANG_TRUOC.some(function (p) {
             return url.pathname.indexOf(p) !== -1; })) { … }

   — nên đối số của `indexOf` là biến `p`, không phải chuỗi. Bản cũ
   chỉ bắt chuỗi nằm thẳng trong lời gọi, rút ra ĐÚNG KHÔNG ĐƯỜNG
   NÀO, rồi kết luận chắc nịch "CACHE_VERSION chưa nâng". Sai, và
   sai lại sau MỖI lượt bot ghi scan.js.

   Cái giá thật không phải một dòng báo thừa. Cảnh báo báo nhầm đều
   đặn thì người ta bỏ qua cảnh báo — rồi bỏ qua luôn lần nó đúng.
   Đó chính là kiểu hỏng mà cả bộ kiểm này sinh ra để chặn.

   Nên hàm này trả về `docDuoc`. Rút ra không đường nào KHÔNG có
   nghĩa là "cung này không có file mạng-trước"; nó có nghĩa là
   "tôi không đọc được", và hai câu đó phải khác nhau. Bên gọi dùng
   `docDuoc` để nói "không đọc được khai báo" thay vì buộc tội oan.

   ── THÊM MỘT DẠNG KHAI BÁO THỨ BA ─────────────────────
   Thêm một nhánh nhận dạng ở dưới, và thêm một cung mẫu vào phần
   chú thích. Đừng "sửa" bằng cách đổi sw.js của cung cho vừa bộ
   kiểm — bộ kiểm phải theo được mã thật, không phải ngược lại.
   ═══════════════════════════════════════════════════════ */

/* Hai dạng đang dùng thật trong repo:

     dạng CHUỖI THẲNG — chín cung
       url.pathname.indexOf("/assets/js/v/") !== -1

     dạng MẢNG — dai-quan-trac
       var MANG_TRUOC = ["/assets/js/scan.js", "/assets/js/do.js"];
       MANG_TRUOC.some(function (p) { return url.pathname.indexOf(p) !== -1; })
*/
export function docMangTruoc(sw) {
  /* CẮT CHÚ THÍCH TRƯỚC. Cả hai phép dò dưới đây rút chuỗi trong
     ngoặc kép, nên một câu giải thích có cụm trong ngoặc kép sẽ bị
     nhặt thành một đường dẫn — rồi phép `every(startsWith("/"))`
     trượt và bộ kiểm kết luận "không đọc được khai báo".

     Đã cắn thật ở dai-quan-trac: chú thích ngay trong mảng dẫn lại
     lời của knowledge-os, có dấu ngoặc kép, và cả cung bị báo là
     không khai được mạng-trước.

     CLAUDE.md đã dặn: công cụ phải theo được mã thật, đừng bẻ mã cho
     vừa công cụ. Chú thích trong mảng là mã hợp lệ. */
  sw = sw.replace(/\/\*[\s\S]*?\*\//g, " ").replace(/(^|[^:])\/\/.*$/gm, "$1 ");
  const duong = new Set();

  /* dạng chuỗi thẳng */
  for (const m of sw.matchAll(/indexOf\(\s*"([^"]+)"\s*\)/g)) duong.add(m[1]);

  /* dạng mảng — và đây là chỗ dễ làm sai, đã làm sai một lần:
     `indexOf(p)` cho tên THAM SỐ CALLBACK (`p`), không phải tên mảng
     (`MANG_TRUOC`). Đi từ `p` là đi vào ngõ cụt.

     Nên lần ngược từ khai báo mảng, và chỉ nhận mảng thoả CẢ BA:
       · mọi phần tử là chuỗi bắt đầu bằng "/"  → là đường dẫn
       · có ít nhất một phần tử
       · tên mảng có được lặp bằng .some/.find/.filter ở đâu đó

     Ba điều kiện cùng lúc để không nuốt nhầm mảng SHELL: phần tử của
     SHELL bắt đầu bằng "./" chứ không phải "/", và SHELL được duyệt
     bằng .map chứ không phải .some. Sai hướng nào cũng nguy: nuốt
     nhầm SHELL là MIỄN TRỪ TOÀN BỘ cung khỏi luật nâng version, tức
     là tắt hẳn phép kiểm mà vẫn in dấu ✓. */
  for (const m of sw.matchAll(/(?:var|let|const)\s+([A-Za-z_$][\w$]*)\s*=\s*\[([\s\S]*?)\]/g)) {
    const ten = m[1];
    const chuoi = [...m[2].matchAll(/"([^"]+)"/g)].map((x) => x[1]);
    if (!chuoi.length || !chuoi.every((s) => s.startsWith("/"))) continue;
    if (!new RegExp(ten + "\\s*\\.\\s*(?:some|find|filter)\\s*\\(").test(sw)) continue;
    for (const s of chuoi) duong.add(s);
  }

  return { duong: [...duong], docDuoc: duong.size > 0 };
}

/* Đường `f` (tương đối trong thư mục cung, không có "./") có được
   phục vụ mạng-trước không. Cùng phép so mà kiem và nang vẫn dùng:
   khớp theo chuỗi con, nên "/assets/js/v/" phủ cả thư mục. */
export function laMangTruoc(duong, f) {
  return duong.some((p) => ("/" + f).indexOf(p) !== -1);
}

/* ĐỌC DANH SÁCH SHELL TỪ MỘT sw.js — cũng một chỗ duy nhất.

   Trước hàm này, BỐN script chép cùng một regex neo đầu dòng:
   build-dist.mjs, kiem-quy-trinh.mjs, nang-version.mjs, tien-hoa.mjs.
   Neo `^` nghĩa là trên một dòng có HAI đường thì chỉ thấy đường
   thứ nhất. dai-quan-trac viết

       "./assets/js/trang/dong.js", "./assets/js/trang/bang.js",

   nên bang.js và nen.js — 30 KB, hai trong bốn file vẽ — vô hình với
   cả bốn. Hậu quả xếp theo mức: sửa hai file ấy KHÔNG nâng
   CACHE_VERSION nên máy đã cài giữ bản cũ mãi; chúng không vào bản
   dist; và thước 'vỏ dưới 200 KB' đếm thiếu chúng, tức báo vỏ nhẹ
   hơn thật.

   Không cái nào ném lỗi. Bốn công cụ cùng im lặng theo cùng một
   kiểu, vì chúng là bốn bản sao của một sự thật.

   Cắt đúng khối `var SHELL = [ … ]` rồi mới quét, để không nhặt
   nhầm đường nằm ở chỗ khác trong file. */
export function docShell(sw) {
  /* Cắt bằng indexOf chứ không bằng regex nhiều dấu thoát: đoạn mã
     này đã hỏng một lượt vì dấu thoát bị nuốt lúc ghi file, và nó
     hỏng THẦM — regex vẫn hợp lệ, chỉ là khớp sai. */
  const i = sw.indexOf("var SHELL");
  if (i < 0) return { duong: [], docDuoc: false };
  const j = sw.indexOf("[", i), k = sw.indexOf("]", j);
  if (j < 0 || k < 0) return { duong: [], docDuoc: false };
  /* Dấu + chứ không phải *: mục đầu của SHELL là "./" — chính trang gốc.
     Bắt nó thì mọi nơi gọi hàm này nhận thêm một đường RỖNG; bản kiểm thử
     cho thấy cả mười ba sw.js đều lệch đúng một mục ấy. */
  const re = new RegExp('"[.]/([^"]+)"', 'g');
  const duong = [...sw.slice(j, k).matchAll(re)].map((m) => m[1]);
  return { duong, docDuoc: duong.length > 0 };
}
