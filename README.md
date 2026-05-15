<div align="center">

# llm-exp-chatcache

### llama.cpp の cache_prompt と speculative decoding を多ターン会話で実測

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)](scripts/)
[![llama.cpp](https://img.shields.io/badge/llama.cpp-Vulkan-000000?style=flat)](https://github.com/ggerganov/llama.cpp)
[![Qwen](https://img.shields.io/badge/Qwen-2.5%20%2F%203-615CED?style=flat)](https://huggingface.co/Qwen)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

**54 ラン × 20 ターン = 1080 ターンで KV キャッシュ再利用と speculative decoding を計測、Qwen2.5-72B で最大 4.38x 高速化**

---

</div>

## 概要

llama.cpp の **`cache_prompt` (KV 再利用)** と **speculative decoding** が
多ターン会話にどれだけ効くかを、モデルサイズとペルソナを変えて定量測定した実験リポジトリ。
temp=0 / seed=42 の決定論セッティングで返答テキストを固定したまま、3 条件の速度差のみを抽出する。

## 実験マトリクス

- **モデル 6**: Qwen2.5-{3B, 7B, 14B, 32B, 72B} / Qwen3-30B-A3B (全て Q4_K_M)
- **ペルソナ 3**:
  - **P0** 汎用アシスタント (fizzbuzz→Go→Rust→観光→歴史→数学→API 比較、累積参照と話題切替が混在)
  - **P1** RPG NPC 薬草商人リナ (`/no_think`, 日常会話)
  - **P2** 引退漁師 富田源次郎 (秘密を小出しに明かす長めの独白)
- **条件 3**:
  - **C0** baseline: `--no-cache-prompt`
  - **C1** cache_prompt 有効
  - **C2** cache_prompt + speculative decoding (`-md Qwen2.5-0.5B -ngld 999 --draft-max 8`)
- **各ラン 20 ターン** (累積文脈、参照あり)

合計 6×3×3 = **54 ラン × 20 ターン = 1080 ターン**。

## 実行環境

- Windows 11, AMD Radeon 780M iGPU, 48GB DDR4 (UMA)
- llama.cpp build `b8672` / Vulkan backend + Flash Attention
- `-ngl 999 -c 8192`  (M72B のみ VRAM 制約のため `-ngl 18 -c 6144`)
- `temperature=0, seed=42, max_tokens=1024, stream=false`

## 結果サマリ

全詳細は [`results/summary/summary.md`](results/summary/summary.md)。代表的な結果:

### 20 ターン総所要時間 (lower is better)

| model | persona | C0 baseline | C1 cache | C2 cache+spec | **C2/C0** |
|---|---|---:|---:|---:|---:|
| Qwen2.5-3B  | P0 | 122.5s | 83.3s | 86.3s | **1.42x** |
| Qwen2.5-7B  | P0 | 668.9s | 345.0s | 270.8s | **2.47x** |
| Qwen2.5-14B | P0 | 1104.5s | 1024.4s | 360.9s | **3.06x** |
| Qwen2.5-32B | P0 | 2228.4s | 1041.7s | 846.0s | **2.63x** |
| Qwen2.5-72B | P0 | 8591.1s (143 min) | 3339.1s (56 min) | **1960.7s (33 min)** | **4.38x** |
| Qwen2.5-72B | P2 | 10840.7s (180 min) | 4130.9s (69 min) | **2515.3s (42 min)** | **4.31x** |

**要点**: モデルが大きいほど cache+spec の相対効果が増える。72B では **4.3-4.5x** の高速化。

### prefill スループット倍率 (C2/C0)

`cache_prompt` の本質は prefill (プロンプト処理) の再計算回避:

| model | P0 | P1 | P2 |
|---|---:|---:|---:|
| Qwen2.5-3B  | 13.3x | 10.7x | 9.0x |
| Qwen2.5-7B  | 40.8x | 16.0x | 15.8x |
| Qwen2.5-14B | **63.8x** | 8.3x | 27.8x |
| Qwen2.5-32B | 36.9x | 22.5x | 30.2x |
| Qwen2.5-72B | 49.1x | 19.0x | 26.9x |

### speculative decoding 受理率 (C2)

P0 (汎用アシスタント) は短く一意な出力が多いので受理率が高く、
P1/P2 (キャラ性強い自然言語) は分岐が多く受理率が低い:

| model | P0 | P1 | P2 |
|---|---:|---:|---:|
| Qwen2.5-3B  | 76% | 67% | 64% |
| Qwen2.5-7B  | 77% | 52% | 58% |
| Qwen2.5-14B | 68% | 51% | 53% |
| Qwen2.5-32B | 74% | 49% | 54% |
| Qwen2.5-72B | 74% | 49% | 57% |
| Qwen3-30B-A3B | 67% | 45% | 58% |

### チャート

- [e6_total_p0.png](results/summary/e6_total_p0.png) — P0 ペルソナの総所要時間
- [e6_total_p1.png](results/summary/e6_total_p1.png) — P1 ペルソナの総所要時間
- [e6_total_p2.png](results/summary/e6_total_p2.png) — P2 ペルソナの総所要時間
- [e6_speedup_heatmap.png](results/summary/e6_speedup_heatmap.png) — total elapsed 速度比ヒートマップ
- [e6_prefill_heatmap.png](results/summary/e6_prefill_heatmap.png) — prefill スループット倍率ヒートマップ
- `results/summary/e6_turns_<model>_<persona>.png` — ターン単位の所要時間推移

## LLM の返答を読む

18 個 `(model × persona)` の全ターンを `results/summary/transcripts/` に markdown で整形済み。
各ファイル先頭に **C0/C1/C2 3 条件の 20 ターン合計 timing 比較**、
各ターンに **3 条件並列の elapsed / prefill / gen / spec 受理率テーブル** +
User 質問 + Assistant 返答 (引用) を載せている。
temp=0 seed=42 の決定論セッティングなので返答テキストは 3 条件で同一、
違うのは速度だけ ← それこそが実験の本題。

例: [`Qwen2.5-72B × P0`](results/summary/transcripts/M72B_P0.md) は
20 ターン合計 8591s → 3339s → 1961s (**4.38x**) が 1 ファイルで一望できる。

| model | P0 | P1 | P2 |
|---|---|---|---|
| Qwen2.5-3B  | [M3B_P0](results/summary/transcripts/M3B_P0.md) | [M3B_P1](results/summary/transcripts/M3B_P1.md) | [M3B_P2](results/summary/transcripts/M3B_P2.md) |
| Qwen2.5-7B  | [M7B_P0](results/summary/transcripts/M7B_P0.md) | [M7B_P1](results/summary/transcripts/M7B_P1.md) | [M7B_P2](results/summary/transcripts/M7B_P2.md) |
| Qwen2.5-14B | [M14B_P0](results/summary/transcripts/M14B_P0.md) | [M14B_P1](results/summary/transcripts/M14B_P1.md) | [M14B_P2](results/summary/transcripts/M14B_P2.md) |
| Qwen3-30B-A3B | [M30A3_P0](results/summary/transcripts/M30A3_P0.md) | [M30A3_P1](results/summary/transcripts/M30A3_P1.md) | [M30A3_P2](results/summary/transcripts/M30A3_P2.md) |
| Qwen2.5-32B | [M32B_P0](results/summary/transcripts/M32B_P0.md) | [M32B_P1](results/summary/transcripts/M32B_P1.md) | [M32B_P2](results/summary/transcripts/M32B_P2.md) |
| Qwen2.5-72B | [M72B_P0](results/summary/transcripts/M72B_P0.md) | [M72B_P1](results/summary/transcripts/M72B_P1.md) | [M72B_P2](results/summary/transcripts/M72B_P2.md) |

## レポジトリ構成

```
scripts/
  bench_conv.py          # ベンチ本体 (モデル起動 / 20 ターン回し / CSV 追記)
  analyze.py             # CSV/JSONL → summary.md + PNG 群
  dump_transcripts.py    # conv_trials.jsonl → 3 条件比較つき markdown
results/
  raw/
    conv.csv             # ラン単位集計 (94 行: 失敗再走の履歴込み、stable=true のみが確定値)
    conv_trials.jsonl    # ターン単位 (1249 行 → dedup 後 1080, 全文 + timings)
    prompts/             # ペルソナ system prompt と質問セット (P0/P1/P2)
    configs/configs/     # 各ランの起動コマンドと設定 JSON (54 本)
    logs/logs/           # llama-server の stdout+stderr (54 本)
    responses/responses/<case>/    # /v1/chat/completions の生レスポンス 20 個 × 54 ケース = 1080
  summary/
    summary.md           # 集計結果
    e6_*.png             # チャート 23 枚
    transcripts/         # 18 個の (model × persona) markdown (3 条件比較つき)
```

### 生データの読み方

- **`conv.csv`**: 同じ `case_id` が複数行ある場合は失敗→再走の履歴。`stable=true` の行だけが最終確定値 (54 行)。
- **`conv_trials.jsonl`**: 同様に `(case_id, turn)` の後勝ちで dedup する。`dump_transcripts.py` がそれをやっている。
- **`responses/responses/<case>/turn_NN.json`**: llama.cpp の `timings` フィールドに prefill/gen ms、spec decoding なら `draft_n` / `draft_n_accepted` も入る。
- **`logs/logs/<case>.log`**: `using device Vulkan0 (AMD Radeon 780M Graphics)` と出ているので iGPU 推論である事が確認できる。

## 再現方法

```bash
# 前提: C:\llm-exp\ 配下に llama.cpp (b8672+) と models/ (Q4_K_M gguf 6 種 + draft 0.5B) を配置
pip install -r requirements.txt             # matplotlib のみ (bench は stdlib)
python scripts/bench_conv.py                 # 54 ランを resume-safe に実行
python scripts/analyze.py                    # 集計・可視化
python scripts/dump_transcripts.py           # 3 条件比較つきトランスクリプト生成
```

`--only M3B M7B` でモデルを絞れる。`conv.csv` に `stable=true` 行があるケースはスキップされるので
途中落ちしても同じコマンドで再開可能。

## 既知の限界

- **M72B は iGPU VRAM を超える** (Q4_K_M 40GB vs 実効 UMA 16GB 相当) ため、`-ngl 18 -c 6144` で
  部分オフロードに切り替えている。他モデルは `-ngl 999 -c 8192` で完全オフロード。
  gen スループットは CPU 律速で 1.1 tok/s 程度 (絶対値は他モデルと直接比較不可)。
- Vulkan backend / iGPU UMA 固有の事情で、連続実行中に稀に TCP RST で応答が途切れることがある
  (bench 側で 3 回リトライ + llama-server ゾンビクリーンアップで吸収)。

## ライセンス

MIT License. 詳細は [LICENSE](LICENSE) を参照。
