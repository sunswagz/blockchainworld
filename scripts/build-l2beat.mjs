/* ═══════════════════════════════════════════════════════
   Sinh dữ liệu cho Đô Sát Viện từ L2BEAT.

   Chạy tay:      npm run l2beat
   Chạy tự động:  .github/workflows/refresh-data.yml

   ── HAI NGUỒN, VÀ VÌ SAO PHẢI CẢ HAI ──────────────────

   1. API  /api/scaling/summary
        · tvs.breakdown, tvs.change7d, chart (chuỗi thời gian)
      Giao diện công khai, ổn định. Nhưng chỉ có mỗi trang tổng quan.

   2. HTML mỗi trang → window.__SSR_DATA__
        · toàn bộ 18 mục còn lại: rủi ro, kiểm chứng trạng thái,
          dữ liệu sẵn có, liên thông, quyền riêng tư, danh mục ZK,
          hệ sinh thái, và từ điển 120 thuật ngữ.
      Đây là dữ liệu nội bộ của trang, KHÔNG phải API cam kết.
      L2BEAT đổi cấu trúc trang là chỗ này gãy.

   Nguồn 1 BẮT BUỘC (số của trang tổng quan). Nguồn 2 hỏng từng
   mục thì mục đó giữ bản cũ và bị đánh dấu, chứ không xoá trắng
   và không làm hỏng cả lần chạy.

   ── XUẤT RA ───────────────────────────────────────────
     assets/js/data.js       chỉ mục chung: nhận dạng dự án, từ
                             điển, biểu đồ, danh sách mục
     assets/js/v/<mã>.js     dữ liệu riêng từng mục, NẠP THEO YÊU CẦU
     assets/logos/*.png      logo tải về, không hotlink

   Tách file vì gộp cả 18 mục vào một chỗ là ~2 MB — không thể
   bắt người mở trang tải hết chỉ để xem một bảng.
   ═══════════════════════════════════════════════════════ */

import { writeFile, mkdir, readFile, readdir, rm } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const DIR = join(ROOT, "do-sat-vien", "assets", "js");
const VDIR = join(DIR, "v");
const LOGOS = join(ROOT, "do-sat-vien", "assets", "logos");

const HOST = "https://l2beat.com";
const UA = "do-sat-vien-databot";

const log = (...a) => console.log(...a);
const warn = (...a) => console.error("  ⚠", ...a);
const nghi = (ms) => new Promise((r) => setTimeout(r, ms));

/* ── lấy có thử lại ────────────────────────────────────
   L2BEAT nấp sau Cloudflare và trả "error code: 1015" khi bị gọi
   dồn. Cron 4 lần/ngày không bao giờ chạm ngưỡng; chạy tay liên
   tiếp thì có. */
async function lay(url, kieu) {
  for (let lan = 1; lan <= 3; lan++) {
    try {
      const res = await fetch(url, { headers: { "user-agent": UA } });
      const txt = await res.text();
      if (!res.ok) throw new Error("HTTP " + res.status);
      if (/^error code: \d+/.test(txt)) throw new Error(txt.trim().slice(0, 40));
      return kieu === "json" ? JSON.parse(txt) : txt;
    } catch (e) {
      if (lan === 3) throw e;
      warn(`${url} lỗi (${e.message}) — thử lại lần ${lan + 1} sau ${lan * 5}s`);
      await nghi(lan * 5000);
    }
  }
}

async function laySSR(duong) {
  const html = await lay(HOST + duong, "text");
  const dau = html.indexOf("window.__SSR_DATA__=");
  if (dau === -1) throw new Error("không thấy window.__SSR_DATA__");
  const i = dau + "window.__SSR_DATA__=".length;
  const cuoi = html.indexOf("</script>", i);
  const d = JSON.parse(html.slice(i, cuoi).trim().replace(/;$/, ""));
  if (!d || !d.props) throw new Error("thiếu props");
  return d;
}

/* ── tiện ích cắt gọn ──────────────────────────────────
   Giữ đúng thứ sẽ vẽ ra màn hình. Mỗi trang SSR nặng 200 KB–1,6 MB
   mà phần dùng được chỉ vài chục KB. */
const lay1 = (o, p) => String(p).split(".").reduce((a, k) => (a == null ? a : a[k]), o);

/* khối nhận dạng — giống nhau ở mọi trang, gom về data.js một lần */
function nhanDang(p) {
  return {
    id: p.id,
    ten: p.name,
    ten2: p.nameSecondLine || null,
    slug: p.slug || p.id,
    logo: p.icon ? String(p.icon).replace(/^.*\/static\/icons\//, "") : null,
    l3: !!p.isLayer3,
    tab: p.tab || null,
    moTa: p.description || null,
    xemXet: !!(p.statuses && p.statuses.underReview),
    baoDong: !!(p.statuses && p.statuses.ongoingAnomaly)
  };
}

/* rủi ro: {value, sentiment, description, secondLine} → gọn */
function rr(x) {
  if (!x) return null;
  return {
    v: x.value ?? null,
    v2: x.secondLine ?? null,
    s: x.sentiment ?? null,
    d: x.description ?? null
  };
}
/* Rủi ro tới ở HAI hình khác nhau tuỳ trang:
     · mảng  [{name, value, sentiment, description}]        — scaling, DA tổng quan
     · object {economicSecurity: {value, sentiment, …}, …}  — DA rủi ro, DA đã ngừng
   Nhận cả hai và trả về một mảng thống nhất; khoá của object thành
   tên chiều (camelCase giữ nguyên, phần dịch nằm ở glossary.js). */
function rrArr(a) {
  if (!a) return [];
  if (Array.isArray(a)) {
    return a.map((r) => ({ n: r.name, v: r.value, v2: r.secondLine ?? null, s: r.sentiment, d: r.description || "" }));
  }
  if (typeof a === "object") {
    return Object.entries(a).map(([k, r]) => ({
      n: (r && r.name) || k,
      v: r?.value ?? null, v2: r?.secondLine ?? null,
      s: r?.sentiment ?? null, d: r?.description || ""
    }));
  }
  return [];
}
/* {value, change, changePeriod} → gọn */
function so(x) {
  if (!x || typeof x.value !== "number") return null;
  return { v: x.value, d: typeof x.change === "number" ? x.change : null, ky: x.changePeriod || null };
}

/* ══════════════════════════════════════════════════════
   ĐỊNH NGHĨA CÁC MỤC
   Mỗi mục: mã, đường dẫn L2BEAT, và hàm rút gọn.
   `rut` trả về { muc: [...] } hoặc { ...bất kỳ } tuỳ mục.
   ══════════════════════════════════════════════════════ */

/* gom entries dạng {rollups, validiumsAndOptimiums, others} hoặc mảng phẳng */
function gomEntries(props, khoa = "entries") {
  const e = lay1(props, khoa);
  if (Array.isArray(e)) return e;
  if (e && typeof e === "object") {
    const ra = [];
    for (const [tab, arr] of Object.entries(e)) {
      if (Array.isArray(arr)) for (const x of arr) ra.push({ ...x, tab: x.tab || tab });
    }
    return ra;
  }
  return [];
}

const MUC = [
  {
    ma: "rui-ro",
    duong: "/scaling/risk",
    ten: "Rủi ro · tổng hợp",
    rut: (p) => ({
      muc: gomEntries(p).map((x) => ({
        id: x.id,
        rr: {
          xepLich: rr(x.risks?.sequencerFailure),
          kiemChung: rr(x.risks?.stateValidation),
          duLieu: rr(x.risks?.dataAvailability),
          cuaThoat: rr(x.risks?.exitWindow),
          chotSo: rr(x.risks?.proposerFailure)
        },
        tvsOrder: x.tvsOrder ?? null
      }))
    })
  },
  {
    ma: "kiem-chung",
    duong: "/scaling/risk/state-validation",
    ten: "Rủi ro · kiểm chứng trạng thái",
    rut: (p) => ({
      hopLe: (p.validity || []).map((x) => ({
        id: x.id, tvsOrder: x.tvsOrder ?? null,
        he: x.proofSystem ? { loai: x.proofSystem.type, ten: x.proofSystem.name } : null,
        isa: x.isa || null,
        soNghiLe: Array.isArray(x.trustedSetups) ? x.trustedSetups.length : 0
      })),
      lacQuan: (p.optimistic || []).map((x) => ({
        id: x.id, tvsOrder: x.tvsOrder ?? null,
        he: x.proofSystem ? { loai: x.proofSystem.type, ten: x.proofSystem.name, gt: x.proofSystem.challengeProtocol || null } : null,
        treThiHanh: x.executionDelay ?? null,
        hanKhieuNai: x.challengePeriod ?? null,
        theChap: x.initialBond?.value ?? null,
        xinPhep: !!x.permissioned
      })),
      khongCM: (p.noProofs || []).map((x) => ({ id: x.id, tvsOrder: x.tvsOrder ?? null }))
    })
  },
  {
    ma: "du-lieu",
    duong: "/scaling/risk/data-availability",
    ten: "Rủi ro · dữ liệu sẵn có",
    rut: (p) => ({
      muc: gomEntries(p).map((x) => {
        const da = (x.dataAvailability || [])[0] || {};
        return {
          id: x.id,
          lop: rr(da.layer),
          cau: rr(da.bridge),
          che: da.mode ? { v: da.mode.value, v2: da.mode.secondLine || null } : null,
          dang: x.dataPosted ? { v: x.dataPosted.pastDay, d: x.dataPosted.change ?? null, ky: x.dataPosted.changePeriod || null } : null,
          he: x.proofSystem ? { loai: x.proofSystem.type, ten: x.proofSystem.name } : null
        };
      })
    })
  },
  {
    ma: "xep-thu-tu",
    duong: "/scaling/risk/sequencing",
    ten: "Rủi ro · xếp thứ tự giao dịch",
    rut: (p) => ({
      muc: (p.entries || []).map((x) => ({
        id: x.id,
        soXepLich: rr(x.sequencerCount),
        quyenTaoKhoi: rr(x.blockProductionAccess),
        dieuKienVao: rr(x.entryPolicy),
        nhipKhoi: rr(x.blockTime),
        luanPhien: rr(x.rotation),
        cachTaoKhoi: rr(x.blockProduction)
      }))
    })
  },
  {
    ma: "hoat-dong",
    duong: "/scaling/activity",
    ten: "Hoạt động",
    rut: (p) => ({
      muc: gomEntries(p).map((x) => ({
        id: x.id,
        dang: x.type || null,
        uops: so(x.data?.uops?.pastDayCount),
        tps: so(x.data?.tps?.pastDayCount),
        gop30d: so(x.data?.uops?.summedCount),
        dinh: x.data?.uops?.maxCount?.value ?? null,
        dinhLuc: x.data?.uops?.maxCount?.timestamp ?? null,
        dongBo: x.data?.isSynced !== false
      }))
    })
  },
  {
    ma: "do-song",
    duong: "/scaling/liveness",
    ten: "Độ sống",
    rut: (p) => {
      const g = (o) => o ? { tb: o.averageInSeconds ?? null, min: o.minimumInSeconds ?? null, max: o.maximumInSeconds ?? null } : null;
      return {
        muc: gomEntries(p).map((x) => ({
          id: x.id,
          dang: x.category || null,
          he: x.proofSystem ? { loai: x.proofSystem.type, ten: x.proofSystem.name } : null,
          capNhat30d: g(x.data?.stateUpdates?.["30d"]),
          goiLo30d: g(x.data?.batchSubmissions?.["30d"]),
          canhBao: x.data?.stateUpdates?.warning || null,
          giaiThich: x.explanation || null,
          dongBo: x.data?.isSynced !== false
        }))
      };
    }
  },
  {
    ma: "luu-tru",
    duong: "/scaling/archived",
    ten: "Đã ngừng hoạt động",
    rut: (p) => ({
      muc: gomEntries(p).map((x) => ({
        id: x.id,
        dang: x.type || null,
        he: x.proofSystem ? { loai: x.proofSystem.type, ten: x.proofSystem.name } : null,
        mucDich: x.purposes || [],
        stacks: x.stacks || [],
        ruiRo: rrArr(x.risks)
      }))
    })
  },

  /* ── dữ liệu sẵn có ── */
  {
    ma: "dl-tong-quan",
    duong: "/data-availability/summary",
    ten: "Dữ liệu sẵn có · tổng quan",
    rut: (p) => {
      const m = (x, cong) => ({
        id: x.id, ten: x.name, ten2: x.nameSecondLine || null,
        logo: x.icon ? String(x.icon).replace(/^.*\/static\/icons\//, "") : null,
        moTa: x.description || null,
        cong,
        anNinhKinhTe: x.economicSecurity ?? null,
        tvs: x.tvs?.latest ?? null,
        tvsTruoc: x.tvs?.sevenDaysAgo ?? null,
        coChe: x.challengeMechanism || null,
        ruiRo: rrArr(x.risks),
        cau: (x.bridges || []).map((b) => ({
          ten: b.name, tvs: b.tvs?.latest ?? null, ruiRo: rrArr(b.risks),
          dungBoi: (b.usedIn || []).map((u) => u.id)
        }))
      });
      return {
        muc: [...(p.publicSystems || []).map((x) => m(x, true)),
              ...(p.customSystems || []).map((x) => m(x, false))]
      };
    }
  },
  {
    ma: "dl-rui-ro",
    duong: "/data-availability/risk",
    ten: "Dữ liệu sẵn có · rủi ro",
    rut: (p) => {
      const m = (x, cong) => ({
        id: x.id, ten: x.name, ten2: x.nameSecondLine || null,
        logo: x.icon ? String(x.icon).replace(/^.*\/static\/icons\//, "") : null,
        cong, tvs: x.tvs?.latest ?? null, ruiRo: rrArr(x.risks),
        cau: (x.bridges || []).map((b) => ({ ten: b.name, ruiRo: rrArr(b.risks) }))
      });
      return {
        muc: [...(p.publicSystems || []).map((x) => m(x, true)),
              ...(p.customSystems || []).map((x) => m(x, false))]
      };
    }
  },
  {
    ma: "dl-thong-luong",
    duong: "/data-availability/throughput",
    ten: "Dữ liệu sẵn có · thông lượng",
    rut: (p) => ({
      muc: (p.entries || []).map((x) => ({
        id: x.id, ten: x.name, ten2: x.nameSecondLine || null,
        logo: x.icon ? String(x.icon).replace(/^.*\/static\/icons\//, "") : null,
        chungThuc: x.finality || null,
        dang24h: x.data?.pastDayData?.totalPosted ?? null,
        doi: x.data?.pastDayData?.change ?? null,
        tocDo: x.data?.pastDayData?.avgThroughputPerSecond ?? null,
        tran: x.data?.maxThroughputPerSecond ?? null,
        dangNhieuNhat: x.data?.pastDayData?.largestPoster
          ? { ten: x.data.pastDayData.largestPoster.name, pt: x.data.pastDayData.largestPoster.percentage } : null,
        chiL2: x.scalingOnlyData?.pastDayData?.totalPosted ?? null
      }))
    })
  },
  {
    ma: "dl-do-song",
    duong: "/data-availability/liveness",
    ten: "Dữ liệu sẵn có · độ sống",
    rut: (p) => ({
      muc: [...(p.publicSystems || []), ...(p.customSystems || [])].map((x) => ({
        id: x.id, ten: x.name, ten2: x.nameSecondLine || null,
        logo: x.icon ? String(x.icon).replace(/^.*\/static\/icons\//, "") : null,
        moTa: x.description || null,
        tvs: x.tvs?.latest ?? null,
        cau: (x.bridges || []).map((b) => ({ ten: b.name, tvs: b.tvs?.latest ?? null }))
      }))
    })
  },
  {
    ma: "dl-luu-tru",
    duong: "/data-availability/archived",
    ten: "Dữ liệu sẵn có · đã ngừng",
    rut: (p) => ({
      muc: [...(p.publicSystems || []).map((x) => ({ ...x, cong: true })),
            ...(p.customSystems || []).map((x) => ({ ...x, cong: false }))].map((x) => ({
        id: x.id, ten: x.name, ten2: x.nameSecondLine || null,
        logo: x.icon ? String(x.icon).replace(/^.*\/static\/icons\//, "") : null,
        cong: x.cong, moTa: x.description || null, ruiRo: rrArr(x.risks)
      }))
    })
  },

  /* ── liên thông ── */
  {
    ma: "lt-tong-quan",
    duong: "/interop/summary",
    ten: "Liên thông · tổng quan",
    rut: (p) => ({
      giaoThuc: (p.protocols || []).map((x) => ({
        id: x.id, ten: x.name, slug: x.slug,
        logo: x.iconUrl ? String(x.iconUrl).replace(/^.*\/static\/icons\//, "") : null
      })),
      chuoi: (p.interopChains || []).map((x) => ({
        id: x.id, ten: x.name, dang: x.type || null, mau: x.color || null,
        sapCo: !!x.isUpcoming,
        logo: x.iconUrl ? String(x.iconUrl).replace(/^.*\/static\/icons\//, "") : null
      }))
    })
  },
  {
    ma: "lt-khung-token",
    duong: "/interop/token-frameworks",
    ten: "Liên thông · khung token",
    rut: (p) => ({
      khung: (p.tokenFrameworks || []).map((x) => ({
        id: x.id, ten: x.name, nhan: x.label || null, mau: x.color || null,
        logo: x.iconUrl ? String(x.iconUrl).replace(/^.*\/static\/icons\//, "") : null
      }))
    })
  },
  {
    ma: "lt-cau-y-dinh",
    duong: "/interop/intent-bridges",
    ten: "Liên thông · cầu ý định",
    rut: (p) => ({
      cau: (p.intentBridges || []).map((x) => ({
        id: x.id, ten: x.name, moTa: x.description || null, mau: x.color || null,
        logo: x.iconUrl ? String(x.iconUrl).replace(/^.*\/static\/icons\//, "") : null,
        moHinh: rr(x.intentModel),
        cuuHoi: rr(x.userRecovery),
        quyenGiaiQuyet: rr(x.solverAccess),
        thanhToan: rr(x.settlement)
      }))
    })
  },

  /* ── quyền riêng tư ── */
  {
    ma: "rieng-tu",
    duong: "/privacy",
    ten: "Quyền riêng tư",
    rut: (p) => ({
      muc: (p.entries || []).map((x) => ({
        id: x.id, ten: x.name, slug: x.slug, moTa: x.description || null,
        logo: x.icon ? String(x.icon).replace(/^.*\/static\/icons\//, "") : null,
        xemXet: !!x.isUnderReview,
        tenMuc: x.summaryTrackedItemName || null,
        nghiLe: x.trustedSetup ? {
          ten: x.trustedSetup.name, rui: x.trustedSetup.risk || null,
          soNguoi: x.trustedSetup.participantCount ?? null,
          moTa: x.trustedSetup.shortDescription || null
        } : null,
        cuaThoat: rr(x.exitWindow),
        taiLap: rr(x.reproducibility),
        riengTu: x.privacy || null,
        thuocTinh: x.attributes || null
      }))
    })
  },

  /* ── danh mục ZK ── */
  {
    ma: "zk",
    duong: "/zk-catalog",
    ten: "Danh mục ZK",
    rut: (p) => {
      const bo = (a) => (a || []).map((t) => ({ id: t.id, dang: t.type, ten: t.name, moTa: t.description || null }));
      return {
        muc: (p.entries || []).map((x) => ({
          id: x.id, ten: x.name, slug: x.slug, moTa: x.description || null,
          logo: x.icon ? String(x.icon).replace(/^.*\/static\/icons\//, "") : null,
          tacGia: x.creator || null,
          tvs: x.tvs?.value ?? null,
          soDuAn: x.tvs?.numberOfProjects ?? null,
          zkVM: bo(x.techStack?.zkVM),
          boc: bo(x.techStack?.finalWrap),
          xemXet: !!(x.statuses && x.statuses.underReview)
        }))
      };
    }
  },

  /* ── hệ sinh thái ── */
  ...[
    ["st-arbitrum-orbit", "/ecosystems/arbitrum-orbit", "Hệ sinh thái · Arbitrum Orbit"],
    ["st-elastic", "/ecosystems/the-elastic-network", "Hệ sinh thái · The Elastic Network"],
    ["st-superchain", "/ecosystems/superchain", "Hệ sinh thái · Superchain"],
    ["st-agglayer", "/ecosystems/agglayer", "Hệ sinh thái · Agglayer"]
  ].map(([ma, duong, ten]) => ({
    ma, duong, ten,
    rut: (p) => {
      const e = p.ecosystem || {};
      const raas = [];
      for (const [ten2, o] of Object.entries(e.projectsByRaas || {})) {
        raas.push({ ten: ten2, duAn: (o.projects || []).map((x) => x.id) });
      }
      return {
        ten: e.name || null,
        moTa: e.description || (e.display && e.display.description) || null,
        mau: (e.colors && (e.colors.primary || e.colors.accent)) || null,
        duAnSong: (e.liveProjects || []).map((x) => (typeof x === "string" ? x : x.id)),
        raas,
        cotMoc: (e.allMilestones || []).slice(0, 24).map((m) => ({
          ten: m.title || m.name || null, ngay: m.date || null, moTa: m.description || null, url: m.url || null
        }))
      };
    }
  }))
];

/* ══════════════════════════════════════════════════════
   CHẠY
   ══════════════════════════════════════════════════════ */

/* bản cũ, để vá khi một mục hỏng */
/* File mục có HAI phép gán (`window.DSV_V = window.DSV_V || {};` rồi
   mới tới dữ liệu), nên phải neo vào đúng phép gán cuối — bắt từ dấu
   `=` đầu tiên sẽ nuốt luôn dòng khởi tạo và JSON.parse gãy. */
async function docCu(f) {
  if (!existsSync(f)) return null;
  try {
    const t = await readFile(f, "utf8");
    const m = t.match(/window\.DSV_V\[[^\]]*\]\s*=\s*([\s\S]*);\s*$/)
      || t.match(/window\.DSV_DATA\s*=\s*([\s\S]*);\s*$/);
    return m ? JSON.parse(m[1]) : null;
  } catch { return null; }
}

const cuChung = await docCu(join(DIR, "data.js"));

/* ── nguồn 1: API tổng quan (bắt buộc) ─────────────── */
let raw;
try {
  const t0 = Date.now();
  raw = await lay(HOST + "/api/scaling/summary", "json");
  log(`✓ API tổng quan  ${Date.now() - t0} ms`);
} catch (e) {
  console.error("Không gọi được API L2BEAT — " + e.message);
  if (cuChung) { console.error("Giữ nguyên bản cũ ngày " + cuChung.date + ", không ghi đè."); process.exit(0); }
  process.exit(1);
}
const apiList = Object.values(raw.projects || {});
if (!apiList.length) { console.error("API trả 0 dự án — không ghi đè."); process.exit(1); }

/* ── nguồn 2a: trang tổng quan (nhận dạng + tab) ────── */
let ssrTongQuan = null, tuDien = null;
try {
  await nghi(1500);
  const d = await laySSR("/scaling/summary");
  ssrTongQuan = {};
  for (const [tab, arr] of Object.entries(d.props.entries || {})) {
    if (Array.isArray(arr)) for (const x of arr) if (x && x.id) ssrTongQuan[x.id] = { ...x, tab };
  }
  /* Từ điển 120 thuật ngữ đi kèm MỌI trang — lấy ở đây một lần.
     Không có trường `term`: tên hiển thị là matches[0], các tên gọi
     khác (viết tắt) nằm ở phần đuôi. */
  tuDien = (d.props.terms || []).map((t) => ({
    id: t.id,
    ten: (t.matches || [])[0] || t.id || null,
    khop: (t.matches || []).slice(1),
    dn: t.description || null
  })).filter((t) => t.ten && t.dn);
  log(`✓ SSR tổng quan  ${Object.keys(ssrTongQuan).length} dự án · từ điển ${tuDien.length} thuật ngữ`);
} catch (e) {
  warn("Không đọc được SSR trang tổng quan (" + e.message + ").");
  warn("Logo / tab / hệ chứng minh sẽ lấy từ bản trước.");
}

const vaCu = {};
if (cuChung) for (const p of cuChung.duAn || []) vaCu[p.id] = p;

const TAB_VI = { rollups: "rollup", validiumsAndOptimiums: "validium", others: "khac" };

/* ── chỉ mục dự án dùng chung ──────────────────────── */
const duAn = apiList.map((p) => {
  const s = ssrTongQuan && ssrTongQuan[p.id];
  const c = vaCu[p.id];
  const nd = s ? nhanDang(s) : null;
  return {
    id: p.id,
    slug: p.slug || p.id,
    ten: p.name,
    loai: p.type,
    dang: p.category,
    thang: p.stage,
    me: p.hostChain,
    stack: (p.providers || [])[0] || null,
    tvs: p.tvs?.breakdown?.total ?? null,
    d7: typeof p.tvs?.change7d === "number" ? p.tvs.change7d : null,
    chiaTvs: p.tvs?.breakdown ? {
      native: p.tvs.breakdown.native ?? 0,
      canonical: p.tvs.breakdown.canonical ?? 0,
      external: p.tvs.breakdown.external ?? 0
    } : null,
    ruiRo: rrArr(p.risks),
    xemXet: !!p.isUnderReview,
    luuTru: !!p.isArchived,
    /* làm giàu từ SSR, hỏng thì vá từ bản cũ */
    tab: nd ? (TAB_VI[s.tab] || "khac") : (c?.tab || "khac"),
    logo: nd ? nd.logo : (c?.logo ?? null),
    moTa: nd ? nd.moTa : (c?.moTa ?? null),
    baoDong: nd ? nd.baoDong : !!c?.baoDong,
    heCM: s?.proofSystem
      ? { loai: s.proofSystem.type || null, ten: s.proofSystem.name || null, giaoThuc: s.proofSystem.challengeProtocol || null }
      : (c?.heCM ?? null),
    uops: s?.activity && typeof s.activity.pastDayUops === "number"
      ? { sl: s.activity.pastDayUops, doi: s.activity.change ?? null, ky: s.activity.changePeriod || null }
      : (c?.uops ?? null),
    thieu: s?.stage?.missing
      ? { thangSau: s.stage.missing.nextStage || null, dieuKien: s.stage.missing.requirements || [] }
      : (c?.thieu ?? null),
    stacks: s?.stacks || c?.stacks || []
  };
}).sort((a, b) => (b.tvs || 0) - (a.tvs || 0));

/* ── nguồn 2b: từng mục ────────────────────────────── */
await mkdir(VDIR, { recursive: true });
const dsMuc = [];

/* Chạy lại riêng vài mục:  npm run l2beat -- dl-rui-ro dl-luu-tru
   Mục không nêu tên thì giữ nguyên file cũ. Dùng khi Cloudflare
   chặn giữa chừng, khỏi phải gọi lại cả 21 trang. */
const chiMuc = process.argv.slice(2).filter((a) => !a.startsWith("-"));
if (chiMuc.length) log(`  (chỉ chạy lại: ${chiMuc.join(", ")})`);

for (const m of MUC) {
  const f = join(VDIR, m.ma + ".js");

  if (chiMuc.length && !chiMuc.includes(m.ma)) {
    const cu = await docCu(f);
    const so = cu ? (Array.isArray(cu.muc) ? cu.muc.length
      : Object.values(cu).filter(Array.isArray).reduce((a, x) => a + x.length, 0)) : null;
    dsMuc.push({ ma: m.ma, ten: m.ten, duong: m.duong, so, ok: !!cu, giuCu: true });
    continue;
  }

  await nghi(2200);
  try {
    const d = await laySSR(m.duong);
    const goi = m.rut(d.props);
    /* Số hiện cạnh mục ở thanh bên. Ưu tiên danh sách chính; cộng
       hết mọi mảng chỉ là đường lui, và với hệ sinh thái nó sẽ cộng
       nhầm cả mốc thời gian lẫn nhà dựng thuê vào số chuỗi. */
    const soMuc = Array.isArray(goi.muc) ? goi.muc.length
      : Array.isArray(goi.duAnSong) ? goi.duAnSong.length
      : Object.values(goi).filter(Array.isArray).reduce((a, x) => a + x.length, 0);
    const js = `/* TỰ SINH bởi scripts/build-l2beat.mjs — ĐỪNG SỬA TAY.\n` +
      `   Mục: ${m.ten}\n   Nguồn: l2beat.com${m.duong}\n */\n` +
      `window.DSV_V = window.DSV_V || {};\nwindow.DSV_V[${JSON.stringify(m.ma)}] = ${JSON.stringify(goi)};\n`;
    await writeFile(f, js, "utf8");
    dsMuc.push({ ma: m.ma, ten: m.ten, duong: m.duong, so: soMuc, ok: true });
    log(`  ✓ ${m.ma.padEnd(16)} ${String(soMuc).padStart(4)} mục · ${(js.length / 1024).toFixed(0)} KB`);
  } catch (e) {
    const con = existsSync(f);
    dsMuc.push({ ma: m.ma, ten: m.ten, duong: m.duong, so: null, ok: false, giuCu: con });
    warn(`${m.ma}: ${e.message}` + (con ? " — GIỮ bản cũ" : " — CHƯA có bản nào"));
  }
}

/* ── biểu đồ ───────────────────────────────────────── */
let bieuDo = null;
if (raw.chart && Array.isArray(raw.chart.data) && raw.chart.data.length) {
  bieuDo = { cot: raw.chart.types || [], diem: raw.chart.data };
  log(`  biểu đồ : ${bieuDo.diem.length} điểm · [${bieuDo.cot.join(", ")}]`);
} else {
  warn("API không trả chart — giữ biểu đồ bản trước.");
  bieuDo = cuChung?.bieuDo || null;
}

/* ── logo ──────────────────────────────────────────── */
/* Gom mọi tên file logo mà data.js và các mục nhắc tới. URL của
   L2BEAT có hash nội dung (base.4840b6b2.png) nên tên đổi = ảnh đổi;
   đã có file trùng tên thì bỏ qua. */
const canLogo = new Set();
for (const p of duAn) if (p.logo) canLogo.add(p.logo);
for (const m of dsMuc) {
  if (!m.ok) continue;
  try {
    const t = await readFile(join(VDIR, m.ma + ".js"), "utf8");
    /* '"logo":"' dài 8 ký tự — cắt từ 9 là mất ký tự đầu của tên file
       và mọi logo sẽ 404 ("agglayer…" thành "gglayer…"). */
    for (const s of t.match(/"logo":"([^"]+)"/g) || []) canLogo.add(s.slice(8, -1));
  } catch {}
}

await mkdir(LOGOS, { recursive: true });
const daCo = new Set(await readdir(LOGOS).catch(() => []));
let taiVe = 0, boQua = 0, hong = 0;
for (const ten of canLogo) {
  if (daCo.has(ten)) { boQua++; continue; }
  try {
    const res = await fetch(HOST + "/static/icons/" + ten, { headers: { "user-agent": UA } });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const buf = Buffer.from(await res.arrayBuffer());
    if (buf.length < 100) throw new Error("quá nhỏ, " + buf.length + " byte");
    await writeFile(join(LOGOS, ten), buf);
    taiVe++;
    await nghi(120);
  } catch (e) { warn(`logo ${ten}: ${e.message}`); hong++; }
}
log(`  logo    : ${taiVe} tải mới · ${boQua} đã có · ${hong} hỏng`);

/* ── ghi data.js ───────────────────────────────────── */
const now = new Date();
const pad = (n) => String(n).padStart(2, "0");
const out = {
  generatedAt: now.toISOString(),
  date: `${pad(now.getUTCDate())}/${pad(now.getUTCMonth() + 1)}/${now.getUTCFullYear()}`,
  nguon: "l2beat.com — API scaling/summary + dữ liệu trang",
  coSSR: !!ssrTongQuan,
  tongTvs: duAn.reduce((s, p) => s + (p.tvs || 0), 0),
  demTab: duAn.reduce((m, p) => { m[p.tab] = (m[p.tab] || 0) + 1; return m; }, {}),
  bieuDo,
  tuDien: tuDien || cuChung?.tuDien || [],
  dsMuc,
  duAn
};

const js = `/* ═══════════════════════════════════════════════════════
   TỰ SINH bởi scripts/build-l2beat.mjs — ĐỪNG SỬA TAY.
   Nguồn: ${out.nguon}
   Lấy lúc: ${out.generatedAt}
   ${duAn.length} dự án · tổng tài sản $${(out.tongTvs / 1e9).toFixed(2)}b
   ${out.tuDien.length} thuật ngữ · ${dsMuc.filter((m) => m.ok).length}/${dsMuc.length} mục lấy được
   Làm giàu từ SSR: ${out.coSSR ? "có" : "KHÔNG — logo/tab lấy từ bản trước"}
   ═══════════════════════════════════════════════════════ */
window.DSV_DATA = ${JSON.stringify(out)};
`;
await writeFile(join(DIR, "data.js"), js, "utf8");

/* ── thống kê ──────────────────────────────────────── */
const dem = (f) => duAn.reduce((m, p) => { const k = f(p) ?? "—"; m[k] = (m[k] || 0) + 1; return m; }, {});
const show = (o) => Object.entries(o).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k}=${v}`).join("  ");
log(`\n  ${duAn.length} dự án · tổng $${(out.tongTvs / 1e9).toFixed(2)}b`);
log("  tab   :", show(out.demTab));
log("  thang :", show(dem((p) => p.thang)));
log("  mục   :", dsMuc.filter((m) => m.ok).length + "/" + dsMuc.length + " lấy được");
const hongMuc = dsMuc.filter((m) => !m.ok);
if (hongMuc.length) warn("mục hỏng: " + hongMuc.map((m) => m.ma).join(", "));
log(`\n✓ đã ghi data.js · ${(js.length / 1024).toFixed(0)} KB  +  ${dsMuc.filter((m) => m.ok).length} file trong assets/js/v/`);
