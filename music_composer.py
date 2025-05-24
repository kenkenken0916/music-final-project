import curses
from music21 import *
import math
import os

# ========== 音樂生成核心 ==========

C_MAJOR = [60, 62, 64, 65, 67, 69, 71, 72]
G_MAJOR = [67, 69, 71, 72, 74, 76, 78, 79]

# 音高修正
def fix_the_note(scale_list, note_val):
    return min(scale_list, key=lambda s: abs(note_val - s))

def transpose_the_melody(note_list, transposition):
    return [n + transposition for n in note_list]

# 主旋律產生
def generate_melody(num_sequence, the_scale, variation=0, transpose=0):
    note_list = []
    duration_list = []
    for d in num_sequence:
        note_pitch = d + 60 + transpose
        note_list.append(fix_the_note(the_scale, note_pitch))
        if d == 0:
            duration = 1  # 將原本的 2 改為 1
        else:
            duration = d * 0.25 if variation == 1 else d * 0.125  # 將 0.5 改為 0.25，0.25 改為 0.125
        duration_list.append(duration)
    if duration_list:
        duration_list[-1] = 2  # 將原本的 4 改為 2，讓最後的音符也相應縮短
    note_list = transpose_the_melody(note_list, 12)
    return note_list, duration_list

def generate_extended_melody(selected_notes, num_measures=4):
    # 從使用者選擇的音符建立音符序列和音階
    user_notes = []
    scale = []
    
    for row in selected_notes:
        for note_name in row:
            if note_name:
                note_obj = note.Note(note_name)
                user_notes.append(note_obj.pitch.midi - 60)  # 轉換為相對音高
                scale.append(note_obj.pitch.midi)
    
    if not scale:
        scale = C_MAJOR  # 如果沒有選擇音符，使用 C 大調
        user_notes = [0, 2, 4, 5, 7]  # 使用簡單的音階

    # 生成主要段落
    notes_A, durs_A = generate_melody(user_notes, scale, variation=0, transpose=0)  # 原始主題
    
    # 生成第一個過渡段 - 使用上行音階
    transition1_notes = user_notes[:3] * 2  # 重複前三個音
    notes_T1, durs_T1 = generate_melody(transition1_notes, scale, variation=1, transpose=2)
    
    # 生成B段 - 升七度的變化
    notes_B, durs_B = generate_melody(user_notes, scale, variation=0, transpose=7)
    
    # 生成第二個過渡段 - 使用下行音階
    transition2_notes = list(reversed(user_notes[-3:]))  # 使用最後三個音的反向
    notes_T2, durs_T2 = generate_melody(transition2_notes, scale, variation=1, transpose=-2)
    
    # 生成C段 - 使用不同的節奏變化和升五度
    notes_C, durs_C = generate_melody(user_notes[::2], scale, variation=1, transpose=5)  # 使用間隔的音符
    
    # 生成最後的A段變奏
    reversed_notes = list(reversed(user_notes))  # 反向主題
    notes_Ap, durs_Ap = generate_melody(reversed_notes, scale, variation=1, transpose=0)

    # 合併所有旋律段落：A-T1-B-T2-C-A'的結構
    full_notes = (notes_A + notes_T1 + notes_B + 
                 notes_T2 + notes_C + notes_Ap)
    full_durations = (durs_A + durs_T1 + durs_B + 
                     durs_T2 + durs_C + durs_Ap)
    
    return full_notes, full_durations

# 和弦庫
chord_library = {
    # 大調和弦
    'C':    ['C3', 'E3', 'G3', 'C4'],
    'G':    ['G2', 'B2', 'D3', 'G3'],
    'D':    ['D3', 'F#3', 'A3', 'D4'],
    'A':    ['A2', 'C#3', 'E3', 'A3'],
    'E':    ['E3', 'G#3', 'B3', 'E4'],
    'F':    ['F2', 'A2', 'C3', 'F3'],
    'Bb':   ['Bb2', 'D3', 'F3', 'Bb3'],
    
    # 小調和弦
    'Cm':   ['C3', 'Eb3', 'G3', 'C4'],
    'Gm':   ['G2', 'Bb2', 'D3', 'G3'],
    'Dm':   ['D3', 'F3', 'A3', 'D4'],
    'Am':   ['A2', 'C3', 'E3', 'A3'],
    'Em':   ['E3', 'G3', 'B3', 'E4'],
    'Fm':   ['F2', 'Ab2', 'C3', 'F3'],
    
    # 增強和弦
    'Caug':  ['C3', 'E3', 'G#3', 'C4'],
    'Gaug':  ['G2', 'B2', 'D#3', 'G3'],
    'Faug':  ['F2', 'A2', 'C#3', 'F3'],
    
    # 減弱和弦
    'Cdim':  ['C3', 'Eb3', 'Gb3', 'B3'],
    'Gdim':  ['G2', 'Bb2', 'Db3', 'F3'],
    'Ddim':  ['D3', 'F3', 'Ab3', 'C4'],
    
    # 七和弦
    'C7':    ['C3', 'E3', 'G3', 'Bb3'],
    'G7':    ['G2', 'B2', 'D3', 'F3'],
    'F7':    ['F2', 'A2', 'C3', 'Eb3'],
    'Dm7':   ['D3', 'F3', 'A3', 'C4'],
    'Am7':   ['A2', 'C3', 'E3', 'G3'],
    
    # 大七和弦
    'Cmaj7': ['C3', 'E3', 'G3', 'B3'],
    'Gmaj7': ['G2', 'B2', 'D3', 'F#3'],
    'Fmaj7': ['F2', 'A2', 'C3', 'E3'],
    
    # sus4和弦
    'Csus4': ['C3', 'F3', 'G3', 'C4'],
    'Gsus4': ['G2', 'C3', 'D3', 'G3'],
    'Fsus4': ['F2', 'Bb2', 'C3', 'F3']
}

note_names = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4']

# 琶音模式定義
def get_arpeggio_patterns():
    return {
        "基本和弦": lambda chord_notes, duration: [
            (chord_notes, 4.0)
        ],
        "上升琶音": lambda chord_notes, duration: [
            (note, duration) for note in chord_notes * 2
        ],
        "下降琶音": lambda chord_notes, duration: [
            (note, duration) for note in list(reversed(chord_notes)) * 2
        ],
        "上下琶音": lambda chord_notes, duration: [
            (note, duration) for note in chord_notes + list(reversed(chord_notes))
        ],
        "阿爾伯蒂低音": lambda chord_notes, duration: [
            (chord_notes[0], duration),
            (chord_notes[2], duration),
            (chord_notes[1], duration),
            (chord_notes[2], duration)
        ]
    }

def generate_accompaniment(chord_notes, pattern_names, total_measures):
    patterns = get_arpeggio_patterns()
    accompaniment_parts = []
    
    instruments = [instrument.Guitar(), instrument.Harp(), 
                  instrument.Piano(), instrument.Harpsichord(), 
                  instrument.AcousticGuitar()]
    
    for idx, pattern_name in enumerate(pattern_names):
        pattern_func = patterns[pattern_name]
          # 為每個伴奏部分創建新的聲部
        chord_part = stream.Part()
        # 為每個聲部使用不同的樂器
        chord_part.insert(0, instruments[idx % len(instruments)])
        
        for _ in range(total_measures):
            note_pattern = pattern_func(chord_notes, 0.5 if pattern_name != "基本和弦" else 4.0)
            for note_name, duration in note_pattern:
                if isinstance(note_name, list):  # 如果是和弦
                    ch = chord.Chord(note_name)
                    ch.quarterLength = duration
                    chord_part.append(ch)
                else:  # 如果是單音
                    n = note.Note(note_name)
                    n.quarterLength = duration
                    chord_part.append(n)
                    
        accompaniment_parts.append(chord_part)
    
    return accompaniment_parts

def build_score(selected_notes, chord_name, pattern_instruments, output_filename):
    # 生成延伸旋律
    full_notes, full_durations = generate_extended_melody(selected_notes)
    
    # 主旋律部分
    melody = stream.Part()
    melody.insert(0, instrument.Piano())
    melody.insert(0, meter.TimeSignature('4/4'))
    
    # 加入原始選擇的音符
    for row in selected_notes:
        for col in row:
            if col:
                nn = note.Note(col)
                nn.quarterLength = 1.0
                melody.append(nn)
    
    # 加入延伸的旋律
    for pitch, duration in zip(full_notes, full_durations):
        nn = note.Note(pitch)
        nn.quarterLength = duration
        melody.append(nn)
    
    melody.makeMeasures(inPlace=True)
    
    # 計算小節數
    total_measures = len(melody.measures(0, None))
    
    # 生成伴奏部分
    accompaniment_parts = []
    for pattern_name, inst in pattern_instruments:
        chord_part = stream.Part()
        chord_part.insert(0, inst)  # 使用選擇的樂器
        
        pattern_func = get_arpeggio_patterns()[pattern_name]
        for _ in range(total_measures):
            note_pattern = pattern_func(chord_library[chord_name], 0.5 if pattern_name != "基本和弦" else 4.0)
            for note_name, duration in note_pattern:
                if isinstance(note_name, list):  # 如果是和弦
                    ch = chord.Chord(note_name)
                    ch.quarterLength = duration
                    chord_part.append(ch)
                else:  # 如果是單音
                    n = note.Note(note_name)
                    n.quarterLength = duration
                    chord_part.append(n)
        
        chord_part.makeMeasures(inPlace=True)
        accompaniment_parts.append(chord_part)
    
    # 合成總譜
    score = stream.Score()
    score.insert(0, melody)
    # 加入所有伴奏聲部
    for i, part in enumerate(accompaniment_parts):
        score.insert(i + 1, part)
    
    # 輸出 MIDI
    output_path = os.path.abspath(output_filename)
    score.write('midi', fp=output_path)
    return output_path

# 根據音符推薦和弦
def suggest_chords(selected_notes):
    # 收集所有不為 None 的音符
    used_notes = set()
    for row in selected_notes:
        for note_name in row:
            if note_name:
                n = note.Note(note_name)
                used_notes.add(n.pitch.name)
    
    # 計算每個和弦與旋律音符的匹配程度
    chord_scores = {}
    for chord_name, chord_notes in chord_library.items():
        score = 0
        chord_note_names = set(note.Note(n).pitch.name for n in chord_notes)
        # 計算和弦音符與旋律音符的重疊數
        matching_notes = len(used_notes.intersection(chord_note_names))
        score += matching_notes * 2
        chord_scores[chord_name] = score
    
    # 根據分數排序和弦
    sorted_chords = sorted(chord_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_chords

def select_chord_screen(stdscr, selected_notes):
    chords = suggest_chords(selected_notes)[:5]  # 只取前五個最適合的和弦
    current_idx = 0
    
    try:
        while True:
            stdscr.clear()
            
            # 顯示標題和操作說明
            stdscr.addstr(1, 5, "選擇伴奏和弦", curses.A_BOLD)
            stdscr.addstr(2, 5, "操作說明：", curses.A_NORMAL)
            stdscr.addstr(3, 5, "上下鍵 = 選擇和弦", curses.A_NORMAL)
            stdscr.addstr(4, 5, "Enter = 確認選擇", curses.A_NORMAL)
            stdscr.addstr(6, 5, "最適合的五個和弦（根據旋律自動分析）：", curses.A_BOLD)
            
            # 顯示前五個最適合的和弦
            for i, (chord_name, score) in enumerate(chords):
                # 使用星號表示推薦程度
                stars = "★" * min(5, score) if score > 0 else "☆"
                text = f"{chord_name:<4} {stars:<5}"  # 固定寬度以避免溢位
                attr = curses.A_REVERSE if i == current_idx else curses.A_NORMAL
                stdscr.addstr(8 + i, 10, text, attr)
            
            stdscr.refresh()
            
            # 處理按鍵輸入
            key = stdscr.getch()
            
            if key == curses.KEY_UP:
                current_idx = (current_idx - 1) % len(chords)
            elif key == curses.KEY_DOWN:
                current_idx = (current_idx + 1) % len(chords)
            elif key == ord('\n') or key == 10:  # Enter鍵
                return chords[current_idx][0]
                
    except curses.error as e:
        # 如果發生終端機大小相關的錯誤，顯示錯誤訊息
        stdscr.clear()
        stdscr.addstr(0, 0, "終端機視窗太小，請調整視窗大小後重試")
        stdscr.refresh()
        stdscr.getch()
        return 'C'  # 返回預設和弦
def select_notes_screen(stdscr):
    cols = 16  # 保持16個音符的長度
    notes = [None] * cols  # 儲存MIDI音符值
    c = 0  # 當前位置
    input_buffer = ""  # 用於暫存輸入的數字或音名
    bulk_input_mode = False  # 是否處於批量輸入模式
    note_name_mode = False  # 是否處於音名輸入模式
    
    def parse_note_name(note_str):
        """將音名轉換為MIDI音高值"""
        try:
            if note_str:
                n = note.Note(note_str)
                return n.pitch.midi
        except:
            return None
        return None
    
    def draw_screen():
        stdscr.clear()
        # 標題和基本操作說明
        stdscr.addstr(1, 5, "輸入旋律音符", curses.A_BOLD)
        stdscr.addstr(2, 5, "基本操作：", curses.A_NORMAL)
        stdscr.addstr(3, 5, "← → = 移動游標", curses.A_NORMAL)
        stdscr.addstr(4, 5, "空格 = 切換輸入模式", curses.A_NORMAL)
        stdscr.addstr(5, 5, "T = 切換批量輸入模式", curses.A_NORMAL)
        stdscr.addstr(6, 5, "Enter = 確認", curses.A_NORMAL)
        stdscr.refresh()  # 刷新第一部分
        
        # 模式說明
        if note_name_mode:
            stdscr.addstr(7, 5, "【音名輸入模式】", curses.A_BOLD)
            stdscr.addstr(8, 5, "輸入範例：C4、D4、E4、F4、G4、A4、B4", curses.A_NORMAL)
            stdscr.addstr(9, 5, "可使用升降記號：C#4、Bb3 等", curses.A_NORMAL)
        else:
            stdscr.addstr(7, 5, "【MIDI值輸入模式】", curses.A_BOLD)
            stdscr.addstr(8, 5, "參考值：60=中央C、67=G4、72=高音C", curses.A_NORMAL)
            stdscr.addstr(9, 5, "範圍：0-127", curses.A_NORMAL)
        stdscr.refresh()  # 刷新模式說明
        
        # 顯示音符網格
        for row in range(2):
            start_idx = row * 8
            end_idx = start_idx + 8
            y_pos = 11 + row * 2
            stdscr.addstr(y_pos, 5, f"第{row+1}行音符:")
            stdscr.refresh()  # 刷新每行開頭
            
            for i in range(start_idx, end_idx):
                if notes[i] is not None:
                    n = note.Note(notes[i])
                    display = f"[{n.nameWithOctave:3}]"
                else:
                    display = "[   ]"
                
                attr = curses.A_REVERSE if i == c and not bulk_input_mode else curses.A_NORMAL
                if i == c and not bulk_input_mode and input_buffer:
                    display = f"[{input_buffer:3}]"
                
                stdscr.addstr(y_pos, 20 + (i - start_idx) * 6, display, attr)
            stdscr.refresh()  # 刷新每行音符
        
        # 顯示當前狀態
        if bulk_input_mode:
            stdscr.addstr(15, 5, "批量輸入模式（用空格分隔多個音符）", curses.A_BOLD)
            stdscr.addstr(16, 5, f"> {input_buffer}")
        elif input_buffer:
            stdscr.addstr(15, 5, f"正在輸入: {input_buffer}", curses.A_BOLD)
        
        stdscr.refresh()  # 最後刷新一次
    
    try:
        while True:
            draw_screen()
            key = stdscr.getch()
            
            if bulk_input_mode:
                if key == ord('\n') or key == 10:  # Enter鍵
                    try:
                        inputs = input_buffer.split()
                        pos = c
                        for val in inputs:
                            if note_name_mode:
                                midi_val = parse_note_name(val)
                            else:
                                midi_val = int(val)
                            if midi_val is not None and 0 <= midi_val <= 127 and pos < cols:
                                notes[pos] = midi_val
                                pos = (pos + 1) % cols
                        bulk_input_mode = False
                        input_buffer = ""
                    except ValueError:
                        pass
                elif key == 27:  # ESC
                    bulk_input_mode = False
                    input_buffer = ""
                elif key == ord('\b') or key == 127:  # Backspace
                    input_buffer = input_buffer[:-1]
                elif 32 <= key <= 126:  # 可列印字符
                    input_buffer += chr(key)
            else:
                if key == ord('t') or key == ord('T'):
                    bulk_input_mode = True
                    input_buffer = ""
                elif key == curses.KEY_LEFT:
                    c = (c - 1) % cols
                    input_buffer = ""
                elif key == curses.KEY_RIGHT:
                    c = (c + 1) % cols
                    input_buffer = ""
                elif key == ord(' '):
                    note_name_mode = not note_name_mode
                    input_buffer = ""
                elif key == ord('\b') or key == 127 or key == curses.KEY_DC:
                    if input_buffer:
                        input_buffer = input_buffer[:-1]
                    else:
                        notes[c] = None
                elif 32 <= key <= 126:
                    if note_name_mode or chr(key).isdigit():
                        input_buffer += chr(key)
                        if not note_name_mode and input_buffer and int(input_buffer) > 127:
                            input_buffer = "127"
                elif key == ord('\n') or key == 10:
                    if input_buffer:
                        if note_name_mode:
                            midi_val = parse_note_name(input_buffer)
                            if midi_val is not None:
                                notes[c] = midi_val
                        else:
                            try:
                                val = int(input_buffer)
                                if 0 <= val <= 127:
                                    notes[c] = val
                            except ValueError:
                                pass
                        input_buffer = ""
                    else:
                        break

    except curses.error:
        stdscr.clear()
        stdscr.addstr(0, 0, "請調整視窗大小後重試")
        stdscr.refresh()
        stdscr.getch()
        return []

    # 轉換結果
    selected = []
    for note_val in notes:
        if note_val is not None:
            n = note.Note(note_val)
            selected.append([n.nameWithOctave])
        else:
            selected.append([None])
    
    return selected

# 樂器列表
AVAILABLE_INSTRUMENTS = {
    "鋼琴": instrument.Piano(),
    "原聲吉他": instrument.AcousticGuitar(),
    "豎琴": instrument.Harp(),
    "大提琴": instrument.Violoncello(),  # Cello 的正確名稱是 Violoncello
    "小提琴": instrument.Violin(),
    "長笛": instrument.Flute(),
    "單簧管": instrument.Clarinet(),
    "雙簧管": instrument.Oboe(),
    "低音提琴": instrument.ElectricBass(),  # 改用電貝斯替代低音管
    "銅管": instrument.Trumpet()
}

def select_pattern_screen(stdscr):
    patterns = list(get_arpeggio_patterns().keys())
    instruments = list(AVAILABLE_INSTRUMENTS.keys())
    current_idx = 0  # 當前選擇的項目索引
    selected_patterns = []  # 儲存已選擇的琶音模式和對應的樂器
    in_instrument_selection = False  # 是否正在選擇樂器
    temp_pattern = None  # 暫存正在配置樂器的琶音模式
    
    def draw_screen():
        stdscr.clear()
        stdscr.addstr(1, 5, "選擇琶音模式和樂器", curses.A_BOLD)
        stdscr.addstr(2, 5, "操作說明：", curses.A_NORMAL)
        stdscr.addstr(3, 5, "空格 = 選擇琶音模式", curses.A_NORMAL)
        stdscr.addstr(4, 5, "Enter = 完成並繼續", curses.A_NORMAL)
        
        # 顯示已選擇的琶音模式和樂器
        y_offset = 6
        for i, (pat, inst) in enumerate(selected_patterns):
            stdscr.addstr(y_offset + i, 10, f"✓ {pat} - 使用{inst}")
        
        y_offset = y_offset + len(selected_patterns) + 2
        
        if in_instrument_selection:
            # 顯示樂器選擇列表
            stdscr.addstr(y_offset - 1, 5, f"為「{temp_pattern}」選擇樂器：", curses.A_BOLD)
            for i, inst in enumerate(instruments):
                attr = curses.A_REVERSE if i == current_idx else curses.A_NORMAL
                stdscr.addstr(y_offset + i, 10, f"[{inst}]", attr)
        else:
            # 顯示琶音模式列表
            for i, pat in enumerate(patterns):
                if not any(p[0] == pat for p in selected_patterns):  # 只顯示未選擇的模式
                    attr = curses.A_REVERSE if i == current_idx else curses.A_NORMAL
                    stdscr.addstr(y_offset + i, 10, f"[ ] {pat}", attr)

        stdscr.refresh()
    
    while True:
        draw_screen()
        key = stdscr.getch()
        
        if in_instrument_selection:
            if key == curses.KEY_UP:
                current_idx = (current_idx - 1) % len(instruments)
            elif key == curses.KEY_DOWN:
                current_idx = (current_idx + 1) % len(instruments)
            elif key == ord('\n') or key == 10:  # 確認選擇樂器
                selected_patterns.append((temp_pattern, instruments[current_idx]))
                in_instrument_selection = False
                temp_pattern = None
                current_idx = 0
            elif key == 27:  # ESC取消選擇
                in_instrument_selection = False
                temp_pattern = None
                current_idx = 0
        else:
            if key == curses.KEY_UP:
                current_idx = (current_idx - 1) % len(patterns)
            elif key == curses.KEY_DOWN:
                current_idx = (current_idx + 1) % len(patterns)
            elif key == ord(' '):
                # 選擇琶音模式後進入樂器選擇
                if not any(p[0] == patterns[current_idx] for p in selected_patterns):
                    temp_pattern = patterns[current_idx]
                    in_instrument_selection = True
                    current_idx = 0
            elif key == ord('\n') or key == 10:
                if not selected_patterns:  # 如果沒有選擇，預設選擇第一個配鋼琴
                    selected_patterns.append((patterns[0], "鋼琴"))
                break
    
    # 返回選擇的琶音模式和對應的樂器
    return [(pat, AVAILABLE_INSTRUMENTS[inst]) for pat, inst in selected_patterns]

# ========== 介面函數 ==========

def start_screen(stdscr):
    stdscr.clear()
    stdscr.addstr(5, 10, "歡迎使用 MIDI 作曲助手", curses.A_BOLD)
    stdscr.addstr(7, 10, "按任意鍵繼續...")
    stdscr.refresh()
    stdscr.getch()

def main(stdscr):
    curses.curs_set(0)  # 隱藏游標
    start_screen(stdscr)
      # 選擇旋律音符
    note_matrix = select_notes_screen(stdscr)
    if not any(any(col) for col in note_matrix):
        stdscr.clear()
        stdscr.addstr(5, 5, "未選擇任何音符，程式結束。")
        stdscr.refresh()
        stdscr.getch()
        return
      # 選擇和弦
    chord_name = select_chord_screen(stdscr, note_matrix)
    
    # 選擇琶音模式和樂器
    pattern_instruments = select_pattern_screen(stdscr)
    path = build_score(note_matrix, chord_name, pattern_instruments, 'output.mid')
    
    # 顯示完成訊息
    stdscr.clear()
    stdscr.addstr(5, 5, f"✅ MIDI已生成: {path}")
    stdscr.addstr(7, 5, "按任意鍵結束。")
    stdscr.refresh()
    stdscr.getch()

if __name__ == '__main__':
    curses.wrapper(main)
