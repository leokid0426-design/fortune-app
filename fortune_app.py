import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from dotenv import load_dotenv
from anthropic import Anthropic
from datetime import datetime
import threading
import json
from pathlib import Path

load_dotenv()

client = Anthropic(
    base_url=os.getenv("ANTHROPIC_BASE_URL"),
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

def ask_ai(prompt):
    res = client.messages.create(
        model="claude-haiku",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return res.content[0].text

class FortuneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ 나의 운세 & 별자리")
        self.root.geometry("700x900")
        self.root.configure(bg="#0f0f23")

        self.history_file = Path("fortune_history.json")
        self.history = self.load_history()

        self.zodiac_list = [
            "양자리 (3/21 ~ 4/19)",
            "황소자리 (4/20 ~ 5/20)",
            "쌍둥이자리 (5/21 ~ 6/20)",
            "게자리 (6/21 ~ 7/22)",
            "사자리 (7/23 ~ 8/22)",
            "처녀자리 (8/23 ~ 9/22)",
            "천칭자리 (9/23 ~ 10/22)",
            "전갈자리 (10/23 ~ 11/21)",
            "사수자리 (11/22 ~ 12/21)",
            "염소자리 (12/22 ~ 1/19)",
            "물병자리 (1/20 ~ 2/18)",
            "물고기자리 (2/19 ~ 3/20)"
        ]

        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TLabel', background='#0f0f23', foreground='#ffffff', font=('Segoe UI', 10))
        style.configure('TFrame', background='#0f0f23')
        style.configure('TLabelFrame', background='#0f0f23', foreground='#64b5f6', font=('Segoe UI', 11, 'bold'))
        style.configure('TEntry', fieldbackground='#1a1a3e', foreground='#ffffff', borderwidth=2)
        style.configure('TCombobox', fieldbackground='#1a1a3e', foreground='#ffffff', borderwidth=2)
        style.configure('TButton', font=('Segoe UI', 11, 'bold'), foreground='#ffffff')
        style.map('TButton', background=[('active', '#42a5f5')])

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.create_header(main_frame)
        self.create_form(main_frame)
        self.create_buttons(main_frame)
        self.create_result(main_frame)
        self.create_footer(main_frame)

    def create_header(self, parent):
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(header_frame, text="✨ 나의 운세 & 별자리", font=('Segoe UI', 28, 'bold'))
        title_label.pack()

        subtitle_label = ttk.Label(header_frame, text="🌟 오늘의 운세를 만나보세요! 🌟", font=('Segoe UI', 12))
        subtitle_label.pack(pady=(5, 0))

    def create_form(self, parent):
        form_frame = ttk.LabelFrame(parent, text="📋 정보 입력", padding=15)
        form_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(form_frame, text="👤 이름:", font=('Segoe UI', 11, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=12)
        self.name_entry = ttk.Entry(form_frame, width=45, font=('Segoe UI', 11))
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, pady=12, padx=(10, 0))
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="📅 생년월일:", font=('Segoe UI', 11, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=12)
        self.birth_entry = ttk.Entry(form_frame, width=45, font=('Segoe UI', 11))
        self.birth_entry.insert(0, "예: 1990-01-15")
        self.birth_entry.grid(row=1, column=1, sticky=tk.EW, pady=12, padx=(10, 0))

        ttk.Label(form_frame, text="♈ 별자리:", font=('Segoe UI', 11, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=12)
        self.zodiac_var = tk.StringVar()
        self.zodiac_combo = ttk.Combobox(form_frame, textvariable=self.zodiac_var,
                                         values=self.zodiac_list, width=42, font=('Segoe UI', 11), state="readonly")
        self.zodiac_combo.grid(row=2, column=1, sticky=tk.EW, pady=12, padx=(10, 0))

    def create_buttons(self, parent):
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 15))

        self.get_fortune_btn = ttk.Button(button_frame, text="🔮 운세보기", command=self.get_fortune)
        self.get_fortune_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.copy_btn = ttk.Button(button_frame, text="📋 복사", command=self.copy_fortune, state=tk.DISABLED)
        self.copy_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.history_btn = ttk.Button(button_frame, text="📚 최근 운세", command=self.show_history)
        self.history_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def create_result(self, parent):
        result_frame = ttk.LabelFrame(parent, text="🌙 오늘의 운세", padding=15)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        self.result_text = scrolledtext.ScrolledText(result_frame, height=12, font=('Segoe UI', 11),
                                                      wrap=tk.WORD, state=tk.DISABLED,
                                                      bg='#1a1a3e', fg='#ffffff', insertbackground='#64b5f6')
        self.result_text.pack(fill=tk.BOTH, expand=True)

        self.extra_info_text = scrolledtext.ScrolledText(result_frame, height=4, font=('Segoe UI', 10),
                                                          wrap=tk.WORD, state=tk.DISABLED,
                                                          bg='#2d2d5f', fg='#64b5f6', insertbackground='#64b5f6')
        self.extra_info_text.pack(fill=tk.BOTH, expand=False, pady=(10, 0))

    def create_footer(self, parent):
        footer_frame = ttk.Frame(parent)
        footer_frame.pack(fill=tk.X, pady=(10, 0))

        footer_label = ttk.Label(footer_frame, text="💫 AI가 생성한 재미있는 운세입니다. 즐거운 하루 되세요! 💫",
                                 font=('Segoe UI', 9), foreground='#64b5f6')
        footer_label.pack()

    def get_fortune(self):
        name = self.name_entry.get().strip()
        birth_date = self.birth_entry.get().strip()
        zodiac = self.zodiac_var.get().strip()

        if not all([name, birth_date, zodiac]):
            messagebox.showwarning("⚠️ 입력 오류", "모든 항목을 입력해주세요!")
            return

        if birth_date == "예: 1990-01-15":
            messagebox.showwarning("⚠️ 입력 오류", "생년월일을 정확히 입력해주세요!")
            return

        self.get_fortune_btn.config(state=tk.DISABLED)
        self.copy_btn.config(state=tk.DISABLED)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "⏳ 운세를 불러오는 중...")
        self.result_text.config(state=tk.DISABLED)

        self.extra_info_text.config(state=tk.NORMAL)
        self.extra_info_text.delete(1.0, tk.END)
        self.extra_info_text.config(state=tk.DISABLED)

        thread = threading.Thread(target=self.fetch_fortune, args=(name, birth_date, zodiac))
        thread.daemon = True
        thread.start()

    def fetch_fortune(self, name, birth_date, zodiac):
        try:
            zodiac_name = zodiac.split(" (")[0]

            prompt = f"""사용자 정보:
- 이름: {name}
- 생년월일: {birth_date}
- 별자리: {zodiac_name}

오늘 날짜: {datetime.now().strftime('%Y년 %m월 %d일')}

위 정보를 바탕으로 {name}님을 위한 오늘의 운세를 4~5줄로 작성해주세요.
운세는 밝고 친근한 말투로, 사용자가 재미있게 읽을 수 있도록 작성해주세요.
재미있는 이모지도 적절히 섞어서 사용해도 좋습니다."""

            fortune = ask_ai(prompt)

            extra_prompt = f"{name}님의 별자리({zodiac_name})을 기반으로 오늘의 럭키 칼러(1개), 럭키 숫자(1~3개), 한 줄 조언을 다음 형식으로 작성해주세요:\n럭키 칼러: [칼러]\n럭키 숫자: [숫자들]\n오늘의 조언: [한 줄 조언]"

            extra_info = ask_ai(extra_prompt)

            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, fortune)
            self.result_text.config(state=tk.DISABLED)

            self.extra_info_text.config(state=tk.NORMAL)
            self.extra_info_text.delete(1.0, tk.END)
            self.extra_info_text.insert(tk.END, extra_info)
            self.extra_info_text.config(state=tk.DISABLED)

            self.save_to_history(name, zodiac_name, fortune, extra_info)

        except Exception as e:
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"❌ 오류 발생:\n\n{str(e)}\n\nAI 호출에 실패했습니다.\n.env 파일에서 API 키를 확인해주세요.")
            self.result_text.config(state=tk.DISABLED)
        finally:
            self.get_fortune_btn.config(state=tk.NORMAL)
            self.copy_btn.config(state=tk.NORMAL)

    def copy_fortune(self):
        fortune_text = self.result_text.get(1.0, tk.END)
        extra_text = self.extra_info_text.get(1.0, tk.END)

        full_text = f"{fortune_text}\n\n{extra_text}"

        self.root.clipboard_clear()
        self.root.clipboard_append(full_text)
        messagebox.showinfo("✅ 복사 완료", "운세가 클립보드에 복사되었습니다!")

    def save_to_history(self, name, zodiac, fortune, extra_info):
        today = datetime.now().strftime("%Y-%m-%d")

        entry = {
            "date": today,
            "name": name,
            "zodiac": zodiac,
            "fortune": fortune,
            "extra_info": extra_info
        }

        if not self.history:
            self.history = []

        self.history.insert(0, entry)

        if len(self.history) > 50:
            self.history = self.history[:50]

        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def load_history(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def show_history(self):
        if not self.history:
            messagebox.showinfo("📚 최근 운세", "저장된 운세가 없습니다.")
            return

        history_window = tk.Toplevel(self.root)
        history_window.title("📚 최근 운세 기록")
        history_window.geometry("600x500")
        history_window.configure(bg="#0f0f23")

        title_label = ttk.Label(history_window, text="📜 최근 운세 기록", font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(10, 10))

        history_text = scrolledtext.ScrolledText(history_window, height=20, font=('Segoe UI', 10),
                                                 wrap=tk.WORD, bg='#1a1a3e', fg='#ffffff')
        history_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        for entry in self.history[:10]:
            history_text.insert(tk.END, f"\n{'='*50}\n")
            history_text.insert(tk.END, f"📅 {entry['date']}\n")
            history_text.insert(tk.END, f"👤 {entry['name']} ({entry['zodiac']})\n")
            history_text.insert(tk.END, f"\n{entry['fortune']}\n")
            history_text.insert(tk.END, f"\n{entry['extra_info']}\n")

        history_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = FortuneApp(root)
    root.mainloop()
