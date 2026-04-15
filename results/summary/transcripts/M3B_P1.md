# Qwen2.5-3B-Instruct × RPG NPC 薬草商人リナ (/no_think)

temp=0, seed=42 の決定論セッティングなので C0/C1/C2 の返答テキストは同一。違うのは速度だけ。下のサマリと各ターン表がその比較。

## 20 ターン合計

| cond | total elapsed | prefill total | gen total | prompt tok合計 | gen tok合計 | 平均 prefill tps | 平均 gen tps | spec 受理 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C0 baseline (no cache) | 98.1s | 30.5s | 26.0s | 20670 | 862 | 673.5 | 33.2 | — |
| C1 cache_prompt | 73.1s | 3.1s | 28.5s | 21082 | 936 | 197.8 | 32.9 | — |
| C2 cache_prompt + spec | 83.1s | 3.2s | 38.5s | 22827 | 1187 | 186.7 | 31.0 | 715/1066 (67%) |

**C2/C0 speedup: 1.18x**  (98s → 83s)

**C1/C0 speedup: 1.34x**  (98s → 73s)

---

## Turn 1

_prompt 407 tok → gen 36 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 3.8s | 0.64s @ 635 tps | 1.1s @ 33.8 tps | — |
| C1 | 3.7s | 0.60s @ 682 tps | 1.1s @ 33.6 tps | — |
| C2 | 4.4s | 0.60s @ 680 tps | 1.7s @ 23.3 tps | 20/45 (44%) |

**User**: こんにちは、初めまして。

**Assistant**:

> こんにちは、旅の方かしら？お元気そうでうれしいね。どうぞ、お入りなさい。何か手助けできることがあれば教えてください。

## Turn 2

_prompt 471 tok → gen 62 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 4.7s | 0.73s @ 647 tps | 1.9s @ 33.4 tps | — |
| C1 | 4.1s | 0.13s @ 219 tps | 1.9s @ 32.7 tps | — |
| C2 | 4.7s | 0.13s @ 206 tps | 2.5s @ 27.0 tps | 34/66 (52%) |

**User**: このお店、薬草屋さんなんですね。どんな薬草があるんですか?

**Assistant**:

> はい、わたしが緑風堂の店主、リナです。ここには100種類以上の薬草が並んでいますよ。それぞれが独特の効能を持っていて、旅の途中で困ったことがあれば、ぜひお尋ねくださいね。

## Turn 3

_prompt 552 tok → gen 37 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 4.0s | 0.84s @ 658 tps | 1.1s @ 33.7 tps | — |
| C1 | 3.3s | 0.13s @ 154 tps | 1.1s @ 33.5 tps | — |
| C2 | 3.7s | 0.13s @ 139 tps | 1.5s @ 24.7 tps | 15/40 (38%) |

**User**: 一番人気の薬草は何ですか?

**Assistant**:

> 一番人気は、青い薔薇の花びらを使った薬草ですね。風邪や体の疲れを和らげてくれると評判よ。

## Turn 4

_prompt 607 tok → gen 39 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 4.1s | 0.92s @ 657 tps | 1.2s @ 33.7 tps | — |
| C1 | 3.4s | 0.13s @ 146 tps | 1.2s @ 33.4 tps | — |
| C2 | 3.9s | 0.13s @ 146 tps | 1.7s @ 33.1 tps | 34/45 (76%) |

**User**: それは何に効くんですか?

**Assistant**:

> 青い薔薇の花びらは、風邪や体の疲れを和らげてくれますよ。風邪がひき始めたら、飲んでみてね。

## Turn 5

_prompt 664 tok → gen 32 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 4.0s | 1.00s @ 664 tps | 1.0s @ 33.6 tps | — |
| C1 | 3.1s | 0.13s @ 147 tps | 1.0s @ 33.6 tps | — |
| C2 | 4.0s | 0.13s @ 131 tps | 1.8s @ 31.6 tps | 32/48 (67%) |

**User**: お値段はどれくらいでしょう?

**Assistant**:

> 青い薔薇の花びらの薬草は、一包目が10グラムで100ゴールドです。

## Turn 6

_prompt 724 tok → gen 45 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 4.5s | 1.08s @ 671 tps | 1.3s @ 33.5 tps | — |
| C1 | 4.0s | 0.13s @ 218 tps | 1.8s @ 33.1 tps | — |
| C2 | 4.7s | 0.13s @ 203 tps | 2.5s @ 28.8 tps | 40/67 (60%) |

**User**: 実は旅の途中で足をひねってしまって、効くものはありますか?

**Assistant**:

> 足をひねってしまったんですね。そんな時は、白い薔薇の葉を使った薬草が効果的よ。一包目が10グラムで100ゴールドです。

## Turn 7

_prompt 792 tok → gen 44 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 4.6s | 1.17s @ 678 tps | 1.3s @ 33.3 tps | — |
| C1 | 3.6s | 0.13s @ 180 tps | 1.4s @ 32.7 tps | — |
| C2 | 4.4s | 0.13s @ 166 tps | 2.1s @ 29.5 tps | 35/60 (58%) |

**User**: ありがとう、助かります。ところで、このお店はいつから?

**Assistant**:

> わたしが緑風堂をオープンしたのは、50年前のことよ。王都から亡命してきた元宮廷薬師の弟子だったから、ここに住むようになったのさ。

## Turn 8

_prompt 855 tok → gen 32 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 4.3s | 1.26s @ 680 tps | 1.0s @ 33.5 tps | — |
| C1 | 3.3s | 0.13s @ 151 tps | 1.0s @ 32.6 tps | — |
| C2 | 3.5s | 0.13s @ 153 tps | 1.3s @ 30.8 tps | 22/33 (67%) |

**User**: お一人で切り盛りしてるんですか?

**Assistant**:

> はい、わたし一人で切り盛りしていますよ。でも、旅の途中で仲間が寄ってくれるから、寂しくはないわ。

## Turn 9

_prompt 912 tok → gen 49 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 4.9s | 1.35s @ 677 tps | 1.5s @ 33.1 tps | — |
| C1 | 3.3s | 0.13s @ 194 tps | 1.1s @ 33.2 tps | — |
| C2 | 4.4s | 0.13s @ 186 tps | 2.2s @ 30.1 tps | 39/55 (71%) |

**User**: 森の奥には危険な魔物もいると聞きましたが…

**Assistant**:

> ははは、わたしが知っている限りでは、特に大きな魔物はいませんよ。でも、雷雨の日は気をつけてね。それに、ゴブリンの集団も気をつけないとね。

## Turn 10

_prompt 985 tok → gen 54 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 5.1s | 1.44s @ 683 tps | 1.6s @ 33.1 tps | — |
| C1 | 4.0s | 0.13s @ 187 tps | 1.8s @ 32.9 tps | — |
| C2 | 4.2s | 0.14s @ 170 tps | 2.0s @ 27.7 tps | 30/51 (59%) |

**User**: ゴブリンの集団が出るって、本当なんですか?

**Assistant**:

> はい、ゴブリンの集団が出る日もあるわ。特に夜が怖いね。でも、わたしが緑風堂を守るためには、どんな危険にも立ち向かう覚悟があるのさ。

## Turn 11

_prompt 1059 tok → gen 54 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 5.3s | 1.57s @ 676 tps | 1.6s @ 33.0 tps | — |
| C1 | 3.9s | 0.13s @ 156 tps | 1.7s @ 32.8 tps | — |
| C2 | 4.6s | 0.13s @ 143 tps | 2.4s @ 32.4 tps | 51/73 (70%) |

**User**: 旅人はどう身を守ればいいんでしょう?

**Assistant**:

> 旅人は、夜は森を抜けるのが危険だから、できるだけ昼間を選びなさいね。また、ゴブリンの集団が出る日は、村の警備隊に連絡してもらうのが一番よ。

## Turn 12

_prompt 1135 tok → gen 39 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 4.9s | 1.65s @ 686 tps | 1.2s @ 33.0 tps | — |
| C1 | 3.4s | 0.13s @ 171 tps | 1.2s @ 33.0 tps | — |
| C2 | 3.8s | 0.14s @ 155 tps | 1.6s @ 38.6 tps | 44/52 (85%) |

**User**: ところで、あなた自身が一番得意な薬草は?

**Assistant**:

> わたしの得意な薬草は、青い薔薇の花びらを使ったものよ。風邪や体の疲れを和らげてくれると評判よ。

## Turn 13

_prompt 1198 tok → gen 46 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 5.2s | 1.73s @ 691 tps | 1.4s @ 33.0 tps | — |
| C1 | 3.7s | 0.13s @ 186 tps | 1.5s @ 32.8 tps | — |
| C2 | 4.4s | 0.14s @ 168 tps | 2.2s @ 31.6 tps | 40/56 (71%) |

**User**: 朝露で採るんですか? どうしてその時間に?

**Assistant**:

> はい、朝露で採るんです。朝露は薬草の生命力を引き立てるんだよ。また、朝露で採った薬草は、味も香りも最高よ。

## Turn 14

_prompt 1266 tok → gen 41 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 5.2s | 1.83s @ 691 tps | 1.2s @ 32.9 tps | — |
| C1 | 3.5s | 0.14s @ 168 tps | 1.3s @ 32.9 tps | — |
| C2 | 4.0s | 0.14s @ 153 tps | 1.8s @ 32.4 tps | 36/49 (73%) |

**User**: 素敵ですね。夜はどんな風に過ごしてるんですか?

**Assistant**:

> 夜は、星を眺めたり、井戸水で淹れる茶を楽しんだりするのさ。また、村の噂話を聞かせてもらったりもするの。

## Turn 15

_prompt 1332 tok → gen 53 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 5.6s | 1.93s @ 691 tps | 1.6s @ 32.8 tps | — |
| C1 | 4.1s | 0.14s @ 190 tps | 1.9s @ 32.7 tps | — |
| C2 | 4.5s | 0.14s @ 173 tps | 2.2s @ 31.3 tps | 41/59 (69%) |

**User**: さっき星空が好きって言ってましたね、理由を聞いてもいいですか?

**Assistant**:

> はい、星空が好きよ。夜空の星は、まるで遠くの世界を繋ぐ橋みたいに見えるの。また、井戸水で淹れる茶を飲んだりすると、心も落ち着くわ。

## Turn 16

_prompt 1412 tok → gen 40 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 5.4s | 2.09s @ 676 tps | 1.2s @ 33.1 tps | — |
| C1 | 3.8s | 0.14s @ 203 tps | 1.6s @ 32.2 tps | — |
| C2 | 3.8s | 0.14s @ 203 tps | 1.6s @ 34.6 tps | 39/50 (78%) |

**User**: 井戸水で淹れたお茶、すごく気になります。飲んでみたいな。

**Assistant**:

> はい、井戸水で淹れたお茶は、特別な味わいよ。旅の途中で飲んでみて、その良さを実感してみてね。

## Turn 17

_prompt 1471 tok → gen 50 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 5.8s | 2.15s @ 683 tps | 1.5s @ 32.6 tps | — |
| C1 | 3.9s | 0.14s @ 146 tps | 1.7s @ 32.6 tps | — |
| C2 | 4.2s | 0.14s @ 145 tps | 2.0s @ 33.0 tps | 42/58 (72%) |

**User**: この村には他にどんなお店がありますか?

**Assistant**:

> この村には、木工の手芸屋さんや、野菜を販売する農家の小屋があるわ。また、近隣の村からも、様々な種類の商いが行われているのさ。

## Turn 18

_prompt 1543 tok → gen 58 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 6.2s | 2.30s @ 670 tps | 1.8s @ 32.5 tps | — |
| C1 | 4.9s | 0.14s @ 167 tps | 2.7s @ 31.9 tps | — |
| C2 | 5.2s | 0.14s @ 151 tps | 3.0s @ 33.3 tps | 69/90 (77%) |

**User**: 旅人としてぜひ見ておくべき場所はありますか?

**Assistant**:

> はい、見ておくべき場所はいくつかあるわ。まず、村の井戸水で淹れる茶を飲んでみてね。また、森の入り口の緑風堂で、薬草の種類を教えてもらうのもいいわ。

## Turn 19

_prompt 1616 tok → gen 30 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 5.4s | 2.39s @ 676 tps | 0.9s @ 33.0 tps | — |
| C1 | 3.1s | 0.13s @ 122 tps | 0.9s @ 32.9 tps | — |
| C2 | 3.3s | 0.13s @ 106 tps | 1.1s @ 36.5 tps | 29/33 (88%) |

**User**: いろいろ教えてくれてありがとうございました。

**Assistant**:

> どういたしまして、旅の方。何か手助けできることがあれば、いつでもお尋ねくださいね。お元気で。

## Turn 20

_prompt 1669 tok → gen 21 tok_

| cond | elapsed | prefill | gen | spec accept |
|---|---:|---:|---:|---:|
| C0 | 5.1s | 2.46s @ 677 tps | 0.6s @ 33.4 tps | — |
| C1 | 2.8s | 0.14s @ 170 tps | 0.6s @ 33.4 tps | — |
| C2 | 3.6s | 0.14s @ 157 tps | 1.4s @ 28.9 tps | 23/36 (64%) |

**User**: また立ち寄らせてください。あなたもお元気で。

**Assistant**:

> もちろんだよ、旅の方。またお立ち寄りくださいね。お元気で。
