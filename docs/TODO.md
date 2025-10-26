* [ ] 「Force using temporary file to show images on gallery」オプションをデフォルトでONにする。これはgradioが自身の配下外のフォルダを扱えるように、gradioのキャッシュフォルダに画像をキャッシュするオプションだと推測。これがOFFだと、画像を読み込めないエラーが出ることがあるので、デフォルトでONが良さそう。
* [ ] 「Filter Images by Tags」で多数のタグが表示される場合、スクロールバーが長くなり、一覧性が悪化する。paddingなどを修正して対策したい。
* [ ] 「/* Adjust checkbox label padding within CheckboxGroup */
[data-testid="checkbox-group"] > label {
    padding: 0 0 0 0;
}
」css.style labelのpadding調整がうまく行かない。cssbotでの上書きはうまくいく
  * `block_tag_filter.py`
    * add `gr.CheckboxGroup(elem_classes=["my-checkbox-group"])`
* [ ] 「Edit Caption of Selected Image」」→「選択された画像をInterrogate」をアコーディオンで閉じれるようにしたい
