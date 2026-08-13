/* ═══════════════════════════════════════════════════════
   TỰ SINH bởi scripts/build-l2beat.mjs — ĐỪNG SỬA TAY.
   Nguồn: l2beat.com/api/scaling/summary
   Lấy lúc: 2026-08-13T06:55:25.719Z
   107 dự án · tổng tài sản $39.44b
   ═══════════════════════════════════════════════════════ */
window.DSV_DATA = {
 "generatedAt": "2026-08-13T06:55:25.719Z",
 "date": "13/08/2026",
 "nguon": "l2beat.com/api/scaling/summary",
 "tongTvs": 39438608294.11682,
 "projects": [
  {
   "id": "base",
   "slug": "base",
   "ten": "Base Chain",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 1",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 11625053184,
   "d7": -0.005610318690907556,
   "chiaTvs": {
    "native": 4638126163.078125,
    "canonical": 2196386660.1955004,
    "external": 4790543317.261719
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "arbitrum",
   "slug": "arbitrum",
   "ten": "Arbitrum One",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 1",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 10079069184,
   "d7": 0.0007925738222271939,
   "chiaTvs": {
    "native": 3125646631.423828,
    "canonical": 2945806810.381881,
    "external": 4007617958.5113983
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "hyperliquid",
   "slug": "hyperliquid",
   "ten": "Hyperliquid",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Arbitrum One",
   "stack": null,
   "tvs": 5855873536,
   "d7": -0.01240677026509518,
   "chiaTvs": {
    "native": 0,
    "canonical": 5855873536,
    "external": 0
   },
   "ruiRo": [
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
     "d": "Proof construction and state derivation rely fully on data that is ultimately NOT published on Ethereum."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "polygon-pos",
   "slug": "polygon-pos",
   "ten": "Polygon PoS",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": null,
   "tvs": 3683557888,
   "d7": -0.017296295155500685,
   "chiaTvs": {
    "native": 8494079.96875,
    "canonical": 2222549192.881812,
    "external": 1452514622
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Decentralized Sequencer Set",
     "s": "warning",
     "d": "Although there is a sequencer set of 105 (called validators), if the cap of 105 is reached, no new stakers can join. A minimum of 100,000 POL stake is required to obtain block production rights. There is no specific censorship resistance mechanism against selective censorship by parts of the active validator set nor a way to force transactions from Ethereum L1. The canonical bridge between Polygon PoS and Ethereum allows for queuing transactions from the Ethereum and Polygon PoS sides, which cannot be skipped, except for halting the queue entirely."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "PoS network",
     "s": "warning",
     "d": "Data is guaranteed to be available by an external proof of stake network of validators. On Ethereum, DA is attested via signed block headers."
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
     "s": "warning",
     "d": "The PoS network is composed of 105 validators. Blocks are included in the chain only if signed by 2/3+1 of the network stake. It's currently not possible to join the set if the validator cap is reached. The current validator cap is set to 105. In the event of a failure in reaching consensus, withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "optimism",
   "slug": "op-mainnet",
   "ten": "OP Mainnet",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 1",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 1389428352,
   "d7": -0.031810746714305616,
   "chiaTvs": {
    "native": 229229655.96875,
    "canonical": 913750402.5807171,
    "external": 246447662.87249756
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "mantle",
   "slug": "mantle",
   "ten": "Mantle",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 1238282880,
   "d7": -0.008906039196530435,
   "chiaTvs": {
    "native": 60259184,
    "canonical": 585154191.9922217,
    "external": 592869564.75
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "robinhood",
   "slug": "robinhood",
   "ten": "Robinhood Chain",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 1116588416,
   "d7": 0.12151792692385777,
   "chiaTvs": {
    "native": 546426376.8598633,
    "canonical": 305951662.9877533,
    "external": 264210304
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no guaranteed mechanism to have transactions included if the sequencer is down or censoring. Although users can enqueue messages in the L1 delayed inbox and call forceInclusion on the SequencerInbox, the chain runs ArbOS 61 transaction filtering: an authorized filterer can register any transaction hash in the ArbFilteredTransactionsManager precompile (0x00…0074), after which the state transition function forcibly fails that transaction, including force-included ones, without delay."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs only allow 2 WHITELISTED actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 6d 8h challenge period."
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
     "d": "Anyone can become a Proposer after 28d of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "lighter",
   "slug": "lighter",
   "ten": "Lighter",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": null,
   "tvs": 902382848,
   "d7": 0.051947497719990965,
   "chiaTvs": {
    "native": 0,
    "canonical": 902382807.9365234,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Force via L1",
     "s": "good",
     "d": "Users can force the sequencer to include a transaction by submitting a request through L1. If the sequencer censors or is down for  for more than 14d, users can use the exit hatch to withdraw their funds."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (SN)",
     "s": "good",
     "d": "SNARKs are succinct zero knowledge proofs that ensure state correctness, but require trusted setup."
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
     "v": "Use escape hatch",
     "s": "good",
     "d": "Users are able to trustlessly exit by submitting a zero knowledge proof of funds."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "starknet",
   "slug": "starknet",
   "ten": "Starknet",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 1",
   "me": "Ethereum",
   "stack": "SN Stack",
   "tvs": 352119744,
   "d7": -0.05302512382219171,
   "chiaTvs": {
    "native": 147148614.578125,
    "canonical": 138117583.07366538,
    "external": 66853515.83251953
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "linea",
   "slug": "linea",
   "ten": "Linea",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": null,
   "tvs": 341197792,
   "d7": -0.014866215425507145,
   "chiaTvs": {
    "native": 1049891.4340820312,
    "canonical": 161025259.59802318,
    "external": 179122609.11956787
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "worldchain",
   "slug": "world",
   "ten": "World Chain",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 334269952,
   "d7": 0.045322921802541716,
   "chiaTvs": {
    "native": 0,
    "canonical": 317897281.8850002,
    "external": 16372697
   },
   "ruiRo": [
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
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "celo",
   "slug": "celo",
   "ten": "Celo",
   "loai": "layer2",
   "dang": "Optimium",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 252428880,
   "d7": 0.05222935722177602,
   "chiaTvs": {
    "native": 233079142.7421875,
    "canonical": 2805557.014448017,
    "external": 16544182.5625
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (1R, ZK)",
     "s": "warning",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Single round proofs (1R) only require a single transaction to resolve. ZK proofs are used to prove the correctness of the state transition. The system currently operates with at least 5 whitelisted challengers external to the team."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "warning",
     "d": "Proof construction and state derivation fully rely on data that is posted on EigenDA. The sequencer is publishing data to EigenDA v2. Sequencer transaction data roots are checked against the DACert Verifier data roots, signed off by EigenDA operators."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "gnosis",
   "slug": "gnosis",
   "ten": "Gnosis Chain",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": null,
   "tvs": 237971472,
   "d7": -0.014559173887583876,
   "chiaTvs": {
    "native": 0,
    "canonical": 237971478.50320044,
    "external": 0
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "zksync2",
   "slug": "zksync-era",
   "ten": "ZKsync Era",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "ZK Stack",
   "tvs": 193647760,
   "d7": -0.04126365773220675,
   "chiaTvs": {
    "native": 74003516.57617188,
    "canonical": 107689374.43045576,
    "external": 11954897.81225586
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "roninnetwork",
   "slug": "ronin-network",
   "ten": "Ronin",
   "loai": "layer2",
   "dang": "Optimium",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 188868672,
   "d7": -0.016917691795829803,
   "chiaTvs": {
    "native": 57004687.40625,
    "canonical": 0,
    "external": 131863984.99167968
   },
   "ruiRo": [
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
     "v": "External",
     "s": "warning",
     "d": "Proof construction and state derivation fully rely on data that is posted on EigenDA. The sequencer is publishing data to EigenDA v2. Sequencer transaction data roots are checked against the DACert Verifier data roots, signed off by EigenDA operators."
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
     "d": "The primary whitelisted proposer has an optimistic advantage, letting them win by default if no conflicting proposals are made. This privilege is dropped after 1mo of inactivity, and anyone can leverage the source available zk prover to prove a fault or a conflicting valid proposal to win against the privileged proposer and/or supply a bond and make a counter proposal at any time."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "fraxtal",
   "slug": "fraxtal",
   "ten": "Fraxtal",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 154979152,
   "d7": 0.003138082680260945,
   "chiaTvs": {
    "native": 0,
    "canonical": 154450855.7181729,
    "external": 528312.21875
   },
   "ruiRo": [
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
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation rely fully on data that is NOT published on chain. Fraxtal uses a separate data availability module developed by the Frax Core Team, and data availability attestations are not published on chain."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "ink",
   "slug": "ink",
   "ten": "Ink",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 1",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 151004528,
   "d7": -0.075230249739627,
   "chiaTvs": {
    "native": 0,
    "canonical": 22170685.360000372,
    "external": 128833856
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "morph",
   "slug": "morph",
   "ten": "Morph",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": null,
   "tvs": 119014656,
   "d7": 0.08237515821648578,
   "chiaTvs": {
    "native": 0,
    "canonical": 12659037.134921193,
    "external": 106355602.22691345
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Force via L1",
     "s": "good",
     "d": "Users can force the sequencer to include a transaction by submitting a request through L1. If the sequencer censors or is down for 7d, new L1 batches must include at least 1 transaction from the queue."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (1R, ZK)",
     "s": "warning",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Single round proofs (1R) only require a single transaction to resolve. ZK proofs are used to prove the correctness of the state transition. The system currently operates with at least 5 whitelisted challengers external to the team."
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
     "d": "Anyone can become a Proposer after 7d of inactivity from the currently whitelisted Proposers. This requires using the source-available prover to submit a zk proof of validity for the proposal."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "xlayer",
   "slug": "xlayer",
   "ten": "X Layer",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 117926744,
   "d7": 0.0022997860885480836,
   "chiaTvs": {
    "native": 0,
    "canonical": 4462241.124334792,
    "external": 113464488
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (1R, ZK)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Single round proofs (1R) only require a single transaction to resolve. ZK proofs are used to prove the correctness of the state transition. Challenges are currently restricted to 1 whitelisted challenger and proposals are restricted to 1 whitelisted proposer."
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
     "d": "Only whitelisted proposers can publish state roots. Permissionless proposing becomes available only after 1000y of proposer inactivity, which is not a practical recovery path."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "mantapacific",
   "slug": "mantapacific",
   "ten": "Manta Pacific",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 86134120,
   "d7": -0.01580235249122064,
   "chiaTvs": {
    "native": 27256866,
    "canonical": 22342129.211647987,
    "external": 36535130.98981476
   },
   "ruiRo": [
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
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "lyra",
   "slug": "derive",
   "ten": "Derive",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 76020272,
   "d7": -0.020848106856130477,
   "chiaTvs": {
    "native": 0,
    "canonical": 86297.037815094,
    "external": 75933973.37933472
   },
   "ruiRo": [
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
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "unichain",
   "slug": "unichain",
   "ten": "Unichain",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 1",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 69922896,
   "d7": -0.034000769893814065,
   "chiaTvs": {
    "native": 0,
    "canonical": 28914833.79667498,
    "external": 41008063.39629841
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "blast",
   "slug": "blast",
   "ten": "Blast",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 67196824,
   "d7": -0.004383881256261435,
   "chiaTvs": {
    "native": 16549606.986328125,
    "canonical": 37002194.13161421,
    "external": 13645016.659179688
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "katana",
   "slug": "katana",
   "ten": "Katana",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Agglayer CDK",
   "tvs": 61564108,
   "d7": -0.10429078356348831,
   "chiaTvs": {
    "native": 995192.6610937119,
    "canonical": 59425731.99214791,
    "external": 1143185.1201171875
   },
   "ruiRo": [
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
     "d": "There is no window for users to exit in case of an unwanted upgrade since the Security Council can remove the delay on upgrades."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "bob",
   "slug": "bob",
   "ten": "BOB",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 61265180,
   "d7": -0.01269382101726546,
   "chiaTvs": {
    "native": 12649854,
    "canonical": 3192256.3967727274,
    "external": 45423070.48364258
   },
   "ruiRo": [
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
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "The primary whitelisted proposer has an optimistic advantage, letting them win by default if no conflicting proposals are made. This privilege is dropped after 1mo of inactivity, and anyone can leverage the source available zk prover to prove a fault or a conflicting valid proposal to win against the privileged proposer and/or supply a bond and make a counter proposal at any time."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "plumenetwork",
   "slug": "plumenetwork",
   "ten": "Plume Network",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 60334660,
   "d7": 0.06364510189507766,
   "chiaTvs": {
    "native": 24709.80078125,
    "canonical": 55572854.60002899,
    "external": 4737093.015625
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 1d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 5d 14h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "abstract",
   "slug": "abstract",
   "ten": "Abstract",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "ZK Stack",
   "tvs": 45477704,
   "d7": -0.00660731231597389,
   "chiaTvs": {
    "native": 1269852.7109375,
    "canonical": 20615173.6875,
    "external": 23592672.625
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "scroll",
   "slug": "scroll",
   "ten": "Scroll",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": null,
   "tvs": 41866704,
   "d7": -0.021185943768865956,
   "chiaTvs": {
    "native": 3877809.25,
    "canonical": 35345713.42330313,
    "external": 2643180.902648926
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "cronoszkevm",
   "slug": "cronoszkevm",
   "ten": "Cronos zkEVM",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "ZK Stack",
   "tvs": 33729568,
   "d7": -0.00005751299348966121,
   "chiaTvs": {
    "native": 0,
    "canonical": 19528860.249023438,
    "external": 14200709.25
   },
   "ruiRo": [
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
     "v": "Replace proposer",
     "s": "warning",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen. There is a decentralized Governance system that can attempt changing Proposers with an upgrade."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "edgex",
   "slug": "edgex",
   "ten": "EdgeX",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "SN Stack",
   "tvs": 32509120,
   "d7": -0.5301071980101792,
   "chiaTvs": {
    "native": 0,
    "canonical": 32509120,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Force via L1",
     "s": "good",
     "d": "Users can force the sequencer to include a trade or a withdrawal transaction by submitting a request through L1. If the sequencer censors or is down for 7d, users can use the exit hatch to withdraw their funds. Users are required to find a counterparty for the trade by out of system means."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST)",
     "s": "good",
     "d": "STARKs are zero knowledge proofs that ensure state correctness."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 2/6 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Use escape hatch",
     "s": "good",
     "d": "Users are able to trustlessly exit by submitting a Merkle proof of funds. Positions will be closed using the average price from the last batch state update."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "lisk",
   "slug": "lisk",
   "ten": "Lisk",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 31444388,
   "d7": 0.0419995806073028,
   "chiaTvs": {
    "native": 0,
    "canonical": 31074183.99255371,
    "external": 370202.97265625
   },
   "ruiRo": [
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
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "megaeth",
   "slug": "megaeth",
   "ten": "MegaETH",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 28195510,
   "d7": -0.011931045353489544,
   "chiaTvs": {
    "native": 0,
    "canonical": 8099469.960000286,
    "external": 20096041.095703125
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (1R, ZK)",
     "s": "bad",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Single round proofs (1R) prove the validity of a state proposal, only requiring a single transaction to resolve. A fault proof eliminates a state proposal by proving that any intermediate state transition in the proposal results in a different state root. For either, a ZK proof is used. Since the node source is not available, challengers cannot watch the chain independently. `vanguardAdvantage` applies to every proposal and is set to 36558901084y 8mo, so only the Vanguard can submit state proposals; faulty proposals can be flagged but not replaced, halting the chain until the Vanguard proposes a correct state root."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on EigenDA. The sequencer is publishing data to EigenDA v2. Sequencer transaction data roots are not checked against the DACert Verifier onchain."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "apex-omni",
   "slug": "apex-omni",
   "ten": "ApeX Omni",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum One",
   "stack": null,
   "tvs": 25826506,
   "d7": -0.001382246110489871,
   "chiaTvs": {
    "native": 0,
    "canonical": 5545201.689941406,
    "external": 20281307.545620203
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs",
     "s": "good",
     "d": "Zero knowledge cryptography is used to ensure state correctness. Proofs are first verified on Arbitrum One and finally on Ethereum."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on the base chain, which ultimately gets published on Ethereum."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "sxnetwork",
   "slug": "sxnetwork",
   "ten": "SX Network",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 23375812,
   "d7": 0.027766177796712865,
   "chiaTvs": {
    "native": 0,
    "canonical": 23375812.69000244,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 4d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs allow 6 WHITELISTED actors watching the chain to prove that the state is incorrect. There are fewer than 5 Challengers external to the Operator among these. Interactive proofs (INT) require multiple transactions over time to resolve. There is a 6d 8h challenge period."
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
     "d": "Anyone can become a Proposer after 12d 17h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "metis",
   "slug": "metis",
   "ten": "Metis Andromeda",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OVM",
   "tvs": 23200834,
   "d7": -0.010619424646409414,
   "chiaTvs": {
    "native": 0,
    "canonical": 23200833.00490594,
    "external": 0
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "galxegravity",
   "slug": "galxegravity",
   "ten": "Gravity",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 22812026,
   "d7": -0.02019869344512304,
   "chiaTvs": {
    "native": 0,
    "canonical": 21937306,
    "external": 874720.203125
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 2y 9mo delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 5d 14h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "immutablezkevm",
   "slug": "immutablezkevm",
   "ten": "Immutable zkEVM",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": null,
   "tvs": 20292764,
   "d7": -0.002327029331621655,
   "chiaTvs": {
    "native": 24276.419921875,
    "canonical": 20268488.12890625,
    "external": 0
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "rise",
   "slug": "rise",
   "ten": "RISE",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 19366780,
   "d7": 0.023336587559864785,
   "chiaTvs": {
    "native": 0,
    "canonical": 109436.37156295776,
    "external": 19257344
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (1R, ZK)",
     "s": "warning",
     "d": "Fraud proofs allow actors watching the chain to prove that the state is incorrect. Single round proofs (1R) only require a single transaction to resolve. ZK proofs are used to prove the correctness of the state transition. The system currently operates with a closed set of 1 whitelisted challenger."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "warning",
     "d": "Proof construction and state derivation fully rely on data that is posted on EigenDA. The sequencer is publishing data to EigenDA v2. Sequencer transaction data roots are checked against the DACert Verifier data roots, signed off by EigenDA operators."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "soneium",
   "slug": "soneium",
   "ten": "Soneium",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 19011472,
   "d7": -0.021451257119021405,
   "chiaTvs": {
    "native": 820992.7475585938,
    "canonical": 7682752.363603592,
    "external": 10507729.279228449
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "fuel",
   "slug": "fuel",
   "ten": "Fuel Ignition",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": null,
   "tvs": 17395424,
   "d7": 0.00846837706928083,
   "chiaTvs": {
    "native": 0,
    "canonical": 17395427.598342896,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1."
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
     "d": "Proof construction and state derivation fully rely on data that is posted on EigenDA. The sequencer is publishing data to EigenDA v2. Sequencer transaction data roots are not checked against the DACert Verifier onchain."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "paradex",
   "slug": "paradex",
   "ten": "Paradex",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "SN Stack",
   "tvs": 17295892,
   "d7": -0.022092391587047233,
   "chiaTvs": {
    "native": 0,
    "canonical": 17295892,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST)",
     "s": "good",
     "d": "STARKs are zero knowledge proofs that ensure state correctness."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Encrypted data is posted on Ethereum as blobs, and a privacy council of 3 members holds the decryption keys. Users are not able to independetly reconstruct the L2 state without relying on the council members."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "apechain",
   "slug": "apechain",
   "ten": "ApeChain",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum One",
   "stack": "Arbitrum",
   "tvs": 15635787,
   "d7": -0.09452692093379655,
   "chiaTvs": {
    "native": 0,
    "canonical": 0,
    "external": 15635787
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 4d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 5/7 that is tasked with protecting and supplying the data."
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
     "d": "Anyone can become a Proposer after 12d 17h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "aevo",
   "slug": "aevo",
   "ten": "Aevo",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 14745156,
   "d7": 0.0009227126816075959,
   "chiaTvs": {
    "native": 0,
    "canonical": 12319602.5546875,
    "external": 2425553.625
   },
   "ruiRo": [
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
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on EigenDA. The sequencer is publishing data to EigenDA v2. Sequencer transaction data roots are not checked against the DACert Verifier onchain."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "lumia",
   "slug": "lumia",
   "ten": "Lumia Prism",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "Agglayer CDK",
   "tvs": 12305734,
   "d7": 0.037887683382254345,
   "chiaTvs": {
    "native": 0,
    "canonical": 12305734.629993938,
    "external": 0
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "adi",
   "slug": "adi",
   "ten": "ADI Chain",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "ZK Stack",
   "tvs": 11947920,
   "d7": -0.034100178419415816,
   "chiaTvs": {
    "native": 0,
    "canonical": 4516852,
    "external": 7431067.5
   },
   "ruiRo": [
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
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "nova",
   "slug": "nova",
   "ten": "Arbitrum Nova",
   "loai": "layer2",
   "dang": "Optimium",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 11633534,
   "d7": -0.007714531047863571,
   "chiaTvs": {
    "native": 0,
    "canonical": 11633533.32103111,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 1d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "warning",
     "d": "Fraud proofs allow 10 WHITELISTED actors watching the chain to prove that the state is incorrect. At least 5 Challengers are external to the Operator. Interactive proofs (INT) require multiple transactions over time to resolve. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "warning",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 5/6 that is tasked with protecting and supplying the data."
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
     "d": "Anyone can become a Proposer after 28d of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "haust",
   "slug": "haust",
   "ten": "Haust Network",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "Agglayer CDK",
   "tvs": 11330472,
   "d7": -0.0010650160563513422,
   "chiaTvs": {
    "native": 0,
    "canonical": 11330472.53126049,
    "external": 0
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "zklinknova",
   "slug": "zklinknova",
   "ten": "zkLink Nova",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Linea",
   "stack": null,
   "tvs": 11114721,
   "d7": 0.004879233809850003,
   "chiaTvs": {
    "native": 0,
    "canonical": 10204960.369759649,
    "external": 909761.2526976839
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs",
     "s": "good",
     "d": "Zero knowledge cryptography is used to ensure state correctness. Proofs are first verified on Linea and finally on Ethereum."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation rely fully on data that is ultimately NOT published on Ethereum."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "ethereal",
   "slug": "ethereal",
   "ten": "Ethereal",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum One",
   "stack": "Arbitrum",
   "tvs": 11052904,
   "d7": -0.04112692898647374,
   "chiaTvs": {
    "native": 0,
    "canonical": 96.5,
    "external": 11052808
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 2d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 5d 14h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "taiko",
   "slug": "taiko",
   "ten": "Taiko Alethia",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Taiko",
   "tvs": 10608246,
   "d7": -0.03276108485437279,
   "chiaTvs": {
    "native": 0,
    "canonical": 10397653.03758359,
    "external": 210592.7550354004
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Enqueue via L1",
     "s": "warning",
     "d": "Users can submit transactions to an L1 queue, but can't force them. The sequencers cannot selectively skip transactions but can stop processing the queue entirely. In other words, if the sequencers censor or are down, they are so for everyone. An inclusion becomes due after 9m 36s. From then on, a whitelisted proposer cannot publish another proposal without processing up to ten due inclusions."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs",
     "s": "good",
     "d": "Every proposal range is verified by exactly two proofs chosen from SGX (Geth), SGX (Reth), SP1 and RISC0, with at least one SP1 or RISC0 proof required. Proof submission is gated by ProverWhitelist, which has 2 whitelisted provers. This can affect liveness but does not allow finalizing invalid state."
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
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen. Proposing is gated by PreconfWhitelist, which selects a single active operator for the current epoch and has no permissionless fallback."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "sophon",
   "slug": "sophon",
   "ten": "Sophon",
   "loai": "layer2",
   "dang": "Validium",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "ZK Stack",
   "tvs": 10374411,
   "d7": -0.14352701646651445,
   "chiaTvs": {
    "native": 0,
    "canonical": 10374411.402685642,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. The Operator actively uses a TransactionFilterer contract, which requires accounts that enqueue or force transactions from L1 to be whitelisted."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST, SN)",
     "s": "good",
     "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "External",
     "s": "warning",
     "d": "Proof construction and state derivation fully rely on data that is posted on Avail. Transaction data is checked against the Vector bridge data roots, signed off by Avail validators."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "zircuit",
   "slug": "zircuit",
   "ten": "Zircuit",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 9409838,
   "d7": -0.002393131512187119,
   "chiaTvs": {
    "native": 0,
    "canonical": 6274864.734807014,
    "external": 3134973.928007841
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. The L2 code has been modified to allow the sequencer to explicitly censor selected L1->L2 transactions."
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
     "v": "Use escape hatch",
     "s": "warning",
     "d": "Users are able to trustlessly exit by submitting a Merkle proof of funds after 1mo with no new state proposals have passed. The escape of ETH and ERC-20 balances is permissionless while the escape of DeFi contract balances is trusted."
    }
   ],
   "xemXet": true,
   "luuTru": false
  },
  {
   "id": "silicon",
   "slug": "silicon",
   "ten": "Silicon",
   "loai": "layer2",
   "dang": "Validium",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Agglayer CDK",
   "tvs": 8912652,
   "d7": -0.005420019724988401,
   "chiaTvs": {
    "native": 0,
    "canonical": 8912653.083269015,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. Although the functionality exists in the code, it is currently disabled."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST, SN)",
     "s": "good",
     "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 2/3 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since the Security Council can remove the delay on upgrades."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "polygonzkevm",
   "slug": "polygonzkevm",
   "ten": "Polygon zkEVM",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "Agglayer CDK",
   "tvs": 8064881,
   "d7": -0.005875896350462928,
   "chiaTvs": {
    "native": 0,
    "canonical": 6619282.298461314,
    "external": 1445598.9462890625
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "mode",
   "slug": "mode",
   "ten": "Mode Network",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 6801095,
   "d7": -0.06340118059930333,
   "chiaTvs": {
    "native": 308356.625,
    "canonical": 5003301.7758206725,
    "external": 1489436.2063598633
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "orderly",
   "slug": "orderly",
   "ten": "Orderly Network",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 6758768.5,
   "d7": -0.033365686681764206,
   "chiaTvs": {
    "native": 0,
    "canonical": 247302.125,
    "external": 6511466.703125
   },
   "ruiRo": [
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
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "hashkey",
   "slug": "hashkey",
   "ten": "HashKey Chain",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 6605629.5,
   "d7": 0.004343581096208471,
   "chiaTvs": {
    "native": 0,
    "canonical": 6605628.98046875,
    "external": 0
   },
   "ruiRo": [
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
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": true,
   "luuTru": false
  },
  {
   "id": "lighter-robinhood",
   "slug": "lighter-robinhood",
   "ten": "Lighter on Robinhood",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Robinhood Chain",
   "stack": null,
   "tvs": 6445662,
   "d7": 0.03021998571745499,
   "chiaTvs": {
    "native": 0,
    "canonical": 6445662.090087891,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no guaranteed mechanism to have transactions included if the sequencer is down or censoring. Although users can enqueue messages in the L1 delayed inbox and call forceInclusion on the SequencerInbox, the chain runs ArbOS 61 transaction filtering: an authorized filterer can register any transaction hash in the ArbFilteredTransactionsManager precompile (0x00…0074), after which the state transition function forcibly fails that transaction, including force-included ones, without delay."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs only allow 2 WHITELISTED actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on the base chain, which ultimately gets published on Ethereum."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Use escape hatch",
     "s": "good",
     "d": "Users are able to trustlessly exit by submitting a zero knowledge proof of funds."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "eclipse",
   "slug": "eclipse",
   "ten": "Eclipse",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": null,
   "tvs": 5612723.5,
   "d7": -0.012735599398219222,
   "chiaTvs": {
    "native": 0,
    "canonical": 5612723.5,
    "external": 0
   },
   "ruiRo": [
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
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "reya",
   "slug": "reya",
   "ten": "Reya",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 5541789,
   "d7": 0.0005390153306576995,
   "chiaTvs": {
    "native": 0,
    "canonical": 99220.8125,
    "external": 5442567.949999809
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 1d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
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
     "d": "Anyone can become a Proposer after 12d 17h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "bobanetwork",
   "slug": "bobanetwork",
   "ten": "Boba Network",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 5280262,
   "d7": -0.008587217699595251,
   "chiaTvs": {
    "native": 0,
    "canonical": 5209894.777907252,
    "external": 70367.09375
   },
   "ruiRo": [
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
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "zora",
   "slug": "zora",
   "ten": "Zora",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 4385698,
   "d7": -0.05123859098579986,
   "chiaTvs": {
    "native": 0,
    "canonical": 4385697.8671875,
    "external": 0
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "karak",
   "slug": "k2",
   "ten": "K2",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 4128370,
   "d7": -0.007894736684003978,
   "chiaTvs": {
    "native": 0,
    "canonical": 4128370.015625,
    "external": 0
   },
   "ruiRo": [
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
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "cyber",
   "slug": "cyber",
   "ten": "Cyber",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 2640292,
   "d7": -0.014929535610229805,
   "chiaTvs": {
    "native": 0,
    "canonical": 432000.4201660156,
    "external": 2208291.5
   },
   "ruiRo": [
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
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation rely fully on data that is NOT published onchain. A custom data availability (DA) provider without attestations is used, but data unavailability can be challenged."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "degen",
   "slug": "degen",
   "ten": "Degen Chain",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Base Chain",
   "stack": "Arbitrum",
   "tvs": 2112727,
   "d7": -0.03940833001519617,
   "chiaTvs": {
    "native": 0,
    "canonical": 2098057,
    "external": 14669.869873046875
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 4d 12h delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs only allow 2 WHITELISTED actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 5d 14h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 2/3 that is tasked with protecting and supplying the data."
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
     "d": "Anyone can become a Proposer after 6d 15h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "penchain",
   "slug": "penchain",
   "ten": "Pentagon Chain",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "Agglayer CDK",
   "tvs": 1985598.75,
   "d7": 0.008928291847529302,
   "chiaTvs": {
    "native": 0,
    "canonical": 1985598.7749938965,
    "external": 0
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "educhain",
   "slug": "edu-chain",
   "ten": "EDU Chain",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum One",
   "stack": "Arbitrum",
   "tvs": 1673799.25,
   "d7": 0.02532964450133579,
   "chiaTvs": {
    "native": 26645.869140625,
    "canonical": 1647153.3418952823,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 5d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs only allow 2 WHITELISTED actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
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
     "d": "Anyone can become a Proposer after 12d 17h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "fluent",
   "slug": "fluent",
   "ten": "Fluent",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": null,
   "tvs": 1645157.5,
   "d7": 0.17663203622964518,
   "chiaTvs": {
    "native": 0,
    "canonical": 1645157.652179718,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring."
    },
    {
     "n": "State Validation",
     "v": "TEE attestations",
     "s": "bad",
     "d": "State roots are accepted on the basis of an AWS Nitro Enclave preconfirmation and a 2d time delay; the SP1 ZK proof system exists in the contracts but is currently unreachable because CHALLENGER_ROLE has no holders. Effective security reduces to trust the TEE and wait the delay. See the State Validation section below for details."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "dbk",
   "slug": "dbk",
   "ten": "DeBank Chain",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 1316178.75,
   "d7": -0.10896417867479302,
   "chiaTvs": {
    "native": 0,
    "canonical": 1316178.75,
    "external": 0
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "superseed",
   "slug": "superseed",
   "ten": "Superseed",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 1098933.125,
   "d7": -0.009583248230643271,
   "chiaTvs": {
    "native": 896422.875,
    "canonical": 161660.8125,
    "external": 40849.41162109375
   },
   "ruiRo": [
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
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "nillion",
   "slug": "nillion",
   "ten": "Nillion",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 872203.9375,
   "d7": 0.18985478417907498,
   "chiaTvs": {
    "native": 0,
    "canonical": 872203.9250488281,
    "external": 0
   },
   "ruiRo": [
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
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "shape",
   "slug": "shape",
   "ten": "Shape",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 864646.875,
   "d7": -0.026000633358148506,
   "chiaTvs": {
    "native": 0,
    "canonical": 864646.875,
    "external": 0
   },
   "ruiRo": [
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
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "lens",
   "slug": "lens",
   "ten": "Lens",
   "loai": "layer2",
   "dang": "Validium",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "ZK Stack",
   "tvs": 792549.6875,
   "d7": -0.0326245972732252,
   "chiaTvs": {
    "native": 0,
    "canonical": 792549.71875,
    "external": 0
   },
   "ruiRo": [
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
     "v": "External",
     "s": "warning",
     "d": "Proof construction and state derivation fully rely on data that is posted on Avail. Transaction data is checked against the Vector bridge data roots, signed off by Avail validators."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "lasernet",
   "slug": "lasernet",
   "ten": "Lasernet",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 783023.625,
   "d7": 0.10992054580078103,
   "chiaTvs": {
    "native": 0,
    "canonical": 783023.625,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 1d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 5d 14h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "lightlink",
   "slug": "lightlink",
   "ten": "LightLink",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": null,
   "tvs": 703520.125,
   "d7": -0.0001494048145657123,
   "chiaTvs": {
    "native": 0,
    "canonical": 703520.1614624709,
    "external": 0
   },
   "ruiRo": [
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
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "hemi",
   "slug": "hemi",
   "ten": "Hemi",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 624011.125,
   "d7": 0.013092341253827522,
   "chiaTvs": {
    "native": 0,
    "canonical": 624011.1919080615,
    "external": 0
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "shibarium",
   "slug": "shibarium",
   "ten": "Shibarium",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": null,
   "tvs": 546674.625,
   "d7": -0.03561558712128943,
   "chiaTvs": {
    "native": 0,
    "canonical": 546674.732408531,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Enqueue via L1",
     "s": "warning",
     "d": "Users can submit transactions to an L1 queue, but can't force them. The sequencers cannot selectively skip transactions but can stop processing the queue entirely. In other words, if the sequencers censor or are down, they are so for everyone."
    },
    {
     "n": "State Validation",
     "v": "None",
     "s": "bad",
     "d": "Currently the system permits invalid state roots. More details in project overview."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 8/11 that is tasked with protecting and supplying the data."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "facet",
   "slug": "facet",
   "ten": "Facet",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 2",
   "me": "Ethereum",
   "stack": null,
   "tvs": 504369.875,
   "d7": -0.010058375254986207,
   "chiaTvs": {
    "native": 0,
    "canonical": 0,
    "external": 504369.8881249428
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "Users can self sequence transactions by sending them on L1. There is no privileged operator."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (1R, ZK)",
     "s": "good",
     "d": "Actors watching the chain can challenge state proposals, and challenged proposals must provide ZK proofs. SNARKs are zero knowledge proofs that ensure state correctness, but require trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "∞",
     "s": "good",
     "d": "Users can exit funds at any time because contracts are not upgradeable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can propose blocks if accompanied by a validity proof. Only the whitelisted proposers can propose state roots for recent blocks optimistically. Anyone can propose optimistically for L2 blocks that are older than 14d."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "xai",
   "slug": "xai",
   "ten": "Xai",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum One",
   "stack": "Arbitrum",
   "tvs": 499015.34375,
   "d7": 0.020142075714471908,
   "chiaTvs": {
    "native": 0,
    "canonical": 499015.3414059207,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 2d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs only allow 2 WHITELISTED actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 3/5 that is tasked with protecting and supplying the data."
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
     "d": "Anyone can become a Proposer after 12d 17h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "zeronetwork",
   "slug": "zeronetwork",
   "ten": "ZERO Network",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "ZK Stack",
   "tvs": 462298.34375,
   "d7": -0.08346912787378769,
   "chiaTvs": {
    "native": 0,
    "canonical": 462298.33837890625,
    "external": 0
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "soon",
   "slug": "soon",
   "ten": "Soon Alpha Mainnet",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 383246.21875,
   "d7": -0.032964761847087076,
   "chiaTvs": {
    "native": 0,
    "canonical": 383246.23694968224,
    "external": 0
   },
   "ruiRo": [
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
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on EigenDA. Sequencer transaction data roots are not checked against the ServiceManager DA bridge data roots onchain."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "superposition",
   "slug": "superposition",
   "ten": "Superposition",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum One",
   "stack": "Arbitrum",
   "tvs": 333142.3125,
   "d7": -0.08098006916601808,
   "chiaTvs": {
    "native": 0,
    "canonical": 243678.01726341248,
    "external": 89464.28125
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 2d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 5d 14h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "metal",
   "slug": "metal",
   "ten": "Metal",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 309577,
   "d7": -0.26369439382239845,
   "chiaTvs": {
    "native": 0,
    "canonical": 309577.0162206888,
    "external": 0
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "b3",
   "slug": "b3",
   "ten": "B3",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Base Chain",
   "stack": "OP Stack",
   "tvs": 277258.28125,
   "d7": -0.007619136674569704,
   "chiaTvs": {
    "native": 0,
    "canonical": 277258.2734375,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 1d delay on this operation."
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
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "alienx",
   "slug": "alienx",
   "ten": "AlienX",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 246769.71875,
   "d7": -0.007396417535450173,
   "chiaTvs": {
    "native": 0,
    "canonical": 246769.71435546875,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 1d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
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
     "d": "Anyone can become a Proposer after 12d 17h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "river",
   "slug": "towns",
   "ten": "Towns",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 227547.59375,
   "d7": -0.00799818098380145,
   "chiaTvs": {
    "native": 0,
    "canonical": 227547.59375,
    "external": 0
   },
   "ruiRo": [
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
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "pepeunchained2",
   "slug": "pepe-unchained",
   "ten": "Pepe Unchained",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 202479.453125,
   "d7": -0.1392734451731621,
   "chiaTvs": {
    "native": 0,
    "canonical": 202479.453125,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 1d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 5d 14h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "ancient",
   "slug": "ancient8",
   "ten": "Ancient8",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 197121.78125,
   "d7": -0.006262162971570451,
   "chiaTvs": {
    "native": 0,
    "canonical": 197121.77734375,
    "external": 0
   },
   "ruiRo": [
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
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "phala",
   "slug": "phala",
   "ten": "Phala",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 162615.546875,
   "d7": 0.05437841194775017,
   "chiaTvs": {
    "native": 0,
    "canonical": 162615.54638671875,
    "external": 0
   },
   "ruiRo": [
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
     "d": "There is no window for users to exit in case of an unwanted upgrade since contracts are instantly upgradable."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "funki",
   "slug": "funki",
   "ten": "Funki",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 123189.9609375,
   "d7": -0.021766015795483207,
   "chiaTvs": {
    "native": 0,
    "canonical": 123189.95234298706,
    "external": 0
   },
   "ruiRo": [
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
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation rely fully on data that is NOT published onchain. A custom data availability (DA) provider without attestations is used, but data unavailability can be challenged."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "intmax",
   "slug": "intmax",
   "ten": "INTMAX",
   "loai": "layer3",
   "dang": "ZK Rollup",
   "thang": "Stage 0",
   "me": "Scroll",
   "stack": null,
   "tvs": 105924.984375,
   "d7": -0.013976354890022469,
   "chiaTvs": {
    "native": 0,
    "canonical": 105924.99126249552,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 7d delay on this operation. Proposing new blocks requires creating ZK proofs."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (SN)",
     "s": "good",
     "d": "SNARKs are succinct zero knowledge proofs that ensure state correctness, but require trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "Self custodied",
     "s": "good",
     "d": "All data required for payments and withdrawals is self custodied by users."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "swan",
   "slug": "swan",
   "ten": "Swan Chain",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 79736.8671875,
   "d7": -0.00837000497548357,
   "chiaTvs": {
    "native": 0,
    "canonical": 79736.8671875,
    "external": 0
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "zkfair",
   "slug": "zkfair",
   "ten": "ZKFair",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "Agglayer CDK",
   "tvs": 61661.28515625,
   "d7": -0.0009235512596582618,
   "chiaTvs": {
    "native": 48955.8984375,
    "canonical": 12705.389864444733,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. Although the functionality exists in the code, it is currently disabled."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (SN)",
     "s": "good",
     "d": "SNARKs are succinct zero knowledge proofs that ensure state correctness, but require trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 3/5 that is tasked with protecting and supplying the data."
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
     "d": "If the Proposer fails, users can leverage the source available prover to submit proofs to the L1 bridge. There is a 5d delay for proving and a 5d delay for finalizing state proven in this way. These delays can only be lowered except during the emergency state."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "edgechain",
   "slug": "edgechain",
   "ten": "Edge Chain",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum One",
   "stack": "Arbitrum",
   "tvs": 59263.26953125,
   "d7": -0.0013850967981443585,
   "chiaTvs": {
    "native": 0,
    "canonical": 59263.2705078125,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 5d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs only allow 3 WHITELISTED actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 7d challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 2/5 that is tasked with protecting and supplying the data."
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
     "d": "Anyone can become a Proposer after 13d 8h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "appchain",
   "slug": "appchain",
   "ten": "Appchain",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "Arbitrum",
   "tvs": 39110.6484375,
   "d7": -0.007998077092843392,
   "chiaTvs": {
    "native": 0,
    "canonical": 39110.6484375,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 3d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
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
     "d": "Anyone can become a Proposer after 12d 17h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "r0ar",
   "slug": "r0ar",
   "ten": "R0ar",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 35261.328125,
   "d7": -0.004363115121693628,
   "chiaTvs": {
    "native": 0,
    "canonical": 35261.3291015625,
    "external": 0
   },
   "ruiRo": [
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "wirex",
   "slug": "wirex",
   "ten": "Wirex Pay Chain",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "Agglayer CDK",
   "tvs": 24359.509765625,
   "d7": -0.0006461469601325431,
   "chiaTvs": {
    "native": 0,
    "canonical": 24359.510009765625,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. Although the functionality exists in the code, it is currently disabled."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST, SN)",
     "s": "good",
     "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/2 that is tasked with protecting and supplying the data."
    },
    {
     "n": "Exit Window",
     "v": "None",
     "s": "bad",
     "d": "There is no window for users to exit in case of an unwanted upgrade since the Security Council can remove the delay on upgrades."
    },
    {
     "n": "Proposer Failure",
     "v": "Cannot withdraw",
     "s": "bad",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "deri",
   "slug": "deri",
   "ten": "Deri",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum One",
   "stack": "Arbitrum",
   "tvs": 10911.599609375,
   "d7": -0.007997649055893508,
   "chiaTvs": {
    "native": 0,
    "canonical": 10911.599609375,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 2d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 1d challenge period."
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
     "d": "Anyone can become a Proposer after 7d 8h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "cartesi-prt-honeypot-v2",
   "slug": "cartesi-prt-honeypot-v2",
   "ten": "Cartesi PRT Honeypot v2",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 2",
   "me": "Ethereum",
   "stack": "Cartesi Rollups",
   "tvs": 1242.0899658203125,
   "d7": 0.12108059236838509,
   "chiaTvs": {
    "native": 0,
    "canonical": 1242.0899658203125,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "Users can self sequence transactions by sending them on L1. There is no privileged operator."
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
     "v": "Not applicable",
     "s": "neutral",
     "d": "Users cannot exit their funds as all deposits are considered donations."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can be a Proposer and propose new roots to the L1 bridge."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "forknet",
   "slug": "forknet",
   "ten": "Forknet",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Not applicable",
   "me": "Ethereum",
   "stack": "Agglayer CDK",
   "tvs": 1076.3699951171875,
   "d7": -0.005313755819693511,
   "chiaTvs": {
    "native": 0,
    "canonical": 1076.370001077652,
    "external": 0
   },
   "ruiRo": [
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
     "d": "Currently the system permits invalid state roots. 'Pessimistic' proofs only validate the bridge accounting."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "settlus",
   "slug": "settlus",
   "ten": "Settlus",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "OP Stack",
   "tvs": 755.469970703125,
   "d7": -0.007996778815841377,
   "chiaTvs": {
    "native": 0,
    "canonical": 755.469970703125,
    "external": 0
   },
   "ruiRo": [
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
     "v": "External",
     "s": "bad",
     "d": "Proof construction and state derivation fully rely on data that is posted on Celestia. Sequencer tx roots are not checked against the Blobstream bridge data roots onchain, but L2 nodes can verify data availability by running a Celestia light client."
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
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "aztecnetwork",
   "slug": "aztecnetwork",
   "ten": "Aztec Network",
   "loai": "layer2",
   "dang": "ZK Rollup",
   "thang": "Stage 2",
   "me": "Ethereum",
   "stack": null,
   "tvs": 585.3900146484375,
   "d7": -0.020234930400224282,
   "chiaTvs": {
    "native": 0,
    "canonical": 585.3900146484375,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Decentralized Sequencer Set",
     "s": "good",
     "d": "Users can permissionlessly become a sequencer by staking 200 K AZTEC to join the queue and wait to obtain committee-based block production rights. If the pseudo-randomly sampled committees censor proposals, anyone who bonds 332 M AZTEC will join the escape hatch candidate set. Every 2d 23h, a candidate is pseudo-randomly selected to propose and prove checkpoints fully autonomously. A candidate remains in the set until they are selected or leave voluntarily."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (SN)",
     "s": "good",
     "d": "SNARKs are succinct zero knowledge proofs that ensure state correctness, but require trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "Onchain (SD)",
     "s": "good",
     "d": "State diffs needed to reconstruct the L2 state are published in Ethereum blobs. Public transaction bodies and client CHONK proofs propagate offchain, so withholding them can prevent permissionless proving; the affected pending checkpoints expire and are pruned rather than finalized."
    },
    {
     "n": "Exit Window",
     "v": "∞",
     "s": "good",
     "d": "Users can exit funds at any time because contracts are not upgradeable. Governance can register a new canonical rollup and bonus-instance validators automatically follow the latest version, but this does not mutate the current instance, its verifier, messaging contracts, or already-installed EscapeHatch. Governance can change bounded validator-entry parameters and can set the GSE proof-of-possession gas limit too low for new deposits; validators explicitly bound to this instance remain on it."
    },
    {
     "n": "Proposer Failure",
     "v": "Self Propose",
     "s": "good",
     "d": "Checkpoint proposals come from the open sequencer set, with the escape hatch providing a bonded fallback if the sampled committees are censoring or unavailable. Anyone with access to the required hardware can submit epoch root proofs which finalize the proven checkpoints."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "ethscriptions",
   "slug": "ethscriptions",
   "ten": "Ethscriptions",
   "loai": "layer2",
   "dang": "Optimistic Rollup",
   "thang": "Stage 2",
   "me": "Ethereum",
   "stack": null,
   "tvs": 0,
   "d7": 0,
   "chiaTvs": {
    "native": 0,
    "canonical": 0,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "Users can self sequence transactions by sending them on L1. There is no privileged operator."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (1R, ZK)",
     "s": "good",
     "d": "Actors watching the chain can challenge state proposals, and challenged proposals must provide ZK proofs. SNARKs are zero knowledge proofs that ensure state correctness, but require trusted setup."
    },
    {
     "n": "Data Availability",
     "v": "Onchain",
     "s": "good",
     "d": "All of the data needed for proof construction is published on Ethereum L1."
    },
    {
     "n": "Exit Window",
     "v": "∞",
     "s": "good",
     "d": "Users can exit funds at any time because contracts are not upgradeable."
    },
    {
     "n": "Proposer Failure",
     "v": "Self propose",
     "s": "good",
     "d": "Anyone can propose blocks if accompanied by a validity proof. Only the whitelisted proposers can propose state roots for recent blocks optimistically. Anyone can propose optimistically for L2 blocks that are older than 14d."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "grvt",
   "slug": "grvt",
   "ten": "GRVT",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "ZK Stack",
   "tvs": 0,
   "d7": 0,
   "chiaTvs": {
    "native": 0,
    "canonical": 0,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "No mechanism",
     "s": "bad",
     "d": "There is no mechanism to have transactions be included if the sequencer is down or censoring. The Operator actively uses a TransactionFilterer contract, which requires accounts that enqueue or force transactions from L1 to be whitelisted."
    },
    {
     "n": "State Validation",
     "v": "Validity proofs (ST, SN)",
     "s": "good",
     "d": "STARKs and SNARKs are zero knowledge proofs that ensure state correctness. STARKs proofs are wrapped in SNARKs proofs for efficiency. SNARKs require a trusted setup."
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
     "v": "Replace proposer",
     "s": "warning",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen. There is a decentralized Governance system that can attempt changing Proposers with an upgrade."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "zkcandy",
   "slug": "zkcandy",
   "ten": "zkCandy",
   "loai": "layer2",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Ethereum",
   "stack": "ZK Stack",
   "tvs": 0,
   "d7": 0,
   "chiaTvs": {
    "native": 0,
    "canonical": 0,
    "external": 0
   },
   "ruiRo": [
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
     "v": "Replace proposer",
     "s": "warning",
     "d": "Only the whitelisted proposers can publish state roots on L1, so in the event of failure the withdrawals are frozen. There is a decentralized Governance system that can attempt changing Proposers with an upgrade."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "earnm",
   "slug": "earnm",
   "ten": "Earnm",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum One",
   "stack": "Arbitrum",
   "tvs": 0,
   "d7": 0,
   "chiaTvs": {
    "native": 0,
    "canonical": 0,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 5d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "No actor outside of the single Proposer can submit fraud proofs. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 6d 8h challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 2/3 that is tasked with protecting and supplying the data."
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
     "d": "Anyone can become a Proposer after 12d 17h of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  },
  {
   "id": "playblock",
   "slug": "playblock",
   "ten": "PlayBlock",
   "loai": "layer3",
   "dang": "Other",
   "thang": "Stage 0",
   "me": "Arbitrum Nova",
   "stack": "Arbitrum",
   "tvs": 0,
   "d7": 0,
   "chiaTvs": {
    "native": 0,
    "canonical": 0,
    "external": 0
   },
   "ruiRo": [
    {
     "n": "Sequencer Failure",
     "v": "Self sequence",
     "s": "good",
     "d": "In the event of a sequencer failure, users can force transactions to be included in the project's chain by sending them to L1. There can be up to a 11d delay on this operation."
    },
    {
     "n": "State Validation",
     "v": "Fraud proofs (INT)",
     "s": "bad",
     "d": "Fraud proofs only allow 2 WHITELISTED actors watching the chain to prove that the state is incorrect. Interactive proofs (INT) require multiple transactions over time to resolve. The challenge protocol can be subject to delay attacks. There is a 30m challenge period."
    },
    {
     "n": "Data Availability",
     "v": "External (DAC)",
     "s": "bad",
     "d": "Proof construction relies fully on data that is NOT published onchain. There exists a Data Availability Committee (DAC) with a threshold of 1/1 that is tasked with protecting and supplying the data."
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
     "d": "Anyone can become a Proposer after 1mo 4d of inactivity from the currently whitelisted Proposers."
    }
   ],
   "xemXet": false,
   "luuTru": false
  }
 ]
};
