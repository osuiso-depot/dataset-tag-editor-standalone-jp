# 国際化(i18n)実装の改善履歴

### 問題の背景

当初、Gradio 4系を想定した`gr.I18n`の使用方法でエラーが発生していました。

**発生していたエラー:**
```
AttributeError: 'I18n' object has no attribute 'set_default_locale'
UserWarning: Invalid locale code: 'default_locale'
UserWarning: Invalid locale code: 'locale_dir'
```

### 原因分析

1. **Gradio 5.xでのAPI変更**: `gr.I18n`クラスに`set_default_locale()`メソッドが存在しない
2. **`gr.I18n`の用途の誤解**: Gradioの`I18n`はGradio組み込みUI要素の翻訳用であり、カスタムテキストの動的翻訳には使用できない
3. **`gr.Blocks`の`i18n`引数**: この引数は存在せず、指定するとエラーの原因となる

### 実装した解決策

#### 1. 独自の翻訳システムの実装

Python側で翻訳辞書を直接管理する方式に変更しました。

**`scripts/ui/i18n_helper.py`の主な変更点:**

```python
# グローバルな翻訳辞書を管理
_translations: Dict[str, Dict[str, str]] = {}
_current_locale: str = "en"

def load_translations(lang: str) -> None:
    """指定された言語の翻訳ファイルをロードする"""
    # 全言語の翻訳ファイルをロード（フォールバック用）

def t(key: str, **kwargs) -> str:
    """
    翻訳キーに対応するテキストを取得
    kwargsで渡されたパラメータは文字列内の{param}を置換
    """
    # 現在のロケールから翻訳を取得
    # 見つからない場合は英語（フォールバック）
    # パラメータ置換をサポート
```

**特徴:**
- ✅ 翻訳ファイル（`locales/ja.json`, `locales/en.json`）から直接読み込み
- ✅ 英語へのフォールバック機能
- ✅ パラメータ置換機能（例: `t("label", num=5)` → `"対象: 5件"`）
- ✅ Gradioのバージョンに依存しない実装

#### 2. 設定画面の翻訳データ移行

**移行前（`settings.py`）:**
```python
DESCRIPTIONS = {
    "allowed_paths": "Path whitelist to show images...",
    "use_temp_files": "Force using temporary file...",
    # ...（英語のみハードコード）
}
```

**移行後（`locales/ja.json`, `locales/en.json`）:**
```json
{
  "settings.allowed_paths.label": "許可されたパス",
  "settings.allowed_paths.description": "ギャラリーに画像を表示するための...",
  "settings.use_temp_files.label": "一時ファイルを使用",
  "settings.use_temp_files.description": "ギャラリーに画像を表示する際..."
}
```

**メリット:**
- ✅ 全てのテキストが翻訳ファイルで一元管理
- ✅ ラベルと説明文の両方を翻訳可能
- ✅ 新しい言語の追加が容易
- ✅ デッドコード（未使用の`DESCRIPTIONS`）を削除

#### 3. UIコンポーネントでの使用方法

**`interface.py`:**
```python
def create_ui():
    with gr.Blocks(analytics_enabled=False, title=t("app.title")) as gui:
        with gr.Tab(t("app.main_tab.label")):
            tab_main.on_ui_tabs()
        with gr.Tab(t("app.settings_tab.label")):
            tab_settings.on_ui_tabs()
    return gui
```

**`tab_settings.py`:**
```python
elem = gr.Number(
    value=s,
    label=t(f"settings.{name}.label"),
    info=t(f"settings.{name}.description")  # 説明文も翻訳
)
```

### サポート言語

- **英語 (en)**: デフォルト・フォールバック言語
- **日本語 (ja)**: 完全翻訳対応

### 翻訳ファイルの形式

```json
{
  "key.subkey.label": "表示テキスト",
  "key.subkey.description": "説明テキスト",
  "key.with_param": "値: {value}件"
}
```

**パラメータ置換の使用例:**
```python
t("move_delete.target_dataset_num.label", num=5)
# → "対象データセット数: 5"
```

### 今後の拡張性

新しい言語を追加する場合:
1. `locales/{lang_code}.json`を作成
2. `i18n_helper.py`の`SUPPORTED_LANGS`に言語を追加
3. 設定画面の言語選択に自動的に表示

### 技術的な注意点

- **Gradio 5.34.2で動作確認済み**
- `gr.I18n`や`gr.Blocks(i18n=...)`は使用していない
- Python側で翻訳を完結させるため、Gradioのバージョンアップの影響を受けにくい
- UIリロード時に言語切り替えが正しく反映される
