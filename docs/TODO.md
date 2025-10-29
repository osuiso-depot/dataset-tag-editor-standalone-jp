* [ ] 「Force using temporary file to show images on gallery」オプションをデフォルトでONにする。
  * [ ] はgradioが自身の配下外のフォルダを扱えるように、gradioのキャッシュフォルダに画像をキャッシュするオプションだと推測。OFFだと、画像を読み込めないエラーが出ることがあるので、ユーザーが混乱する。デフォルトでONが良さそう。
* [x] 「Filter Images by Tags」で多数のタグが表示される場合、スクロールバーが長くなり、一覧性が悪化する。paddingなどを修正して対策したい。
* [x] 「/* Adjust checkbox label padding within CheckboxGroup */
[data-testid="checkbox-group"] > label {
    padding: 0 0 0 0;
}
」css.style labelのpadding調整がうまく行かない。cssbotでの上書きはうまくいく
  * `block_tag_filter.py`
    * add `gr.CheckboxGroup(elem_classes=["my-checkbox-group"])`
* [x] 「Edit Caption of Selected Image」」→「選択された画像をInterrogate」をアコーディオンで閉じれるようにしたい
* [ ] 現在の表示タブ(gradio内の表示タブ)を覚える。リロード時も表示タブが変化しない

# メイン
* [ ] 「メイン」タブ内のディレクトリの読み込みなどによって、表示が変化しないチェックボックス／ラジオボタンの状態を保存する。
  * [ ] localstorageなどで保存できないか検討
    * [ ] `「Backup original text file (original file will be renamed like filename」...`
    * [ ] `Use kohya-ss's finetuning metadata json`
    * [ ] `Dataset directory`
    * [ ] `Caption File Ext`
    * [ ] `Dataset Load Settings`
      * [ ] `Load from subdirectories`
      * [ ] `Load caption from filename if no text file exists`
      * [ ] `Replace new-line character with comma`
      * [ ] `Use Interrogator Caption`
    * [ ] `Interrogator Settings`
      * [ ] `Booru Score Threshold`
      * [ ] `Z3D-E621 Score Threshold`
      * [ ] `Use Custom Threshold (WDv1.4 Tagger)`
      * [ ] `WDv1.4 Tagger Score Threshold`
# 設定
* [ ] 「UIを再読み込み」ボタン押下でブラウザの自動リロードを行う
* [ ] 「設定を保存」「デフォルトの設定に戻す」ボタン押下で、操作が行われたことを通知(alertやpopup windowなどで)を表示
    * [ ]  ユーザーの操作を阻害しない形で、伝える実装にする
