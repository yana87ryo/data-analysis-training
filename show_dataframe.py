import pandas as pd
import glob
import os

# カラム名を明示的に指定
column_names = [
    'Period',
    'Date',
    'Merchant ID',
    'Merchant Name',
    '#Users',
    'Value',
    '#Trans.',
    'Avg. Age',
    'Std. Age',
    '#Users by Gender (Male)',
    '#Users by Gender (Female)',
    '#Users by Gender (Unknown)',
    '#Users by Card Type (Cash+Debit)',
    '#Users by Card Type (Debit)',
    '#Users by Web Registration (Registered)',
    '#Users by Web Registration (Not Registered)',
    '#Users by Payment Method Value Order (online,In-person,Unknown)',
    '#Users by Payment Method Value Order (Online,Unknown,In-person)',
    '#Users by Payment Method Value Order (In-person, Online,Unknown)',
    '#Users by Payment Method Value Order (In-person,Unknown,Online)',
    '#Users by Payment Method Value Order (Unknown,Online,In-person)',
    '#Users by Payment Method Value Order (Unknown,In-person,Online)',
    '#Users by Payment Method #Trans. Order (Online,In-person,Unknown)',
    '#Users by Payment Method #Trans. Order (online,Unknown, In-person)',
    '#Users by Payment Method #Trans. Order (In-person,Online,Unknown)',
    '#Users by Payment Method #Trans. Order (In-person,Unknown,Online)',
    '#Users by Payment Method #Trans. Order (Unknown,Online,In-person)',
    '#Users by Payment Method #Trans. Order (Unknown, In-person,Online)',
    'Value by Payment Method (Online)',
    'Value by Payment Method (In-person)',
    'Value by Payment Method (Unknown)',
    '#Trans. by Payment Method (Online)',
    '#Trans. by Payment Method (In-person)',
    '#Trans. by Payment Method (Unknown)',
    'Value / trans.',
    'CDF VT(i)',
    'CDF #Trans.(j)',
    '2DR (2x2, VTxT) - VT(I)',
    '2DR (2x2 VTxT) - #Trans.(j)',
    '2DR Cell (2x2, VTxT)',
    'Prev. CDF #Trans.(j)',
    'Prev. CDF VT(i)',
    'Prev. 2DR (2x2, VTxT) - #Trans. (j)',
    'Prev. 2DR (2x2,  VTxT)- VT(i)',
    'Prev. 2DR Cell (2x2,  VTxT)'
]

# 複数CSVファイルを読み込む（24277〜24300）
csv_files = sorted(glob.glob('sample/2*.csv'))

print(f"=== 読み込み対象ファイル ({len(csv_files)}件) ===")
for f in csv_files:
    print(f"  - {os.path.basename(f)}")
print()

# 全ファイルを結合
dfs = []
for csv_file in csv_files:
    df = pd.read_csv(csv_file, encoding='utf-8-sig', header=0, names=column_names)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# データフレームの基本情報を表示
print("=== データフレームの形状 ===")
print(f"行数: {df_all.shape[0]}, 列数: {df_all.shape[1]}")
print(f"Period範囲: {df_all['Period'].min()} 〜 {df_all['Period'].max()}")
print()

print("=== カラム名一覧 ===")
for i, col in enumerate(column_names):
    print(f"{i+1}. {col}")
print()

print("=== データフレームの内容（先頭10行） ===")
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
print(df_all.head(10))
print()

print("=== データフレームの内容（末尾10行） ===")
print(df_all.tail(10))
