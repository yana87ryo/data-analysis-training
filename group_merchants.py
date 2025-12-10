import pandas as pd
import glob
import os
import sys
import unicodedata
from difflib import SequenceMatcher

# Windows環境での日本語出力対応
sys.stdout.reconfigure(encoding='utf-8')

# 類似度の閾値（0.0〜1.0、高いほど厳密）
SIMILARITY_THRESHOLD = 0.8


def normalize_text(text):
    """テキストを正規化する（表記ゆれ統一）"""
    if pd.isna(text):
        return ""
    text = str(text).strip()
    # NFKC正規化：全角英数字→半角、半角カタカナ→全角
    text = unicodedata.normalize('NFKC', text)
    # 小文字化
    text = text.lower()
    return text


def calc_similarity(str1, str2):
    """2つの文字列の類似度を計算（0.0〜1.0）"""
    return SequenceMatcher(None, str1, str2).ratio()


def group_merchants(merchant_names, threshold=SIMILARITY_THRESHOLD):
    """店名を類似度でグルーピングする"""
    groups = []  # [(代表名, [メンバーリスト]), ...]

    for name in merchant_names:
        normalized = normalize_text(name)
        if not normalized:
            continue

        # 既存グループとの類似度をチェック
        matched_group = None
        max_similarity = 0

        for i, (rep_name, members) in enumerate(groups):
            rep_normalized = normalize_text(rep_name)
            similarity = calc_similarity(normalized, rep_normalized)

            if similarity >= threshold and similarity > max_similarity:
                max_similarity = similarity
                matched_group = i

        if matched_group is not None:
            # 既存グループに追加
            groups[matched_group][1].append(name)
        else:
            # 新規グループ作成
            groups.append((name, [name]))

    return groups


def main():
    # CSVファイルを取得
    csv_dir = 'data/monthly-individual-merchant-profile-vectors-v02-2x2'
    csv_files = sorted(glob.glob(f'{csv_dir}/2*.csv'))

    print("=" * 60)
    print("店名グルーピング")
    print("=" * 60)
    print(f"対象ファイル数: {len(csv_files)} 件")
    print(f"類似度閾値: {SIMILARITY_THRESHOLD * 100:.0f}%")
    print()

    # 全ファイルから店名を抽出
    all_merchants = set()
    for csv_file in csv_files:
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        # Merchant Name列を取得（4列目）
        merchant_col = df.columns[3]
        merchants = df[merchant_col].dropna().unique()
        all_merchants.update(merchants)

    merchant_list = sorted(all_merchants)
    print(f"ユニークな店名数: {len(merchant_list)} 件")
    print()

    # グルーピング実行
    groups = group_merchants(merchant_list, SIMILARITY_THRESHOLD)

    # 結果表示
    print("=" * 60)
    print("グルーピング結果")
    print("=" * 60)
    print(f"グループ数: {len(groups)} 件")
    print()

    # 複数メンバーを持つグループのみ表示
    multi_member_groups = [(rep, members) for rep, members in groups if len(members) > 1]

    if multi_member_groups:
        print("【複数店舗を含むグループ】")
        print("-" * 40)
        for i, (rep_name, members) in enumerate(multi_member_groups, 1):
            print(f"\nグループ {i}: {rep_name}")
            for member in members:
                print(f"  - {member}")
    else:
        print("複数店舗を含むグループはありませんでした。")

    print()
    print("=" * 60)
    print("【全グループ一覧】")
    print("-" * 40)
    for i, (rep_name, members) in enumerate(groups, 1):
        if len(members) == 1:
            print(f"{i}. {rep_name}")
        else:
            print(f"{i}. {rep_name} ({len(members)}件)")


if __name__ == "__main__":
    main()
