import pandas as pd
import glob
import os
import unicodedata
import re
import random
from collections import defaultdict, Counter
from difflib import SequenceMatcher
from IPython.display import clear_output

# =============================================================================
# 設定値（ここを変更するとプログラム全体に反映されます）
# =============================================================================

# 前方一致の文字数
# - 正規化後の先頭N文字が同じなら同一グループとみなす
# - 小さいと誤グループ化が増える、大きいと類似店名を見逃す
PREFIX_LENGTH = 3

# =============================================================================


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


def select_best_representative(members, normalized_cache=None):
    """グループ内で最も他メンバーと類似度が高い店名を代表として選ぶ"""
    if len(members) <= 1:
        return members[0] if members else ""

    # 大きなグループはサンプリングして計算量を削減
    MAX_SAMPLE = 50
    if len(members) > MAX_SAMPLE:
        sample_members = random.sample(members, MAX_SAMPLE)
    else:
        sample_members = members

    def get_normalized(text):
        if normalized_cache and text in normalized_cache:
            return normalized_cache[text]
        return normalize_text(text)

    def calc_similarity(str1, str2):
        return SequenceMatcher(None, str1, str2).ratio()

    best_rep = members[0]
    best_total_similarity = 0

    for candidate in sample_members:
        candidate_norm = get_normalized(candidate)
        total_similarity = sum(
            calc_similarity(candidate_norm, get_normalized(other))
            for other in sample_members if other != candidate
        )
        if total_similarity > best_total_similarity:
            best_total_similarity = total_similarity
            best_rep = candidate

    return best_rep


def group_merchants_fast(merchant_names, prefix_len=PREFIX_LENGTH):
    """店名を前方一致でグルーピングする（高速版）

    正規化後の先頭N文字が同じなら同一グループとみなす。
    類似度計算を省略することで高速化。

    Args:
        merchant_names: 店名リスト
        prefix_len: 前方一致の文字数

    Returns:
        [(代表名, [メンバーリスト]), ...]
    """
    total = len(merchant_names)

    # 正規化結果をキャッシュ
    normalized_cache = {}

    # 前方一致でグループ化: {先頭N文字: [店名リスト]}
    prefix_groups = defaultdict(list)

    for idx, name in enumerate(merchant_names):
        # キャッシュを活用した正規化
        if name in normalized_cache:
            normalized = normalized_cache[name]
        else:
            normalized = normalize_text(name)
            normalized_cache[name] = normalized

        if not normalized:
            continue

        # 進捗表示（10000件ごと）
        if idx > 0 and idx % 10000 == 0:
            clear_output(wait=True)
            print(f"グルーピング中: {idx:,}/{total:,} ({idx*100//total}%)")

        # 先頭N文字でグループ化
        prefix = normalized[:prefix_len] if len(normalized) >= prefix_len else normalized
        prefix_groups[prefix].append(name)

    clear_output(wait=True)
    print(f"グルーピング完了: {total:,}/{total:,} (100%) - グループ数: {len(prefix_groups):,}")

    # 各グループの代表名を再選定（最も他メンバーと類似する店名）
    print("代表名を再選定中...")
    result = []
    groups_list = list(prefix_groups.values())
    multi_member_count = sum(1 for members in groups_list if len(members) > 1)

    processed = 0
    for members in groups_list:
        if len(members) > 1:
            processed += 1
            if processed > 0 and processed % 1000 == 0:
                clear_output(wait=True)
                print(f"代表名再選定中: {processed:,}/{multi_member_count:,} ({processed*100//multi_member_count}%)")
            best_rep = select_best_representative(members, normalized_cache)
        else:
            best_rep = members[0]
        result.append((best_rep, members))

    clear_output(wait=True)
    print(f"完了: {len(result):,} グループ（うち複数メンバー: {multi_member_count:,}）")

    return result


def find_longest_common_substring(str1, str2):
    """2つの文字列の最長共通部分文字列を見つける"""
    if not str1 or not str2:
        return ""

    m, n = len(str1), len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    max_len = 0
    end_pos = 0

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > max_len:
                    max_len = dp[i][j]
                    end_pos = i

    return str1[end_pos - max_len:end_pos]


def extract_common_keyword_from_group(members):
    """グループ内の店舗名から共通キーワードを抽出する

    最長店舗名と最短店舗名を比較し、最長共通部分文字列をキーワードとする
    """
    if not members or len(members) < 2:
        return ""

    normalized_members = [normalize_text(m) for m in members if normalize_text(m)]

    if len(normalized_members) < 2:
        return ""

    # 最長と最短の店舗名を取得
    sorted_by_length = sorted(normalized_members, key=len)
    shortest = sorted_by_length[0]
    longest = sorted_by_length[-1]

    # 最長共通部分文字列を求める
    common = find_longest_common_substring(shortest, longest)

    # 最終的なキーワードを整形
    if common:
        common = re.sub(r'(店|支店|号店|fc|フランチャイズ|本店|駅前|駅|東口|西口|南口|北口)$', '', common)
        common = common.strip()

    if len(common) >= 2:
        return common

    # 見つからない場合は最短の店舗名から生成
    keyword = shortest
    keyword = re.sub(r'\d+', '', keyword)
    keyword = re.sub(r'(店|支店|号店|fc|フランチャイズ|本店|駅前|駅|東口|西口|南口|北口)$', '', keyword)
    keyword = re.sub(r'\s+', '', keyword)
    return keyword if len(keyword) >= 2 else shortest[:10]


def export_grouping_master(groups, merchant_counts, output_path='output/merchant_grouping_master.csv'):
    """グルーピング結果をマスタCSVとして出力する

    ※ 2件以上のグループのみ出力（1件のグループは出力しない）

    Args:
        groups: グルーピング結果 [(代表名, [メンバーリスト]), ...]
        merchant_counts: 各店舗名の出現回数 Counter
        output_path: 出力ファイルパス
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    rows = []
    for group_name, members in groups:
        # キーワード抽出（1件の場合は店名をそのままキーワードに）
        if len(members) >= 2:
            keyword = extract_common_keyword_from_group(members)
        else:
            keyword = normalize_text(members[0])

        # グループ全体のcount合計を計算
        group_count = sum(merchant_counts.get(member, 0) for member in members)

        for member in members:
            rows.append({
                'keyword': keyword,
                'merchant_name': member,
                'count': merchant_counts.get(member, 0),
                'group_count': group_count
            })

    df = pd.DataFrame(rows)

    # keywordごとのgroup_countを取得（重複排除）
    keyword_counts = df.drop_duplicates('keyword')[['keyword', 'group_count']].copy()
    keyword_counts = keyword_counts.sort_values('group_count', ascending=False)

    # 累積計算
    keyword_counts['cumsum_count'] = keyword_counts['group_count'].cumsum()
    total = keyword_counts['group_count'].sum()
    keyword_counts['cumsum_percent'] = (keyword_counts['cumsum_count'] / total * 100).round(2)

    # 元のDataFrameにマージ
    df = df.merge(keyword_counts[['keyword', 'cumsum_count', 'cumsum_percent']], on='keyword')

    # group_countの降順でソート
    df = df.sort_values('group_count', ascending=False)

    df.to_csv(output_path, index=False, encoding='utf-8-sig')

    return output_path, len(rows)


def main():
    # CSVファイルを取得
    csv_dir = 'data'
    csv_files = sorted(glob.glob(f'{csv_dir}/tran*.csv'))

    print("=" * 60)
    print("店名グルーピングマスタ生成（高速版）")
    print("=" * 60)
    print(f"対象ファイル数: {len(csv_files)} 件")
    print(f"前方一致文字数: {PREFIX_LENGTH} 文字")
    print()

    # 全ファイルから店名を抽出（出現回数もカウント）
    print("店名を抽出中...")
    merchant_counts = Counter()
    for i, csv_file in enumerate(csv_files):
        if i > 0 and i % 10 == 0:
            clear_output(wait=True)
            print(f"ファイル読み込み中: {i}/{len(csv_files)}")
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        merchant_col = df.columns[5]
        merchants = df[merchant_col].dropna()
        merchant_counts.update(merchants)

    merchant_list = sorted(merchant_counts.keys())
    clear_output(wait=True)
    print(f"ユニークな店名数: {len(merchant_list):,} 件")
    print()

    # グルーピング実行
    groups = group_merchants_fast(merchant_list, PREFIX_LENGTH)

    # 結果表示
    print("=" * 60)
    print("グルーピング結果")
    print("=" * 60)
    print(f"グループ数: {len(groups):,} 件")
    print()

    multi_member_groups = [(rep, members) for rep, members in groups if len(members) > 1]

    if multi_member_groups:
        print("【複数店舗を含むグループ（先頭10件）】")
        print("-" * 40)
        for i, (rep_name, members) in enumerate(multi_member_groups[:10], 1):
            print(f"\nグループ {i}: {rep_name}")
            for member in members[:5]:
                print(f"  - {member}")
            if len(members) > 5:
                print(f"  ... 他 {len(members) - 5} 件")
        if len(multi_member_groups) > 10:
            print(f"\n... 他 {len(multi_member_groups) - 10} グループ")
    else:
        print("複数店舗を含むグループはありませんでした。")

    # マスタCSV出力
    print()
    print("=" * 60)
    print("マスタCSV出力")
    print("=" * 60)
    output_path, row_count = export_grouping_master(groups, merchant_counts)
    print(f"出力ファイル: {output_path}")
    print(f"出力レコード数: {row_count:,} 件")
    print()
    print("【CSVカラム説明】")
    print("  - keyword: 部分一致用キーワード（正規化済み）")
    print("  - merchant_name: 元の店名")
    print("  - count: 元データでの出現回数")
    print("  - group_count: グループ全体のcount合計")
    print("  - cumsum_count: group_countの累積値（降順）")
    print("  - cumsum_percent: 累積割合（%）")

main()
