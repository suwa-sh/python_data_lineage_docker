# テストコマンド

## 事前準備

```bash
# 前回のテスト結果をクリア
rm -rf data/output/*
```

## analyze_delete.py のテスト

DELETE文・TRUNCATE文の抽出テスト

```bash
# test_delete_truncate.sql からDELETE/TRUNCATE文を抽出
python analyze_delete.py data/input/test_delete_truncate.sql data/output/analyze_delete/

# 結果確認
cat data/output/test_delete_truncate_delete.csv
```

## split.py のテスト

### 1. 基本的なSQL分割テスト

```bash
# test_split.sql を分割
python split.py data/input/test_split.sql data/output/split/

# 生成されたファイル確認
ls -la data/output/test_split/

# 分割結果確認
cat data/output/test_split/test_split_01.sql    # DDL
cat data/output/test_split/test_split_02.sql    # DDL
cat data/output/test_split/test_split_03.sql    # DDL
cat data/output/test_split/test_split_04.sql    # 一時テーブル
cat data/output/test_split/test_split_05.sql    # CTE
cat data/output/test_split/test_split_main.sql  # メインクエリ
```

### 2. サブクエリ抽出テスト（シンプル）

```bash
# test_simple_subquery.sql を分割
python split.py data/input/test_simple_subquery.sql data/output/split/

# 生成されたファイル確認
ls -la data/output/split/test_simple_subquery/

# サブクエリ抽出結果確認
cat data/output/split/test_simple_subquery/test_simple_subquery_03.sql  # 抽出されたサブクエリ（VIEW）
cat data/output/split/test_simple_subquery/test_simple_subquery_main.sql # メインクエリ（サブクエリ参照に変更）
```

### 3. 複雑なサブクエリ抽出テスト

```bash
# test_split_subquery.sql を分割
python split.py data/input/test_split_subquery.sql data/output/split/

# 生成されたファイル確認
ls -la data/output/split/test_split_subquery/

# 複雑なサブクエリの抽出結果確認
cat data/output/split/test_split_subquery/test_split_subquery_04.sql  # monthly_sales VIEW
cat data/output/split/test_split_subquery/test_split_subquery_05.sql  # regional_avg VIEW
cat data/output/split/test_split_subquery/test_split_subquery_main.sql # メインクエリ
```

### 4. 全ファイル連結テスト

分割されたファイルを連結して元のSQLと同等の動作をするか確認

```bash
# test_split.sql の分割結果を連結
cd data/output/split/test_split
cat test_split_*.sql test_split_main.sql > combined.sql
cd ../../..

# test_simple_subquery.sql の分割結果を連結
cd data/output/split/test_simple_subquery  
cat test_simple_subquery_*.sql test_simple_subquery_main.sql > combined.sql
cd ../../..

# test_split_subquery.sql の分割結果を連結
cd data/output/split/test_split_subquery
cat test_split_subquery_*.sql test_split_subquery_main.sql > combined.sql
cd ../../..
```

## テスト結果の確認

```bash
# 生成されたすべてのファイル一覧
find data/output/ -name "*.sql" -o -name "*.csv" | sort
```