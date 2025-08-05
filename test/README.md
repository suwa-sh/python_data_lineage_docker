# テストコマンド

## 事前準備

```bash
# 前回のテスト結果をクリア
rm -rf test/output/*
```

## analyze_delete.py のテスト

DELETE文・TRUNCATE文の抽出テスト

```bash
# test_delete_truncate.sql からDELETE/TRUNCATE文を抽出
python analyze_delete.py test/input/test_delete_truncate.sql --output test/output/

# 結果確認
cat test/output/test_delete_truncate_delete.csv
```

## split.py のテスト

### 1. 基本的なSQL分割テスト

```bash
# test_split.sql を分割
python split.py test/input/test_split.sql test/output/

# 生成されたファイル確認
ls -la test/output/test_split/

# 分割結果確認
cat test/output/test_split/test_split_01.sql    # DDL
cat test/output/test_split/test_split_02.sql    # DDL
cat test/output/test_split/test_split_03.sql    # DDL
cat test/output/test_split/test_split_04.sql    # 一時テーブル
cat test/output/test_split/test_split_05.sql    # CTE
cat test/output/test_split/test_split_main.sql  # メインクエリ
```

### 2. サブクエリ抽出テスト（シンプル）

```bash
# test_simple_subquery.sql を分割
python split.py test/input/test_simple_subquery.sql test/output/

# 生成されたファイル確認
ls -la test/output/test_simple_subquery/

# サブクエリ抽出結果確認
cat test/output/test_simple_subquery/test_simple_subquery_03.sql  # 抽出されたサブクエリ（VIEW）
cat test/output/test_simple_subquery/test_simple_subquery_main.sql # メインクエリ（サブクエリ参照に変更）
```

### 3. 複雑なサブクエリ抽出テスト

```bash
# test_split_subquery.sql を分割
python split.py test/input/test_split_subquery.sql test/output/

# 生成されたファイル確認
ls -la test/output/test_split_subquery/

# 複雑なサブクエリの抽出結果確認
cat test/output/test_split_subquery/test_split_subquery_04.sql  # monthly_sales VIEW
cat test/output/test_split_subquery/test_split_subquery_05.sql  # regional_avg VIEW
cat test/output/test_split_subquery/test_split_subquery_main.sql # メインクエリ
```

### 4. 全ファイル連結テスト

分割されたファイルを連結して元のSQLと同等の動作をするか確認

```bash
# test_split.sql の分割結果を連結
cd test/output/test_split
cat test_split_*.sql test_split_main.sql > combined.sql
cd ../../..

# test_simple_subquery.sql の分割結果を連結
cd test/output/test_simple_subquery  
cat test_simple_subquery_*.sql test_simple_subquery_main.sql > combined.sql
cd ../../..

# test_split_subquery.sql の分割結果を連結
cd test/output/test_split_subquery
cat test_split_subquery_*.sql test_split_subquery_main.sql > combined.sql
cd ../../..
```

## Docker環境でのテスト

```bash
# Dockerイメージをビルド
make build

# Docker環境でanalyze_delete.pyをテスト
docker run --rm -v $(pwd):/app python_data_lineage_docker python analyze_delete.py test/input/test_delete_truncate.sql --output test/output/

# Docker環境でsplit.pyをテスト
docker run --rm -v $(pwd):/app python_data_lineage_docker python split.py test/input/test_split.sql test/output/
```

## テスト結果の確認

```bash
# 生成されたすべてのファイル一覧
find test/output/ -name "*.sql" -o -name "*.csv" | sort

# ディスク使用量確認
du -sh test/output/*
```