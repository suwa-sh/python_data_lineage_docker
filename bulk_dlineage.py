#!/usr/bin/env python3
import sys
import subprocess
import argparse
from pathlib import Path

def run_dlineage_for_directory(dir_path, dlineage_args, verbose=False):
    """
    指定ディレクトリに対してdlineage.pyを実行
    
    Args:
        dir_path: 処理対象のディレクトリパス
        dlineage_args: dlineage.pyに渡す追加引数のリスト
        verbose: 詳細出力フラグ
    """
    # 基本コマンド: python dlineage.py /d <directory_path>
    cmd = [sys.executable, "dlineage.py", "/d", str(dir_path)]
    
    # 追加の引数を追加
    if dlineage_args:
        cmd.extend(dlineage_args)
    
    if verbose:
        print(f"Processing: {dir_path}")
        print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        if verbose:
            print(f"Success: {dir_path}")
            if result.stdout:
                print(f"Output: {result.stdout}")
        
        return True, None
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Error processing {dir_path}: {e.stderr if e.stderr else str(e)}"
        return False, error_msg

def main():
    parser = argparse.ArgumentParser(
        description="指定ディレクトリ直下のすべてのディレクトリに対してdlineage.pyを実行",
        epilog="""
使用例:
  # Oracle SQLで処理
  %(prog)s /path/to/parent/dir /t oracle
  
  # SQL Serverで処理し、結果をJSONで出力
  %(prog)s /path/to/parent/dir /t mssql /json
  
  # シンプルモードで実行
  %(prog)s /path/to/parent/dir /s
  
  # 複数のオプションを指定
  %(prog)s /path/to/parent/dir /t postgresql /json /s /i
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "target_dir",
        help="処理対象の親ディレクトリ"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="詳細な出力を表示"
    )
    parser.add_argument(
        "--ignore",
        nargs="*",
        default=[],
        help="無視するディレクトリ名（例: --ignore .git __pycache__）"
    )
    parser.add_argument(
        "dlineage_args",
        nargs=argparse.REMAINDER,
        help="dlineage.pyに渡す追加引数（例: /t oracle /json /s）"
    )
    
    args = parser.parse_args()
    
    target_path = Path(args.target_dir)
    
    if not target_path.exists():
        print(f"Error: Directory '{target_path}' does not exist")
        sys.exit(1)
    
    if not target_path.is_dir():
        print(f"Error: '{target_path}' is not a directory")
        sys.exit(1)
    
    # 直下のディレクトリを取得
    subdirs = [d for d in target_path.iterdir() 
               if d.is_dir() and d.name not in args.ignore]
    
    if not subdirs:
        print(f"No subdirectories found in '{target_path}'")
        sys.exit(0)
    
    print(f"Found {len(subdirs)} directories to process")
    if args.dlineage_args:
        print(f"Additional dlineage.py arguments: {' '.join(args.dlineage_args)}")
    print("-" * 50)
    
    success_count = 0
    error_count = 0
    errors = []
    
    for i, subdir in enumerate(subdirs, 1):
        print(f"[{i}/{len(subdirs)}] Processing: {subdir.name}")
        
        success, error_msg = run_dlineage_for_directory(subdir, args.dlineage_args, args.verbose)
        
        if success:
            success_count += 1
            print(f"  ✓ Success")
        else:
            error_count += 1
            errors.append((subdir.name, error_msg))
            print(f"  ✗ Failed: {error_msg}")
        
        print()
    
    # サマリー表示
    print("=" * 50)
    print("Summary:")
    print(f"  Total: {len(subdirs)}")
    print(f"  Success: {success_count}")
    print(f"  Failed: {error_count}")
    
    if errors:
        print("\nFailed directories:")
        for dir_name, error_msg in errors:
            print(f"  - {dir_name}: {error_msg}")
    
    sys.exit(0 if error_count == 0 else 1)

if __name__ == "__main__":
    main()