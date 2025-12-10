import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 日本語フォント設定
plt.rcParams['font.family'] = 'MS Gothic'

# CSVを読み込み
df = pd.read_csv('output/merchant_grouping_master.csv')

# keywordごとのcount合計を計算し、降順にソート
group_counts = df.groupby('keyword')['count'].sum().sort_values(ascending=False)

# 累積割合を計算
cumsum = group_counts.cumsum()
cumsum_percent = cumsum / group_counts.sum() * 100

# パレート図を描画
fig, ax1 = plt.subplots(figsize=(14, 7))

# 棒グラフ（count合計）
x = range(len(group_counts))
ax1.bar(x, group_counts.values, color='steelblue', alpha=0.7)
ax1.set_xlabel('キーワード（count合計の降順）')
ax1.set_ylabel('count合計', color='steelblue')
ax1.tick_params(axis='y', labelcolor='steelblue')
ax1.set_xticks([])  # X軸ラベルは多すぎるので非表示

# 累積割合の折れ線グラフ（右軸）
ax2 = ax1.twinx()
ax2.plot(x, cumsum_percent.values, color='red', linewidth=2)
ax2.set_ylabel('累積割合 (%)', color='red')
ax2.tick_params(axis='y', labelcolor='red')
ax2.set_ylim(0, 105)

# 80%ラインを追加
ax2.axhline(y=80, color='green', linestyle='--', linewidth=1, label='80%ライン')

# 80%に達するグループ数を計算
idx_80 = np.searchsorted(cumsum_percent.values, 80)
ax2.axvline(x=idx_80, color='green', linestyle='--', linewidth=1)

plt.title(f'パレート図: キーワード別count合計\n（上位{idx_80:,}グループで80%をカバー）')
plt.tight_layout()
plt.show()

# 参考情報を表示
print("=" * 60)
print("パレート分析結果")
print("=" * 60)
print(f"全keywordユニーク数: {len(group_counts):,}")
print(f"全count合計: {group_counts.sum():,}")
print()
print("累積カバー率:")
for percent in [50, 80, 90, 95, 99]:
    idx = np.searchsorted(cumsum_percent.values, percent)
    if idx < len(group_counts):
        threshold_value = group_counts.iloc[idx]
        print(f"  上位 {idx:,} グループ ({idx/len(group_counts)*100:.1f}%) で {percent}%カバー (閾値: {threshold_value:,})")
print()
print("上位グループの詳細:")
for i in range(min(10, len(group_counts))):
    print(f"  {i+1}. {group_counts.index[i]}: {group_counts.iloc[i]:,}")
