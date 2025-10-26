# Gradioアップデート／互換パッチ対応計画

## 背景
- 起動時に[`interface.main`](scripts/interface.py:212)から`app.get_blocks().get_api_info()`が呼び出され、Gradio内部でAPI情報のJSON Schemaを生成する過程で例外が発生している。
- 例外の原因は[`gradio_client.utils._json_schema_to_python_type`](venv/lib/site-packages/gradio_client/utils.py:900)が`additionalProperties`に含まれる`bool`を辞書として扱おうとする既知不具合で、`TypeError: argument of type 'bool' is not iterable`が送出される。

## 対処オプション
### オプションA: Gradioアップデートでの恒久対策
1. **修正バージョンのリサーチ**
   - Gradio 4.29以降のリリースノートやIssue/PRを調査し、`additionalProperties`／`TypeError`修正の有無を確認する。
2. **検証用アップデート実施**
   - 事前に`pip freeze > requirements.lock.txt`で現行環境をバックアップ。
   - テスト環境で
     ```
     .\venv\Scripts\pip.exe install "gradio==<修正候補バージョン>"
     ```
     を実行し、`install.bat`→`launch_user.bat`→`http://127.0.0.1:7860`で起動確認。
3. **スモークテスト**
   - デフォルト設定でのデータセットロード、設定保存／リセット（[`tab_settings.btn_restore_clicked`](scripts/tab_settings.py:78)）など主要ユースケースを確認。
4. **展開準備**
   - 問題なければ`requirements.txt`を更新し、運用ドキュメントにアプグレード手順と注意点を追記。

### オプションB: 互換パッチによる暫定対策
1. **パッチ適用ポイント**
   - [`interface.main`](scripts/interface.py:212)実行前に新規モジュール（例: `scripts/compat/gradio_patch.py`）をimportし、起動1回でパッチ適用を完了させる。
2. **パッチ内容**
   - `gradio_client.utils._json_schema_to_python_type`を軽量ラップし、`schema`または`schema["additionalProperties"]`が`bool`の場合に早期リターン（例: `"Dict()"`／`"Dict(str, Any)"`）して既存ロジックへboolを渡さない。
   - 元関数のコピーは避け、最小差分で副作用を抑制する。
3. **動作検証**
   - 起動エラーが解消されることと、設定タブ操作（[`tab_settings.btn_restore_clicked`](scripts/tab_settings.py:78)）などAPI情報生成に関わる操作で問題が出ないことを確認。
4. **メンテナンス注意**
   - Gradio更新で不具合が解消された際はパッチを除去できるよう、バージョン依存のコメントを残す。

## テストおよびロールバック方針
- いずれのオプションでも`launch_user.bat`からの起動→ブラウザアクセス→主要ユースケースのスモークテストを実施して結果を記録する。
- アップデート後に不具合が生じた場合は下記いずれかでロールバックする。
  - `.\venv\Scripts\pip.exe install -r requirements.lock.txt`
  - または `.\venv\Scripts\pip.exe install "gradio==4.28.3"` で既存バージョンへ復元し、必要に応じて`install.bat`で仮想環境を再構築する。

## 次のアクション候補
- 修正バージョンのリサーチ結果を共有し、採用するオプション（AまたはB）を確定する。
- 選択したオプションに沿って実装モードへ切り替え、作業を進める。
- スモークテストの結果とロールバック手順をドキュメント（本ファイルまたはREADME類）に追記して運用へ引き渡す。
