import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import glob

matplotlib.rcParams['font.family'] = 'MS Gothic'

# 複数CSVファイルを読み込む（24277〜24300）
csv_files = sorted(glob.glob('sample/2*.csv'))
dfs = []
for csv_file in csv_files:
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    dfs.append(df)

df = pd.concat(dfs, ignore_index=True)
df['Date'] = pd.to_datetime(df['Date'])

print(f"読み込みファイル数: {len(csv_files)}")
print(f"総レコード数: {len(df)}")
print(f"Period範囲: {df['Period'].min()} 〜 {df['Period'].max()}")

# Period別の集計データを作成（月別推移用）
df_monthly = df.groupby('Period').agg({
    'Value': 'sum',
    '#Trans.': 'sum',
    '#Users': 'sum',
    '#Users by Gender (Male)': 'sum',
    '#Users by Gender (Female)': 'sum',
    '#Users by Gender (Unknown)': 'sum',
    'Value by Payment Method (Online)': 'sum',
    'Value by Payment Method (In-person)': 'sum',
}).reset_index()

# 4x3のグリッドレイアウトを作成
fig, axes = plt.subplots(4, 3, figsize=(16, 16))
fig.suptitle(f'マーチャント取引データ分析（Period: {df["Period"].min()}〜{df["Period"].max()}）', fontsize=16)

# === 月別推移グラフ（3種） ===

# 1. 月別取引額の推移
ax1 = axes[0, 0]
ax1.plot(df_monthly['Period'], df_monthly['Value'], marker='o', color='blue', linewidth=2)
ax1.set_title('月別取引額推移')
ax1.set_xlabel('Period')
ax1.set_ylabel('取引額')
ax1.ticklabel_format(style='plain', axis='y')

# 2. 月別トランザクション数の推移
ax2 = axes[0, 1]
ax2.plot(df_monthly['Period'], df_monthly['#Trans.'], marker='s', color='green', linewidth=2)
ax2.set_title('月別トランザクション数推移')
ax2.set_xlabel('Period')
ax2.set_ylabel('トランザクション数')

# 3. 月別ユーザー数の推移
ax3 = axes[0, 2]
ax3.plot(df_monthly['Period'], df_monthly['#Users'], marker='^', color='orange', linewidth=2)
ax3.set_title('月別ユーザー数推移')
ax3.set_xlabel('Period')
ax3.set_ylabel('ユーザー数')

# === 日別推移グラフ（3種） ===

# 4. 日別取引額の折れ線グラフ
ax4 = axes[1, 0]
ax4.plot(df['Date'], df['Value'], marker='.', color='blue', alpha=0.5, markersize=2)
ax4.set_title('日別取引額')
ax4.set_xlabel('日付')
ax4.set_ylabel('取引額')
ax4.tick_params(axis='x', rotation=45)

# 5. 日別トランザクション数の折れ線グラフ
ax5 = axes[1, 1]
ax5.plot(df['Date'], df['#Trans.'], marker='.', color='green', alpha=0.5, markersize=2)
ax5.set_title('日別トランザクション数')
ax5.set_xlabel('日付')
ax5.set_ylabel('トランザクション数')
ax5.tick_params(axis='x', rotation=45)

# 6. 日別ユーザー数の推移
ax6 = axes[1, 2]
ax6.plot(df['Date'], df['#Users'], marker='.', color='orange', alpha=0.5, markersize=2)
ax6.set_title('日別ユーザー数')
ax6.set_xlabel('日付')
ax6.set_ylabel('ユーザー数')
ax6.tick_params(axis='x', rotation=45)

# === 構成比グラフ（4種） ===

# 7. 性別構成比（円グラフ）
ax7 = axes[2, 0]
gender_data = [
    df['#Users by Gender (Male)'].sum(),
    df['#Users by Gender (Female)'].sum(),
    df['#Users by Gender (Unknown)'].sum()
]
gender_labels = ['男性', '女性', '不明']
colors_gender = ['#4169E1', '#FF69B4', '#808080']
gender_data_filtered = [(d, l, c) for d, l, c in zip(gender_data, gender_labels, colors_gender) if d > 0]
if gender_data_filtered:
    data, labels, colors = zip(*gender_data_filtered)
    ax7.pie(data, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
ax7.set_title('性別構成比')

# 8. カードタイプ別ユーザー数（円グラフ）
ax8 = axes[2, 1]
card_data = [
    df['#Users by Card Type (Cash+Debit)'].sum(),
    df['#Users by Card Type (Debit)'].sum()
]
card_labels = ['Cash+Debit', 'Debit']
colors_card = ['#32CD32', '#FFD700']
ax8.pie(card_data, labels=card_labels, colors=colors_card, autopct='%1.1f%%', startangle=90)
ax8.set_title('カードタイプ別')

# 9. Web登録状況の構成比（円グラフ）
ax9 = axes[2, 2]
web_data = [
    df['#Users by Web Registration (Registered)'].sum(),
    df['#Users by Web Registration (Not Registered)'].sum()
]
web_labels = ['登録済み', '未登録']
colors_web = ['#00CED1', '#FF6347']
ax9.pie(web_data, labels=web_labels, colors=colors_web, autopct='%1.1f%%', startangle=90)
ax9.set_title('Web登録状況')

# 10. 決済方法別の取引額構成比
ax10 = axes[3, 0]
payment_value = [
    df['Value by Payment Method (Online)'].sum(),
    df['Value by Payment Method (In-person)'].sum(),
    df['Value by Payment Method (Unknown)'].sum()
]
payment_labels = ['オンライン', '対面', '不明']
colors_payment = ['#9370DB', '#20B2AA', '#808080']
payment_filtered = [(d, l, c) for d, l, c in zip(payment_value, payment_labels, colors_payment) if d > 0]
if payment_filtered:
    data, labels, colors = zip(*payment_filtered)
    ax10.pie(data, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
ax10.set_title('決済方法別取引額')

# === 相関・ランキンググラフ（2種） ===

# 11. ユーザー数 vs 取引額の散布図
ax11 = axes[3, 1]
ax11.scatter(df['#Users'], df['Value'], color='purple', alpha=0.3, s=10)
ax11.set_title('ユーザー数 vs 取引額')
ax11.set_xlabel('ユーザー数')
ax11.set_ylabel('取引額')

# 12. マーチャント別取引額ランキング（横棒グラフ）
ax12 = axes[3, 2]
merchant_total = df.groupby('Merchant Name')['Value'].sum().nlargest(10)
ax12.barh(merchant_total.index, merchant_total.values, color='teal')
ax12.set_title('取引額TOP10マーチャント')
ax12.set_xlabel('取引額')
ax12.invert_yaxis()

plt.tight_layout()
plt.show()
