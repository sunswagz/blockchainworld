(function () {
"use strict";

/* ══ bảng xếp hạng nội lực ════════════════════════════ */
/* Số đo: chụp từ DefiLlama ngày 10/08/2026. Cosmos và Polkadot là tổng cả hệ. */
var SNAP_DATE="10/08/2026";
var STRENGTH={
 eth :{tvl:41804e6, stab:147975e6, addr:932847,  proto:1961, dec:95,
       decNote:"Hơn một triệu validator, nhiều phần mềm node độc lập — không nhóm nào hạ được mạng."},
 bnb :{tvl:4968e6,  stab:13386e6,  addr:1850000, proto:1229, dec:35,
       decNote:"Chỉ vài chục validator, ảnh hưởng của Binance rất lớn. Đổi phi tập trung lấy tốc độ."},
 sol :{tvl:4854e6,  stab:15633e6,  addr:1940000, proto:588,  dec:60,
       decNote:"Hơn một nghìn validator nhưng đòi phần cứng nặng, quyền biểu quyết tập trung ở nhóm lớn."},
 atom:{tvl:2040e6,  stab:670e6,    addr:25000,   proto:900,  dec:75, partial:true,
       decNote:"Mỗi nước tự tuyển validator — chủ quyền cao nhất, nhưng nước nhỏ tự lo an ninh nên mong manh."},
 avax:{tvl:424e6,   stab:1572e6,   addr:622870,  proto:632,  dec:65,
       decNote:"Mạng chính đông validator, nhưng mỗi subnet tự tuyển người gác cổng của mình."},
 sui :{tvl:413e6,   stab:444e6,    addr:164682,  proto:147,  dec:55,
       decNote:"Khoảng trăm validator, hệ còn trẻ và đội sáng lập vẫn dẫn dắt kỹ thuật."},
 near:{tvl:98.7e6,  stab:78.1e6,   addr:84061,   proto:50,   dec:60,
       decNote:"Vài trăm validator, chia mảnh để mở rộng; quyền kỹ thuật còn tập trung."},
 ton :{tvl:60.1e6,  stab:3.01e6,   addr:118856,  proto:89,   dec:55,
       decNote:"Vài trăm validator, nhưng đường sống phụ thuộc gần như hoàn toàn vào Telegram."},
 dot :{tvl:59e6,    stab:2.75e6,   addr:2600,    proto:250,  dec:80, partial:true,
       decNote:"Validator relay chain bảo vệ chung cho mọi bang — bang nhỏ vẫn được che như bang lớn."}
};
var DIMS=[
 {k:"tvl",  w:25, n:"Vốn khoá",     d:"Tổng tài sản đang nằm trong các giao thức DeFi của nước đó.", meas:1, fmt:"usd"},
 {k:"stab", w:20, n:"Tiền lưu hành", d:"Vốn hoá stablecoin trên chuỗi — thước đo tiền thật đang chảy, không phải giá token.", meas:1, fmt:"usd"},
 {k:"addr", w:20, n:"Hoạt động",     d:"Số địa chỉ hoạt động trong 24 giờ. Đông dân không có nghĩa giàu, nhưng vắng thì chắc chắn yếu.", meas:1, fmt:"num"},
 {k:"proto",w:15, n:"Hệ sinh thái",  d:"Số giao thức đang chạy — độ dày của nền kinh tế, không phải quy mô của nó.", meas:1, fmt:"int"},
 {k:"dec",  w:20, n:"Phi tập trung", d:"Mức độ khó bị một nhóm nhỏ khống chế. Đây là đánh giá của tôi, không phải số đo.", meas:0, fmt:"score"}
];

/* cộng dồn cho hai hệ đa chuỗi */
var AGG={atom:["Provenance","Cronos","dYdX","Sei","THORChain","Kava","Osmosis","Injective","Neutron","Terra","Canto","Secret","MANTRA","Babylon Genesis","Noble","Stride","Archway"],
         dot:["Hydration","Bifrost","Astar","Moonriver","Moonbeam","Equilibrium","Acala","Interlay","Polkadex"]};
var NAMEMAP={eth:"Ethereum",bnb:"BSC",sol:"Solana",avax:"Avalanche",sui:"Sui",near:"Near",ton:"TON"};

window.KT_DATA = window.KT_DATA || {};
window.KT_DATA.SNAP_DATE = SNAP_DATE;
window.KT_DATA.STRENGTH  = STRENGTH;
window.KT_DATA.DIMS      = DIMS;
window.KT_DATA.AGG       = AGG;
window.KT_DATA.NAMEMAP   = NAMEMAP;
})();
