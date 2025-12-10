import pandas as pd
import glob
import os
import sys

# Windows環境での日本語出力対応
sys.stdout.reconfigure(encoding='utf-8')

# CSVファイルを取得
csv_dir = 'data/monthly-individual-merchant-profile-vectors-v02-2x2'
csv_files = sorted(glob.glob(f'{csv_dir}/2*.csv'))

print("=" * 60)
print("CSVファイル件数カウント")
print("=" * 60)
print()

# ファイル数
print(f"【ファイル数】{len(csv_files)} 件")
print()

# 各ファイルの行数をカウント
print("【各ファイルの行数】")
print("-" * 40)

total_rows = 0
file_counts = []

for csv_file in csv_files:
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    row_count = len(df)
    total_rows += row_count
    file_counts.append((os.path.basename(csv_file), row_count))
    print(f"  {os.path.basename(csv_file)}: {row_count:,} 行")

print("-" * 40)
print()

# 合計
print(f"【合計行数】{total_rows:,} 行")
print()

# 統計情報
if file_counts:
    counts = [c[1] for c in file_counts]
    print("【統計情報】")
    print(f"  最小行数: {min(counts):,} 行")
    print(f"  最大行数: {max(counts):,} 行")
    print(f"  平均行数: {sum(counts) / len(counts):,.1f} 行")
