import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'MS Gothic'

# データ読み込み
df = pd.read_csv('sample/24277.csv', encoding='utf-8-sig')
df['Date'] = pd.to_datetime(df['Date'])

# 3x4のグリッドレイアウトを作成
fig, axes = plt.subplots(3, 4, figsize=(16, 12))
fig.suptitle('マーチャント取引データ分析', fontsize=16)

# 1. 日別取引額の折れ線グラフ
ax1 = axes[0, 0]
ax1.plot(df['Date'], df['Value'], marker='o', color='blue')
ax1.set_title('日別取引額')
ax1.set_xlabel('日付')
ax1.set_ylabel('取引額')
ax1.tick_params(axis='x', rotation=45)

# 2. 日別トランザクション数の折れ線グラフ
ax2 = axes[0, 1]
ax2.plot(df['Date'], df['#Trans.'], marker='s', color='green')
ax2.set_title('日別トランザクション数')
ax2.set_xlabel('日付')
ax2.set_ylabel('トランザクション数')
ax2.tick_params(axis='x', rotation=45)

# 3. 日別ユーザー数の推移
ax3 = axes[0, 2]
ax3.plot(df['Date'], df['#Users'], marker='^', color='orange')
ax3.set_title('日別ユーザー数')
ax3.set_xlabel('日付')
ax3.set_ylabel('ユーザー数')
ax3.tick_params(axis='x', rotation=45)

# 4. 性別構成比（円グラフ）
ax4 = axes[0, 3]
gender_data = [
    df['#Users by Gender (Male)'].sum(),
    df['#Users by Gender (Female)'].sum(),
    df['#Users by Gender (Unknown)'].sum()
]
gender_labels = ['男性', '女性', '不明']
colors_gender = ['#4169E1', '#FF69B4', '#808080']
# 0の項目を除外
gender_data_filtered = [(d, l, c) for d, l, c in zip(gender_data, gender_labels, colors_gender) if d > 0]
if gender_data_filtered:
    data, labels, colors = zip(*gender_data_filtered)
    ax4.pie(data, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
ax4.set_title('性別構成比')

# 5. カードタイプ別ユーザー数（円グラフ）
ax5 = axes[1, 0]
card_data = [
    df['#Users by Card Type (Cash+Debit)'].sum(),
    df['#Users by Card Type (Debit)'].sum()
]
card_labels = ['Cash+Debit', 'Debit']
colors_card = ['#32CD32', '#FFD700']
ax5.pie(card_data, labels=card_labels, colors=colors_card, autopct='%1.1f%%', startangle=90)
ax5.set_title('カードタイプ別')

# 6. Web登録状況の構成比（円グラフ）
ax6 = axes[1, 1]
web_data = [
    df['#Users by Web Registration (Registered)'].sum(),
    df['#Users by Web Registration (Not Registered)'].sum()
]
web_labels = ['登録済み', '未登録']
colors_web = ['#00CED1', '#FF6347']
ax6.pie(web_data, labels=web_labels, colors=colors_web, autopct='%1.1f%%', startangle=90)
ax6.set_title('Web登録状況')

# 7. 決済方法別の取引額構成比
ax7 = axes[1, 2]
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
    ax7.pie(data, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
ax7.set_title('決済方法別取引額')

# 8. ユーザー数 vs 取引額の散布図
ax8 = axes[1, 3]
ax8.scatter(df['#Users'], df['Value'], color='purple', alpha=0.7)
ax8.set_title('ユーザー数 vs 取引額')
ax8.set_xlabel('ユーザー数')
ax8.set_ylabel('取引額')

# 9. 平均年齢 vs 取引額の散布図
ax9 = axes[2, 0]
ax9.scatter(df['Avg. Age'], df['Value'], color='red', alpha=0.7)
ax9.set_title('平均年齢 vs 取引額')
ax9.set_xlabel('平均年齢')
ax9.set_ylabel('取引額')

# 10. マーチャント別取引額ランキング（横棒グラフ）
ax10 = axes[2, 1]
top_merchants = df.nlargest(10, 'Value')[['Merchant Name', 'Value']]
ax10.barh(top_merchants['Merchant Name'], top_merchants['Value'], color='teal')
ax10.set_title('取引額TOP10')
ax10.set_xlabel('取引額')
ax10.invert_yaxis()

# 空白のサブプロットを非表示
axes[2, 2].axis('off')
axes[2, 3].axis('off')

plt.tight_layout()
plt.show()
