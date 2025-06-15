# GitHub Activities Tracker 使用ガイド

## 概要
GitHub Activities Trackerは、GitHubユーザーのアクティビティを追跡して表示するツールです。以下のような情報を取得できます：
- コミット数
- プルリクエスト数
- 作成した課題（Issue）の数
- コードレビュー数
- その他のGitHubアクティビティ指標

## インストール方法

1. リポジトリをクローンします：
   ```
   git clone https://github.com/yourusername/github-activities.git
   cd github-activities
   ```

2. 仮想環境を作成し、依存パッケージをインストールします：
   ```
   # 1) プロジェクト直下で作成（フォルダ名は .venv が慣例）
   python3 -m venv .venv

   # 2) 有効化（シェルを抜けるまで有効）
   source .venv/bin/activate   # fish は `source .venv/bin/activate.fish`

   # 3) pip の更新とライブラリインストール
   python -m pip install --upgrade pip
   pip install -r requirements.txt

   # 4) 使い終わったら
   deactivate
   ```

3. パッケージをインストールします：
   ```
   pip install -e .
   ```

## 設定方法

アプリケーションを使用するには、GitHubのパーソナルアクセストークンが必要です。以下の2つの方法で設定できます：

### 方法1：セットアップコマンドを使用する

```
github-activities setup
```

このコマンドを実行すると、GitHubのAPIトークンの入力を求められます。入力すると、`config/config.json`ファイルが自動的に作成されます。

### 方法2：設定ファイルを手動で作成する

1. `config/config_template.json`を`config/config.json`にコピーします。
2. `config/config.json`を編集し、`YOUR_GITHUB_PERSONAL_ACCESS_TOKEN`を実際のGitHubトークンに置き換えます。

## 使用方法

### アクティビティの概要を表示する

特定のGitHubユーザーのアクティビティ概要を表示するには：

```
github-activities summary <ユーザー名>
```

オプション：
- `--token`, `-t`: GitHubのAPIトークン（設定ファイルがある場合は不要）
- `--config`, `-c`: 設定ファイルのパス（デフォルトは`config/config.json`）
- `--days`, `-d`: アクティビティを取得する日数（デフォルトは365日）
- `--repository`, `-r`: 特定のリポジトリからのみデータを取得（例：`owner/repo`）。指定しない場合はすべてのリポジトリが対象
- `--aggregation`, `-a`: データを週単位または月単位で集計（`week`または`month`）

例：
```
github-activities summary octocat --days 30
```

特定のリポジトリからのみデータを取得する例：
```
github-activities summary octocat --repository octocat/Hello-World
```

週単位でデータを集計する例：
```
github-activities summary octocat --aggregation week
```

月単位でデータを集計する例：
```
github-activities summary octocat --aggregation month
```

### アクティビティデータをエクスポートする

GitHubアクティビティデータをJSONファイルまたはHTMLレポートとしてエクスポートするには：

```
github-activities export <ユーザー名>
```

オプション：
- `--token`, `-t`: GitHubのAPIトークン
- `--config`, `-c`: 設定ファイルのパス
- `--days`, `-d`: アクティビティを取得する日数
- `--output`, `-o`: 出力ファイルのパス（指定しない場合はJSONでは`<ユーザー名>_github_activity_<日付時刻>.json`、HTMLでは`reports/<ユーザー名>_github_activity_<集計単位>_<日付時刻>.html`）
- `--repository`, `-r`: 特定のリポジトリからのみデータを取得（例：`owner/repo`）。指定しない場合はすべてのリポジトリが対象
- `--aggregation`, `-a`: データを週単位または月単位で集計（`week`または`month`）。HTML出力の場合、指定がなければデフォルトで`week`が使用されます
- `--format`, `-f`: 出力形式（`json`または`html`、デフォルトは`json`）

例：
```
github-activities export octocat --output octocat_activity.json
```

特定のリポジトリからのみデータをエクスポートする例：
```
github-activities export octocat --repository octocat/Hello-World --output octocat_hello_world.json
```

週単位でデータを集計してエクスポートする例：
```
github-activities export octocat --aggregation week --output octocat_weekly.json
```

月単位でデータを集計してエクスポートする例：
```
github-activities export octocat --aggregation month --output octocat_monthly.json
```

HTMLレポートとして可視化してエクスポートする例：
```
github-activities export octocat --format html --output octocat_report.html
```

週単位で集計したデータをHTMLレポートとして可視化してエクスポートする例：
```
github-activities export octocat --format html --aggregation week --output octocat_weekly_report.html
```

## トラブルシューティング

1. **認証エラー**: GitHubのAPIトークンが正しいことを確認してください。
2. **レート制限**: GitHubのAPIにはレート制限があります。制限に達した場合は、しばらく待ってから再試行してください。
3. **依存関係エラー**: すべての依存パッケージが正しくインストールされていることを確認してください。

## 注意事項

- GitHubのAPIトークンは秘密情報です。公開リポジトリにコミットしないでください。
- 大量のデータを取得する場合は、GitHubのAPIレート制限に注意してください。
