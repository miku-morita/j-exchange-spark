# 公開とアップデート

このプロジェクトはまだ外部データベースに接続していません。
現時点でCloudに公開する場合は、架空データだけのデモとして利用してください。
本運用では、メンバー・シフト・活動予定・共有メモを永続的な外部データベースへ移してから公開します。
Community Cloudのローカルファイルには永続性の保証がありません。

## 公開先とコードの対応

Streamlit Community CloudとGitHubを連携して公開します。
GitHubのリポジトリ、公開対象のブランチ（例：main）、起動ファイル（app.py）を記録してください。
PC上のファイルを保存しただけでは公開先は更新されません。
必ず、公開先が参照しているリポジトリ・ブランチへ変更をpushします。

公開先URL：未設定
GitHubリポジトリ：未設定
公開対象ブランチ：main（予定）
起動ファイル：app.py
Python：3.11（手元の検証環境に合わせる）
データベース：未設定

## GitHubへ含めるファイル

- app.py
- requirements.txt
- .streamlit/config.toml
- japan_holidays.csv（内閣府の公開祝日データ）
- test_calendar.py
- README.md、DEPLOYMENT.md、.gitignore

個人情報のCSV、パスワード、データベースの接続情報は含めません。
.gitignoreに対象ファイルを追加済みですが、すでにGitで追跡されているファイルには効果がありません。
アップロード前に追跡対象を確認してください。過去に秘密情報を公開した場合は、削除だけでなく秘密情報も変更します。
公開先の管理者パスワード・接続情報はCommunity CloudのSecretsに設定します。
この文書には秘密値を記録しません。

## 普段の更新

1. PC上でコードを修正する。
2. `python -m unittest test_calendar.py` を実行し、架空データのテストを確認する。
3. デモ用の公開アプリで動作を確認する。本運用のデータベースと分離する。
4. GitHubの公開対象ブランチへcommit・pushする。
5. 同じ公開URLで更新後の動作を確認する。

Community Cloudはコードの変更を検知し、依存ファイルの変更時にはライブラリも再インストールします。
反映されない補助ファイルの変更などは、管理画面からRebootを実行し、ログを確認してください。
requirements.txtは手元で確認したバージョンを固定しています。ライブラリを更新するときもテストしてからこのファイルを変更します。

## 更新失敗からの復旧

GitHubで問題の変更をrevertし、公開対象ブランチへpushします。
これでコードを以前の状態へ戻せます。データベースの変更はコードのrevertでは戻りません。
データ構造を変更する更新は、事前バックアップと移行手順を用意し、以前のコードとの互換性も確認してください。

## 公開前に残っている作業

- 外部データベースへの移行（CSVの一括上書きをやめ、同時提出に対応する）。
- 名前による回答の識別を固定IDへ変更する。
- パスワード保存を認証向けの方式へ変更する。
- 本運用・デモ環境とバックアップの設定。
- GitHub・Community Cloudの連携、Secrets設定、実際の更新と復旧の確認。

## 公式資料

- [公開・更新の管理](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app)
- [再起動](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/reboot-your-app)
- [Secrets設定](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
- [データ保存・接続](https://docs.streamlit.io/develop/concepts/connections/connecting-to-data)
