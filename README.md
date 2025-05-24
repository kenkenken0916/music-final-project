# MIDI作曲助手

這是一個互動式的MIDI音樂創作工具，可以幫助使用者輕鬆創作音樂並生成MIDI檔案。

## 功能特點

- 直觀的終端機介面
- 支持音符名稱（如C4、D4）和MIDI數值輸入
- 批量輸入模式，快速輸入多個音符
- 智能和弦推薦系統
- 多種琶音模式
- 支援多種樂器
- 自動生成延伸旋律

## 安裝需求

- Python 3.8+
- music21 函式庫
- Windows/Linux/MacOS 作業系統

## 安裝步驟

1. 克隆此專案：
```bash
git clone https://github.com/yourusername/midi-composer-assistant.git
```

2. 安裝相依套件：
```bash
pip install -r requirements.txt
```

## 使用方法

執行以下指令啟動程式：

```bash
python music_composer.py
```

### 操作說明

1. **音符輸入界面**
   - ← → : 移動游標
   - 空格 : 切換輸入模式（MIDI值/音名）
   - T : 切換批量輸入模式
   - Enter : 確認

2. **和弦選擇界面**
   - ↑ ↓ : 選擇和弦
   - Enter : 確認選擇

3. **琶音模式選擇**
   - 空格 : 選擇琶音模式
   - Enter : 完成並繼續

## 支援的樂器

- 鋼琴
- 原聲吉他
- 豎琴
- 大提琴
- 小提琴
- 長笛
- 單簧管
- 雙簧管
- 低音提琴
- 銅管

## 授權

本專案採用 MIT 授權條款，詳情請參閱 [LICENSE](LICENSE) 文件。
