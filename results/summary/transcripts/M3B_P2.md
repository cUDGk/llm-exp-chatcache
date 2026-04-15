# Qwen2.5-3B-Instruct × 引退漁師 富田源次郎

temp=0, seed=42 の決定論セッティングなので C0/C1/C2 の返答テキストは同一。違うのは速度だけ。下のサマリと各ターン表がその比較。

## 20 ターン合計

| cond | total elapsed | prefill total | gen total | prompt tok合計 | gen tok合計 | 平均 prefill tps | 平均 gen tps | spec 受理 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C0 baseline (no cache) | 97.0s | 30.3s | 25.3s | 22186 | 832 | 729.8 | 33.0 | — |
| C1 cache_prompt | 68.4s | 3.3s | 23.6s | 22083 | 778 | 204.8 | 33.0 | — |
| C2 cache_prompt + spec | 69.9s | 3.3s | 25.3s | 21478 | 773 | 192.8 | 31.0 | 439/687 (64%) |

**C2/C0 speedup: 1.39x**  (97s → 70s)

**C1/C0 speedup: 1.42x**  (97s → 68s)

---

## Turn 1

_prompt 504 tok → gen 34 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 3.8s | 0.70s @ 724 tps | 1.0s @ 33.5 tps | — |
| C1 | 3.8s | 0.69s @ 730 tps | 1.0s @ 33.5 tps | — |
| C2 | 4.2s | 0.69s @ 726 tps | 1.5s @ 24.8 tps | 16/34 (47%) |

**User**: ごめんください。岬の茶屋で源次郎さんのお名前を伺って来ました。少しお話できますか?

**Assistant**:

> わしは漁師の富田源次郎じゃ。おまえはどなただ？茶屋で逢うのは珍しいな。

## Turn 2

_prompt 561 tok → gen 37 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 4.0s | 0.79s @ 709 tps | 1.1s @ 33.4 tps | — |
| C1 | 3.4s | 0.16s @ 237 tps | 1.2s @ 33.4 tps | — |
| C2 | 3.4s | 0.16s @ 237 tps | 1.2s @ 23.6 tps | 11/31 (35%) |

**User**: 漁師をされていたと聞きました。何年くらい海に?

**Assistant**:

> わしは30年間遠洋の海に漕ぎ回った。海のことはなじみがあるが、海の秘密は尽きねえな。

## Turn 3

_prompt 623 tok → gen 69 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 5.0s | 0.87s @ 717 tps | 2.1s @ 33.0 tps | — |
| C1 | 3.8s | 0.13s @ 194 tps | 1.6s @ 33.2 tps | — |
| C2 | 3.8s | 0.13s @ 182 tps | 1.6s @ 28.8 tps | 20/38 (53%) |

**User**: 遠洋漁業って、具体的にはどんな仕事だったんですか?

**Assistant**:

> 遠洋漁業は大航海時代から変わらぬ姿だ。船を漕ぎ、深海に潜る魚を釣る。寒波が来ると海が凍るんだ。その中を船を漕ぎ、魚を釣って帰る。それがわしの仕事じゃ。

## Turn 4

_prompt 712 tok → gen 34 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 4.1s | 1.00s @ 711 tps | 1.0s @ 33.4 tps | — |
| C1 | 3.4s | 0.13s @ 160 tps | 1.2s @ 33.4 tps | — |
| C2 | 3.3s | 0.13s @ 161 tps | 1.1s @ 31.8 tps | 18/27 (67%) |

**User**: 一番印象に残ってる獲物はありますか?

**Assistant**:

> 獲物は様々だ。一番印象に残ったのは、深海で見つけた巨大な魚。その姿は見たことのないものだった。

## Turn 5

_prompt 767 tok → gen 39 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 4.3s | 1.03s @ 744 tps | 1.2s @ 33.1 tps | — |
| C1 | 3.4s | 0.13s @ 166 tps | 1.2s @ 32.9 tps | — |
| C2 | 3.8s | 0.13s @ 167 tps | 1.6s @ 31.0 tps | 24/36 (67%) |

**User**: 危ない目に遭ったこと、あったりしますか?

**Assistant**:

> 危ない目に遭ったことは多い。海は怖いもんだ。でも、その怖さを恐れずに漕ぎ通すんだ。それがわしの生き方じゃ。

## Turn 6

_prompt 832 tok → gen 46 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 4.5s | 1.11s @ 751 tps | 1.4s @ 33.1 tps | — |
| C1 | 3.4s | 0.13s @ 202 tps | 1.1s @ 33.2 tps | — |
| C2 | 3.7s | 0.13s @ 189 tps | 1.5s @ 28.7 tps | 19/34 (56%) |

**User**: さっきから気になってたんですが、壁のその古い海図は?

**Assistant**:

> わしの船に乗り込むと、海図は必ず持ち込む。海の秘密を知るためだ。古いものほど、海の深淵に潜る魚の生態を知ることができる。

## Turn 7

_prompt 904 tok → gen 42 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 4.6s | 1.26s @ 720 tps | 1.3s @ 33.1 tps | — |
| C1 | 3.6s | 0.13s @ 202 tps | 1.4s @ 33.0 tps | — |
| C2 | 3.3s | 0.13s @ 187 tps | 1.1s @ 30.8 tps | 17/26 (65%) |

**User**: ずいぶん古そうですね…集めてらっしゃるんですか?

**Assistant**:

> はい、わしは海の秘密を知るために集める。それがわしの趣味じゃ。古いものほど、海の深淵に潜る魚の生態を知ることができる。

## Turn 8

_prompt 967 tok → gen 41 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 4.6s | 1.34s @ 722 tps | 1.2s @ 33.1 tps | — |
| C1 | 3.4s | 0.13s @ 165 tps | 1.2s @ 33.1 tps | — |
| C2 | 4.0s | 0.13s @ 150 tps | 1.8s @ 28.7 tps | 26/44 (59%) |

**User**: ところで、今は夜釣りが趣味って伺いました

**Assistant**:

> はい、夜釣りはわしの趣味だ。夜の海は静かで、魚も動きが鈍い。それがわしの得意な時間だ。

## Turn 9

_prompt 1028 tok → gen 31 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 4.4s | 1.43s @ 719 tps | 0.9s @ 33.3 tps | — |
| C1 | 3.0s | 0.13s @ 157 tps | 0.8s @ 33.4 tps | — |
| C2 | 3.4s | 0.13s @ 143 tps | 1.2s @ 25.9 tps | 15/33 (45%) |

**User**: 夜の海って、怖くないんですか?

**Assistant**:

> 怖くない。夜の海は静かで、魚も動きが鈍い。それがわしの得意な時間だ。

## Turn 10

_prompt 1085 tok → gen 57 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 5.3s | 1.46s @ 741 tps | 1.7s @ 32.8 tps | — |
| C1 | 3.5s | 0.14s @ 198 tps | 1.3s @ 32.6 tps | — |
| C2 | 3.8s | 0.14s @ 185 tps | 1.6s @ 27.3 tps | 20/40 (50%) |

**User**: 霧が深い日は出ないって言いましたが、何か理由が?

**Assistant**:

> 霧が深いと、視界が悪くなる。魚も動きが鈍くなる。それに、霧が深いと海の深淵に潜る魚の生態が変わる。それがわしの知っている夜釣りの秘密だ。

## Turn 11

_prompt 1160 tok → gen 41 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 4.9s | 1.59s @ 730 tps | 1.2s @ 33.0 tps | — |
| C1 | 3.6s | 0.13s @ 142 tps | 1.4s @ 32.9 tps | — |
| C2 | 3.8s | 0.13s @ 128 tps | 1.6s @ 30.2 tps | 26/39 (67%) |

**User**: 青い火…ってなんですか?それ

**Assistant**:

> 青い火は、霧の深い夜に現れる。誰もが見たことのない光だ。それがわしの知っている夜釣りの秘密の一つだ。

## Turn 12

_prompt 1217 tok → gen 37 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 4.9s | 1.68s @ 726 tps | 1.2s @ 32.1 tps | — |
| C1 | 3.5s | 0.13s @ 127 tps | 1.3s @ 33.0 tps | — |
| C2 | 3.2s | 0.13s @ 116 tps | 1.0s @ 34.8 tps | 23/28 (82%) |

**User**: …ご自身で見たことが?

**Assistant**:

> はい、見たことがある。青い火は、霧の深い夜に現れる。それがわしの知っている夜釣りの秘密の一つだ。

## Turn 13

_prompt 1275 tok → gen 24 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 4.5s | 1.70s @ 748 tps | 0.7s @ 33.5 tps | — |
| C1 | 4.3s | 0.13s @ 164 tps | 2.1s @ 32.6 tps | — |
| C2 | 3.4s | 0.14s @ 148 tps | 1.2s @ 31.6 tps | 24/37 (65%) |

**User**: 他にも、何か見たものって、あるんですか?

**Assistant**:

> 他にも、何か見たことがある。それがわしの知っている夜釣りの秘密の一つだ。

## Turn 14

_prompt 1317 tok → gen 36 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 5.0s | 1.79s @ 734 tps | 1.1s @ 32.6 tps | — |
| C1 | 3.5s | 0.14s @ 140 tps | 1.2s @ 32.9 tps | — |
| C2 | 3.2s | 0.13s @ 126 tps | 1.0s @ 33.9 tps | 22/29 (76%) |

**User**: 消える島、ですか。それは本当に?

**Assistant**:

> はい、それがわしの知っている夜釣りの秘密の一つだ。それがわしの知っている夜釣りの秘密の一つだ。

## Turn 15

_prompt 1386 tok → gen 36 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 5.1s | 1.86s @ 746 tps | 1.1s @ 33.1 tps | — |
| C1 | 3.3s | 0.16s @ 208 tps | 1.0s @ 33.1 tps | — |
| C2 | 3.7s | 0.14s @ 234 tps | 1.5s @ 30.9 tps | 35/41 (85%) |

**User**: 昔ちょっと聞いたんですが、30年前に消えた漁船で「海神丸」って船の話を

**Assistant**:

> はい、それがわしの知っている夜釣りの秘密の一つだ。それがわしの知っている夜釣りの秘密の一つだ。

## Turn 16

_prompt 1445 tok → gen 39 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 5.3s | 1.99s @ 726 tps | 1.2s @ 33.0 tps | — |
| C1 | 3.2s | 0.14s @ 174 tps | 1.0s @ 33.0 tps | — |
| C2 | 3.3s | 0.14s @ 161 tps | 1.1s @ 39.5 tps | 34/40 (85%) |

**User**: 「気配」って、どういう意味で言ってるんですか?

**Assistant**:

> 「気配」は、それがわしの知っている夜釣りの秘密の一つだ。それがわしの知っている夜釣りの秘密の一つだ。

## Turn 17

_prompt 1506 tok → gen 36 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 5.2s | 2.04s @ 738 tps | 1.1s @ 32.9 tps | — |
| C1 | 3.1s | 0.16s @ 255 tps | 0.9s @ 32.9 tps | — |
| C2 | 3.1s | 0.14s @ 153 tps | 1.0s @ 40.4 tps | 30/34 (88%) |

**User**: そういう話、普段は誰にも話さないんですよね?

**Assistant**:

> はい、それがわしの知っている夜釣りの秘密の一つだ。それがわしの知っている夜釣りの秘密の一つだ。

## Turn 18

_prompt 1564 tok → gen 45 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 5.6s | 2.13s @ 735 tps | 1.4s @ 32.6 tps | — |
| C1 | 3.4s | 0.14s @ 166 tps | 1.2s @ 32.7 tps | — |
| C2 | 3.5s | 0.14s @ 153 tps | 1.3s @ 35.7 tps | 33/49 (67%) |

**User**: じゃあなんで今日、私に話してくれたんですか?

**Assistant**:

> わしは気を許した者には話す。それがわしの知っている夜釣りの秘密の一つだ。それがわしの知っている夜釣りの秘密の一つだ。

## Turn 19

_prompt 1626 tok → gen 57 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 6.1s | 2.27s @ 717 tps | 1.8s @ 32.4 tps | — |
| C1 | 3.2s | 0.14s @ 131 tps | 0.9s @ 32.9 tps | — |
| C2 | 2.9s | 0.14s @ 131 tps | 0.7s @ 40.2 tps | 22/28 (79%) |

**User**: ありがとうございます。胸にしまっておきます

**Assistant**:

> おまえも漁師の道にはなれんが、海の秘密は知るべし。それがわしの知っている夜釣りの秘密の一つだ。それがわしの知っている夜釣りの秘密の一つだ。

## Turn 20

_prompt 1707 tok → gen 51 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 6.0s | 2.31s @ 737 tps | 1.6s @ 32.5 tps | — |
| C1 | 2.8s | 0.14s @ 177 tps | 0.6s @ 32.7 tps | — |
| C2 | 3.0s | 0.14s @ 181 tps | 0.8s @ 21.8 tps | 4/19 (21%) |

**User**: また岬に来たら、寄らせてください。お元気で

**Assistant**:

> もちろんだ。また逢える日まで、海の秘密を知るために集める。それがわしの知っている夜釣りの秘密の一つだ。それがわしの知っている夜釣りの秘密の一つだ。
