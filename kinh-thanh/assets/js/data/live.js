/* ═══════════════════════════════════════════════════════
   TỰ SINH — ĐỪNG SỬA TAY.
   Sinh bởi scripts/build-live.mjs lúc 2026-09-09T20:59:27.140Z
   Sửa tay sẽ bị ghi đè ở lần cập nhật tự động kế tiếp.

   File này đè số đo lên bản chụp trong strength.js.
   Xoá file này đi thì app quay về dùng số chụp — vẫn chạy bình thường.
   ═══════════════════════════════════════════════════════ */
(function () {
"use strict";

/* KT_LIVE_BEGIN */
var LIVE = {
  "generatedAt": "2026-09-09T20:59:27.140Z",
  "date": "09/09/2026",
  "sources": {
    "tvl": "api.llama.fi/v2/chains",
    "stab": "stablecoins.llama.fi/stablecoinchains",
    "proto": "api.llama.fi/protocols (đếm giao thức theo chuỗi)",
    "cities": "l2beat.com/api/scaling/summary (stage, rủi ro, TVS)"
  },
  "frozen": {
    "addr": "Địa chỉ hoạt động 24h — chưa có nguồn miễn phí nào phủ cả 9 nước. Giữ số chụp trong strength.js.",
    "dec": "Phi tập trung — là đánh giá, không phải số đo. Không tự động hoá được."
  },
  "chains": {
    "eth": {
      "tvl": 49605353514,
      "stab": 147026431924,
      "proto": 1860
    },
    "bnb": {
      "tvl": 5737274578,
      "stab": 13294275267,
      "proto": 1131
    },
    "sol": {
      "tvl": 5940813989,
      "stab": 16143222837,
      "proto": 452
    },
    "avax": {
      "tvl": 494467462,
      "stab": 1455278464,
      "proto": 563
    },
    "sui": {
      "tvl": 481655961,
      "stab": 458794100,
      "proto": 125
    },
    "near": {
      "tvl": 147997703,
      "stab": 105112391,
      "proto": 45
    },
    "ton": {
      "tvl": 49593681,
      "stab": 771188539,
      "proto": 92
    },
    "atom": {
      "tvl": 498378710,
      "stab": 1203811839,
      "proto": 574
    },
    "dot": {
      "tvl": 65022486,
      "stab": 82328010,
      "proto": 215
    }
  },
  "cities": {
    "base": {
      "name": "Base Chain",
      "slug": "base",
      "stage": "Stage 1",
      "category": "Optimistic Rollup",
      "hostChain": "Ethereum",
      "providers": [
        "OP Stack"
      ],
      "tvs": 14786074624,
      "change7d": 0.06383162440559964,
      "risks": [
        {
          "n": "Sequencer Failure",
          "v": "Self sequence",
          "s": "good",
          "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
        },
        {
          "n": "State Validation",
          "v": "Fraud proofs (1R, ZK)",
          "s": "good",
          "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Single round proofs (1R) prove the validity of a state proposal, only requiring a single transaction to resolve. A fault proof eliminates a state proposal by proving that any intermediate state transition in the proposal results in a different state root. For either, a ZK proof is used."
        },
        {
          "n": "Data Availability",
          "v": "Onchain",
          "s": "good",
          "d": "All of the data needed for proof construction is published on Ethereum L1."
        },
        {
          "n": "Exit Window",
          "v": "None",
          "s": "bad",
          "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable. Upgrades need to be approved by 2 parties: the Base Coordinator Multisig and the Base Security Council."
        },
        {
          "n": "Proposer Failure",
          "v": "Self propose",
          "s": "good",
          "d": "Anyone can be a Proposer and propose new roots to the L1 bridge."
        }
      ]
    },
    "arbitrum one": {
      "name": "Arbitrum One",
      "slug": "arbitrum",
      "stage": "Stage 1",
      "category": "Optimistic Rollup",
      "hostChain": "Ethereum",
      "providers": [
        "Arbitrum"
      ],
      "tvs": 12482569216,
      "change7d": 0.04088337546531262,
      "risks": [
        {
          "n": "Sequencer Failure",
          "v": "Self sequence",
          "s": "good",
          "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 1d delay on this operation."
        },
        {
          "n": "State Validation",
          "v": "Fraud proofs (INT)",
          "s": "good",
          "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve."
        },
        {
          "n": "Data Availability",
          "v": "Onchain",
          "s": "good",
          "d": "All of the data needed for proof construction is published on Ethereum L1."
        },
        {
          "n": "Exit Window",
          "v": "None",
          "s": "bad",
          "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
        },
        {
          "n": "Proposer Failure",
          "v": "Self propose",
          "s": "good",
          "d": "Anyone can be a Proposer and propose new roots to the L1 bridge."
        }
      ]
    },
    "optimism": {
      "name": "OP Mainnet",
      "slug": "op-mainnet",
      "stage": "Stage 1",
      "category": "Optimistic Rollup",
      "hostChain": "Ethereum",
      "providers": [
        "OP Stack"
      ],
      "tvs": 1707964288,
      "change7d": 0.061151687881793926,
      "risks": [
        {
          "n": "Sequencer Failure",
          "v": "Self sequence",
          "s": "good",
          "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
        },
        {
          "n": "State Validation",
          "v": "Fraud proofs (INT)",
          "s": "good",
          "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve."
        },
        {
          "n": "Data Availability",
          "v": "Onchain",
          "s": "good",
          "d": "All of the data needed for proof construction is published on Ethereum L1."
        },
        {
          "n": "Exit Window",
          "v": "None",
          "s": "bad",
          "d": "There is no exit window for users to exit in case of unwanted upgrades as they are initiated by the Security Council with instant upgrade power and without proper notice."
        },
        {
          "n": "Proposer Failure",
          "v": "Self propose",
          "s": "good",
          "d": "Anyone can be a Proposer and propose new roots to the L1 bridge."
        }
      ]
    },
    "zksync era": {
      "name": "ZKsync Era",
      "slug": "zksync-era",
      "stage": "Stage 0",
      "category": "ZK Rollup",
      "hostChain": "Ethereum",
      "providers": [
        "ZK Stack"
      ],
      "tvs": 242387776,
      "change7d": 0.11053992189175177,
      "risks": [
        {
          "n": "Sequencer Failure",
          "v": "Enqueue via L1",
          "s": "warning",
          "d": "Users can submit transactions to an L1 queue, but can't force them. The sequencers cannot selectively skip transactions but can stop processing the queue entirely. In other words, if the sequencers censor or are down, they are so for everyone."
        },
        {
          "n": "State Validation",
          "v": "Validity proofs (ST, SN)",
          "s": "good",
          "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
        },
        {
          "n": "Data Availability",
          "v": "Onchain (SD)",
          "s": "good",
          "d": "All of the data (SD = state diffs) needed for proof construction is published onchain."
        },
        {
          "n": "Exit Window",
          "v": "None",
          "s": "bad",
          "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
        },
        {
          "n": "Proposer Failure",
          "v": "Replace proposer",
          "s": "warning",
          "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen. There is a decentralized Governance system that can attempt changing Proposers with an upgrade."
        }
      ]
    },
    "starknet": {
      "name": "Starknet",
      "slug": "starknet",
      "stage": "Stage 1",
      "category": "ZK Rollup",
      "hostChain": "Ethereum",
      "providers": [
        "SN Stack"
      ],
      "tvs": 407561280,
      "change7d": 0.07284824108615329,
      "risks": [
        {
          "n": "Sequencer Failure",
          "v": "Log via L1",
          "s": "warning",
          "d": "Users can submit transactions to an L1 map, but can't force them. When users “complain” that their transaction is stuck on L1 and not picked up by the sequencer, the Security Council minority can bypass the sequencer by posting a state root that includes it."
        },
        {
          "n": "State Validation",
          "v": "Validity proofs (ST)",
          "s": "good",
          "d": "STARKs are zero knowledge proofs that ensure state correctness."
        },
        {
          "n": "Data Availability",
          "v": "Onchain (SD)",
          "s": "good",
          "d": "All of the data (SD = state diffs) needed for proof construction is published onchain."
        },
        {
          "n": "Exit Window",
          "v": "None",
          "s": "bad",
          "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
        },
        {
          "n": "Proposer Failure",
          "v": "Security Council minority",
          "s": "warning",
          "d": "Only the whitelisted proposer can update state roots on L1, so in the event of failure the withdrawals are frozen. The Security Council minority can be alerted to enforce censorship resistance because they are a permissioned Operator."
        }
      ]
    },
    "scroll": {
      "name": "Scroll",
      "slug": "scroll",
      "stage": "Stage 0",
      "category": "ZK Rollup",
      "hostChain": "Ethereum",
      "providers": [],
      "tvs": 46314332,
      "change7d": 0.021117765161089208,
      "risks": [
        {
          "n": "Sequencer Failure",
          "v": "Self sequence",
          "s": "good",
          "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 7d delay on this operation. Proposing new blocks requires creating ZK proofs."
        },
        {
          "n": "State Validation",
          "v": "Validity proofs (ST, SN)",
          "s": "good",
          "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
        },
        {
          "n": "Data Availability",
          "v": "Onchain",
          "s": "good",
          "d": "All of the data needed for proof construction is published on Ethereum L1."
        },
        {
          "n": "Exit Window",
          "v": "None",
          "s": "bad",
          "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
        },
        {
          "n": "Proposer Failure",
          "v": "Self propose",
          "s": "good",
          "d": "If the Proposer fails, users can leverage the source available prover to submit proofs to the L1 bridge."
        }
      ]
    },
    "linea": {
      "name": "Linea",
      "slug": "linea",
      "stage": "Stage 0",
      "category": "ZK Rollup",
      "hostChain": "Ethereum",
      "providers": [],
      "tvs": 358461664,
      "change7d": 0.07598943982771766,
      "risks": [
        {
          "n": "Sequencer Failure",
          "v": "No mechanism",
          "s": "bad",
          "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. Eventually (after 6 months of no finalized blocks) the Operator role becomes public, theoretically allowing anyone to post data."
        },
        {
          "n": "State Validation",
          "v": "Validity proofs (SN)",
          "s": "good",
          "d": "SNARKs are succinct zero knowledge proofs that ensure state correctness, but require trusted setup."
        },
        {
          "n": "Data Availability",
          "v": "Onchain",
          "s": "good",
          "d": "All of the data needed for proof construction is published on Ethereum L1. Unlike most ZK rollups, transaction data is posted instead of state diffs."
        },
        {
          "n": "Exit Window",
          "v": "None",
          "s": "bad",
          "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
        },
        {
          "n": "Proposer Failure",
          "v": "Cannot withdraw",
          "s": "bad",
          "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen. Eventually (after 6 months of no finalized blocks) the Operator role becomes public, theoretically allowing anyone to propose state with valid proofs."
        }
      ]
    },
    "polygon zkevm": {
      "name": "Polygon zkEVM",
      "slug": "polygonzkevm",
      "stage": "Not applicable",
      "category": "Other",
      "hostChain": "Ethereum",
      "providers": [
        "Agglayer CDK"
      ],
      "tvs": 9550906,
      "change7d": 0.02281956357912618,
      "risks": [
        {
          "n": "Sequencer Failure",
          "v": "No mechanism",
          "s": "bad",
          "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. Although the functionality exists in the code, it is currently disabled."
        },
        {
          "n": "State Validation",
          "v": "None",
          "s": "bad",
          "d": "Currently the system permits invalid state roots. 'Pessimistic' proofs only validate the bridge accounting."
        },
        {
          "n": "Data Availability",
          "v": "External",
          "s": "bad",
          "d": "Proof construction and state derivation rely fully on data that is NOT published onchain."
        },
        {
          "n": "Exit Window",
          "v": "None",
          "s": "bad",
          "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
        },
        {
          "n": "Proposer Failure",
          "v": "Cannot withdraw",
          "s": "bad",
          "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
        }
      ]
    },
    "blast": {
      "name": "Blast",
      "slug": "blast",
      "stage": "Stage 0",
      "category": "Other",
      "hostChain": "Ethereum",
      "providers": [
        "OP Stack"
      ],
      "tvs": 82279560,
      "change7d": 0.04073763344609649,
      "risks": [
        {
          "n": "Sequencer Failure",
          "v": "Self sequence",
          "s": "good",
          "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
        },
        {
          "n": "State Validation",
          "v": "None",
          "s": "bad",
          "d": "Currently the system permits invalid state roots. More details in project overview."
        },
        {
          "n": "Data Availability",
          "v": "Onchain",
          "s": "good",
          "d": "All of the data needed for proof construction is published on Ethereum L1."
        },
        {
          "n": "Exit Window",
          "v": "None",
          "s": "bad",
          "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
        },
        {
          "n": "Proposer Failure",
          "v": "Cannot withdraw",
          "s": "bad",
          "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
        }
      ]
    },
    "mantle": {
      "name": "Mantle",
      "slug": "mantle",
      "stage": "Stage 0",
      "category": "ZK Rollup",
      "hostChain": "Ethereum",
      "providers": [
        "OP Stack"
      ],
      "tvs": 1468072576,
      "change7d": 0.022946128288472645,
      "risks": [
        {
          "n": "Sequencer Failure",
          "v": "Self sequence",
          "s": "good",
          "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
        },
        {
          "n": "State Validation",
          "v": "Validity proofs (ST, SN)",
          "s": "good",
          "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
        },
        {
          "n": "Data Availability",
          "v": "Onchain",
          "s": "good",
          "d": "All of the data needed for proof construction is published on Ethereum L1."
        },
        {
          "n": "Exit Window",
          "v": "None",
          "s": "bad",
          "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
        },
        {
          "n": "Proposer Failure",
          "v": "Cannot withdraw",
          "s": "bad",
          "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
        }
      ]
    },
    "metis": {
      "name": "Metis Andromeda",
      "slug": "metis",
      "stage": "Stage 0",
      "category": "Other",
      "hostChain": "Ethereum",
      "providers": [
        "OVM"
      ],
      "tvs": 27428280,
      "change7d": 0.11798565725619414,
      "risks": [
        {
          "n": "Sequencer Failure",
          "v": "No mechanism",
          "s": "bad",
          "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. The single address acting as a sequencer on L1 is not trustlessly linkable to the claim of multiple decentralized sequencers being used."
        },
        {
          "n": "State Validation",
          "v": "Fraud proofs (INT)",
          "s": "bad",
          "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve.Anyone can submit challenge requests. However, permissioned actors are needed to create the challenge and to delete successfully disputed state roots. Additionally, the current permissioned actors (GameCreator and Security Council minority) can collude and finalize malicious state roots."
        },
        {
          "n": "Data Availability",
          "v": "Onchain",
          "s": "good",
          "d": "All of the data needed for proof construction is published on Ethereum L1."
        },
        {
          "n": "Exit Window",
          "v": "None",
          "s": "bad",
          "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
        },
        {
          "n": "Proposer Failure",
          "v": "Security Council minority",
          "s": "warning",
          "d": "Only the whitelisted proposer can update state roots on L1, so in the event of failure the withdrawals are frozen. The Security Council minority can be alerted to enforce censorship resistance because they own the proposer registry, controlling the active whitelisted proposer."
        }
      ]
    },
    "mode": {
      "name": "Mode Network",
      "slug": "mode",
      "stage": "Stage 0",
      "category": "Other",
      "hostChain": "Ethereum",
      "providers": [
        "OP Stack"
      ],
      "tvs": 8357239,
      "change7d": 0.03139697789686924,
      "risks": [
        {
          "n": "Sequencer Failure",
          "v": "Self sequence",
          "s": "good",
          "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
        },
        {
          "n": "State Validation",
          "v": "Fraud proofs (INT)",
          "s": "bad",
          "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. Only one entity is currently allowed to propose and submit challenges, as only permissioned games are currently allowed."
        },
        {
          "n": "Data Availability",
          "v": "Onchain",
          "s": "good",
          "d": "All of the data needed for proof construction is published on Ethereum L1."
        },
        {
          "n": "Exit Window",
          "v": "None",
          "s": "bad",
          "d": "There is no exit window for users to exit in case of unwanted upgrades as they are initiated by the Security Council with instant upgrade power and without proper notice."
        },
        {
          "n": "Proposer Failure",
          "v": "Cannot withdraw",
          "s": "bad",
          "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
        }
      ]
    },
    "gnosis chain": {
      "name": "Gnosis Chain",
      "slug": "gnosis",
      "stage": "Not applicable",
      "category": "Other",
      "hostChain": "Ethereum",
      "providers": [],
      "tvs": 293555808,
      "change7d": 0.02495020561864525,
      "risks": [
        {
          "n": "Sequencer Failure",
          "v": "Decentralized Sequencer Set",
          "s": "good",
          "d": "Users can permissionlessly become a sequencer (validator) by staking a minimum of 1 GNO to join the queue and wait to obtain block production rights. There is no specific censorship resistance mechanism against selective censorship by parts of the active validator set nor a way to force transactions from Ethereum L1."
        },
        {
          "n": "State Validation",
          "v": "None",
          "s": "bad",
          "d": "Ethereum contracts do not validate Gnosis Chain state transitions. Bridge messages are accepted after threshold signatures from dedicated bridge validators."
        },
        {
          "n": "Data Availability",
          "v": "PoS network",
          "s": "bad",
          "d": "Data is made available by an external proof of stake network of validators. Since there is no DA bridge, Ethereum cannot verify whether any data was made available on Gnosis Chain or whether incoming messages originate from state that was attested to by the PoS network."
        },
        {
          "n": "Exit Window",
          "v": "None",
          "s": "bad",
          "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
        },
        {
          "n": "Proposer Failure",
          "v": "Cannot withdraw",
          "s": "bad",
          "d": "The Gnosis Chain bridge is not validated by its PoS validator set. Withdrawals through the xDAI bridge require 4/7 validator signatures, while AMB and Omnibridge withdrawals require 4/7 validator signatures. The bridge validators can freeze bridge transactions and/or steal bridge-locked and minted assets. Transactions on Gnosis Chain itself cannot be forced from Ethereum. If the chain has a liveness failure due to blanket censorship or operator walkaway the only recourse are new validators joining the open validator set."
        }
      ]
    },
    "immutable zkevm": {
      "name": "Immutable zkEVM",
      "slug": "immutablezkevm",
      "stage": "Not applicable",
      "category": "Other",
      "hostChain": "Ethereum",
      "providers": [],
      "tvs": 23791612,
      "change7d": 0.02156204330167788,
      "risks": [
        {
          "n": "Sequencer Failure",
          "v": "No mechanism",
          "s": "bad",
          "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring."
        },
        {
          "n": "State Validation",
          "v": "None",
          "s": "bad",
          "d": "Currently the system permits invalid state roots. More details in project overview."
        },
        {
          "n": "Data Availability",
          "v": "External",
          "s": "bad",
          "d": "Proof construction and state derivation rely fully on data that is NOT published onchain."
        },
        {
          "n": "Exit Window",
          "v": "None",
          "s": "bad",
          "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
        },
        {
          "n": "Proposer Failure",
          "v": "Cannot withdraw",
          "s": "bad",
          "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
        }
      ]
    }
  }
};
/* KT_LIVE_END */

var D = window.KT_DATA = window.KT_DATA || {};

/* chỉ đè khi có số thật — hỏng nguồn thì giữ nguyên số chụp.
   Guard chỉ bao phần này: hồ sơ thành phố bên dưới không phụ
   thuộc vào strength.js nên vẫn phải gán dù chưa có STRENGTH. */
if (D.STRENGTH) {
  Object.keys(LIVE.chains).forEach(function (id) {
    var row = LIVE.chains[id], target = D.STRENGTH[id];
    if (!target) return;
    ["tvl", "stab", "proto"].forEach(function (k) {
      var v = row[k];
      if (typeof v === "number" && isFinite(v) && v > 0) target[k] = v;
    });
  });
}

/* app hiển thị "số chụp ngày ..." ở bảng xếp hạng — cho đúng ngày thật */
D.SNAP_DATE = LIVE.date;
D.LIVE = LIVE;

/* hồ sơ L2BEAT cho từng thành phố — l2beat.js đọc từ đây */
D.L2BEAT = LIVE.cities;
})();
