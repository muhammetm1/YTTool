import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import sys
import re
import os
import json
import requests
from PIL import Image, ImageTk
from io import BytesIO
from tkinterdnd2 import DND_FILES, TkinterDnD

class AllInOneApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        # --- DİL VERİLERİ ---
        self.languages = {
            'tr': {
                "app_title": "Medya Merkezi", "downloader_tab": "Video İndirici", "converter_tab": "Video Dönüştürücü",
                "url_label": "Video URL'si:", "paste_button": "Yapıştır", "title_placeholder": "Video başlığı burada görünecek...",
                "quality_label": "Kalite ve Format Seçin:", "path_label": "Kaydetme Konumu:", "change_button": "Değiştir",
                "download_video_button": "VİDEO İNDİR", "download_audio_button": "SADECE SES İNDİR (MP3)",
                "initial_status": "Lütfen bir video linki yapıştırın.", "fetching_info": "Video bilgileri alınıyor...",
                "info_error": "Video bilgileri alınamadı. URL'yi kontrol edin.", "thumb_error": "Küçük resim indirilemedi.",
                "format_error": "Uygun video formatı bulunamadı.", "ready_to_download": "Video indirilmeye hazır.",
                "download_start": "İndirme başlıyor...", "download_success": "İndirme başarıyla tamamlandı!",
                "download_error_generic": "HATA:", "ask_convert": "Bu videoyu dönüştürme listesine eklemek ister misiniz?",
                "select_files_button": "Dosya(lar) Seç", "clear_list_button": "Listeyi Temizle",
                "convert_button": "DÖNÜŞTÜRMEYİ BAŞLAT", "converter_initial_status": "Dönüştürmek için dosya seçin, sürükleyip bırakın...",
                "no_files_warning_title": "Dosya Yok", "no_files_warning_msg": "Lütfen önce en az bir dosya seçin.",
                "conversion_loop_status": "Dosya {i}/{total} dönüştürülüyor: {filename}",
                "conversion_complete": "Tüm dönüştürme işlemleri tamamlandı!",
                "conversion_error_title": "Dönüştürme Hatası", "conversion_error_msg": "{filename} dönüştürülürken bir hata oluştu.",
                "ffprobe_error": "FFprobe bulunamadı veya video süresi okunamadı.",
                "success_title": "Başarılı", "error_title": "Hata", "paste_error": "Panoda metin bulunamadı."
            },
            'en': {
                "app_title": "Media Center", "downloader_tab": "Video Downloader", "converter_tab": "Video Converter",
                "url_label": "Video URL:", "paste_button": "Paste", "title_placeholder": "Video title will appear here...",
                "quality_label": "Select Quality and Format:", "path_label": "Save Location:", "change_button": "Change",
                "download_video_button": "DOWNLOAD VIDEO", "download_audio_button": "DOWNLOAD AUDIO ONLY (MP3)",
                "initial_status": "Please paste a video link.", "fetching_info": "Fetching video information...",
                "info_error": "Could not fetch video info. Check the URL.", "thumb_error": "Could not download thumbnail.",
                "format_error": "No suitable video formats found.", "ready_to_download": "Ready to download.",
                "download_start": "Download starting...", "download_success": "Download completed successfully!",
                "download_error_generic": "ERROR:", "ask_convert": "Add this video to the conversion list?",
                "select_files_button": "Select File(s)", "clear_list_button": "Clear List",
                "convert_button": "START CONVERSION", "converter_initial_status": "Select files to convert, drag and drop, or add from downloader.",
                "no_files_warning_title": "No Files", "no_files_warning_msg": "Please select at least one file first.",
                "conversion_loop_status": "Converting file {i}/{total}: {filename}",
                "conversion_complete": "All conversions are complete!",
                "conversion_error_title": "Conversion Error", "conversion_error_msg": "An error occurred while converting {filename}.",
                "ffprobe_error": "FFprobe not found or video duration could not be read.",
                "success_title": "Success", "error_title": "Error", "paste_error": "No text found on clipboard."
            },
            'ru': {
                "app_title": "Медиацентр", "downloader_tab": "Загрузчик видео", "converter_tab": "Конвертер видео",
                "url_label": "URL видео:", "paste_button": "Вставить", "title_placeholder": "Название видео появится здесь...",
                "quality_label": "Выберите качество и формат:", "path_label": "Место сохранения:", "change_button": "Изменить",
                "download_video_button": "СКАЧАТЬ ВИДЕО", "download_audio_button": "СКАЧАТЬ ТОЛЬКО АУДИО (MP3)",
                "initial_status": "Пожалуйста, вставьте ссылку на видео.", "fetching_info": "Получение информации о видео...",
                "info_error": "Не удалось получить информацию. Проверьте URL.", "thumb_error": "Не удалось загрузить миниатюру.",
                "format_error": "Подходящие форматы видео не найдены.", "ready_to_download": "Готово к загрузке.",
                "download_start": "Загрузка начинается...", "download_success": "Загрузка успешно завершена!",
                "download_error_generic": "ОШИБКА:", "ask_convert": "Добавить это видео в список для конвертации?",
                "select_files_button": "Выбрать файл(ы)", "clear_list_button": "Очистить список",
                "convert_button": "НАЧАТЬ КОНВЕРТАЦИЮ", "converter_initial_status": "Выберите файлы для конвертации, перетащите их или добавьте из загрузчика.",
                "no_files_warning_title": "Нет файлов", "no_files_warning_msg": "Пожалуйста, сначала выберите хотя бы один файл.",
                "conversion_loop_status": "Конвертация файла {i}/{total}: {filename}",
                "conversion_complete": "Все операции конвертации завершены!",
                "conversion_error_title": "Ошибка конвертации", "conversion_error_msg": "Произошла ошибка при конвертации {filename}.",
                "ffprobe_error": "FFprobe не найден или не удалось прочитать длительность видео.",
                "success_title": "Успех", "error_title": "Ошибка", "paste_error": "В буфере обмена текст не найден."
            }
        }
        self.current_lang = tk.StringVar(value='tr')
        self.current_lang.trace("w", self.update_ui_language)

        # --- PENCERE AYARLARI ---
        self.geometry("850x800")
        self.minsize(700, 600)
        self.configure(bg="#2b2b2b")

        logo_path = self.resource_path("logo.ico")
        if os.path.exists(logo_path): self.iconbitmap(logo_path)

        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure_styles()

        self.downloader_vars = {"url": tk.StringVar(), "title": tk.StringVar(), "path": tk.StringVar(value=os.path.expanduser("~\\Downloads")), "info": None, "formats": []}
        self.converter_vars = {"file_list": [], "is_converting": False}
        
        self.startupinfo = None
        if sys.platform == "win32":
            self.startupinfo = subprocess.STARTUPINFO()
            self.startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.startupinfo.wShowWindow = subprocess.SW_HIDE

        self.create_widgets()
        self.update_ui_language()

    def resource_path(self, relative_path):
        try: base_path = sys._MEIPASS
        except Exception: base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def configure_styles(self):
        self.style.configure('TFrame', background='#2b2b2b')
        self.style.configure('TNotebook', background='#2b2b2b', borderwidth=0)
        self.style.configure('TNotebook.Tab', background='#3c3c3c', foreground='white', padding=[10, 5], font=('Calibri', 11, 'bold'))
        self.style.map('TNotebook.Tab', background=[('selected', '#0078d4')], foreground=[('selected', 'white')])
        self.style.configure('TLabel', background='#2b2b2b', foreground='#f0f0f0', font=('Calibri', 11))
        self.style.configure('Title.TLabel', font=('Calibri', 14, 'bold'), wraplength=760)
        self.style.configure('Path.TLabel', font=('Calibri', 9), foreground='#cccccc')
        self.style.configure('TButton', font=('Calibri', 10, 'bold'), borderwidth=0)
        self.style.map('TButton', foreground=[('active', 'white')], background=[('active', '#4a4a4a')])
        self.style.configure('Download.TButton', foreground='white', background='#0078d4', font=('Calibri', 12, 'bold'))
        self.style.map('Download.TButton', background=[('active', '#005a9e'), ('disabled', '#444444')])
        self.style.configure('Audio.TButton', foreground='white', background='#107C10', font=('Calibri', 12, 'bold'))
        self.style.map('Audio.TButton', background=[('active', '#0E6B0E'), ('disabled', '#444444')])
        self.style.configure('Convert.TButton', foreground='white', background='#107C10', font=('Calibri', 12, 'bold'))
        self.style.map('Convert.TButton', background=[('active', '#0E6B0E'), ('disabled', '#444444')])
        self.style.configure('TEntry', fieldbackground='#3c3c3c', foreground='white', borderwidth=1, insertcolor='white')
        self.style.configure('TCombobox', fieldbackground='#3c3c3c', foreground='white', background='#3c3c3c', arrowcolor='white', bordercolor='#555')
        self.style.map('TCombobox', fieldbackground=[('readonly', '#3c3c3c')], foreground=[('readonly', 'white')])
        self.style.configure('Horizontal.TProgressbar', background='#0078d4', troughcolor='#3c3c3c')
        self.style.configure('Converter.Horizontal.TProgressbar', background='#107C10')

    def create_widgets(self):
        # --- DİL MENÜSÜ ---
        menubar = tk.Menu(self)
        language_menu = tk.Menu(menubar, tearoff=0)
        language_menu.add_radiobutton(label="Türkçe", value='tr', variable=self.current_lang)
        language_menu.add_radiobutton(label="English", value='en', variable=self.current_lang)
        language_menu.add_radiobutton(label="Русский", value='ru', variable=self.current_lang)
        menubar.add_cascade(label="Dil / Language / Язык", menu=language_menu)
        self.config(menu=menubar)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=5, pady=5)
        self.downloader_frame = ttk.Frame(self.notebook, padding="15")
        self.converter_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.downloader_frame, text="...")
        self.notebook.add(self.converter_frame, text="...")
        self.create_downloader_tab()
        self.create_converter_tab()
    
    def update_ui_language(self, *args):
        lang = self.current_lang.get()
        i18n = self.languages[lang]
        
        self.title(i18n["app_title"])
        self.notebook.tab(0, text=i18n["downloader_tab"])
        self.notebook.tab(1, text=i18n["converter_tab"])
        
        # Downloader Tab
        self.d_url_label.config(text=i18n["url_label"])
        self.d_paste_button.config(text=i18n["paste_button"])
        self.downloader_vars["title"].set(i18n["title_placeholder"])
        self.d_quality_label.config(text=i18n["quality_label"])
        self.d_path_label.config(text=i18n["path_label"])
        self.d_change_button.config(text=i18n["change_button"])
        self.d_download_button.config(text=i18n["download_video_button"])
        self.d_audio_button.config(text=i18n["download_audio_button"])
        self.d_status_label.config(text=i18n["initial_status"])
        
        # Converter Tab
        self.c_select_button.config(text=i18n["select_files_button"])
        self.c_clear_button.config(text=i18n["clear_list_button"])
        self.c_convert_button.config(text=i18n["convert_button"])
        self.c_status_label.config(text=i18n["converter_initial_status"])

    def create_downloader_tab(self):
        frame = self.downloader_frame
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
        url_frame = ttk.Frame(frame)
        url_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        url_frame.columnconfigure(0, weight=1)
        self.d_url_label = ttk.Label(url_frame, text="...")
        self.d_url_label.pack(side="left", padx=(0, 5))
        self.d_url_entry = ttk.Entry(url_frame, textvariable=self.downloader_vars["url"], font=('Calibri', 11))
        self.d_url_entry.pack(side="left", fill="x", expand=True, ipady=5)
        self.d_url_entry.bind("<FocusOut>", self.start_fetch_info_thread)
        self.d_url_entry.bind("<<Paste>>", lambda e: self.after(100, self.start_fetch_info_thread))
        self.d_paste_button = ttk.Button(url_frame, text="...", command=self.paste_from_clipboard, width=8)
        self.d_paste_button.pack(side="left", padx=(5, 0))
        self.d_title_label = ttk.Label(frame, textvariable=self.downloader_vars["title"], style='Title.TLabel', anchor='center')
        self.d_title_label.grid(row=1, column=0, sticky="ew", pady=(5, 10))
        self.d_thumbnail_label = ttk.Label(frame, background="#1e1e1e", anchor='center')
        self.d_thumbnail_label.grid(row=2, column=0, sticky="nsew")
        options_frame = ttk.Frame(frame)
        options_frame.grid(row=3, column=0, sticky="ew", pady=(15, 5))
        options_frame.columnconfigure(0, weight=1)
        options_frame.columnconfigure(1, weight=1)
        self.d_quality_label = ttk.Label(options_frame, text="...")
        self.d_quality_label.grid(row=0, column=0, sticky="w")
        self.d_quality_combobox = ttk.Combobox(options_frame, state='disabled', font=('Calibri', 11))
        self.d_quality_combobox.grid(row=1, column=0, sticky="ew", ipady=4, padx=(0, 10))
        self.d_path_label = ttk.Label(options_frame, text="...")
        self.d_path_label.grid(row=0, column=1, sticky="w")
        path_frame = ttk.Frame(options_frame)
        path_frame.grid(row=1, column=1, sticky="ew")
        path_frame.columnconfigure(0, weight=1)
        ttk.Label(path_frame, textvariable=self.downloader_vars["path"], style="Path.TLabel", anchor="w", wraplength=300).grid(row=0, column=0, sticky="ew")
        self.d_change_button = ttk.Button(path_frame, text="...", command=self.select_download_path)
        self.d_change_button.grid(row=0, column=1, padx=(5,0))
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, sticky="ew", pady=(15, 10))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        self.d_download_button = ttk.Button(button_frame, text="...", style='Download.TButton', command=lambda: self.start_download_thread('video'), state=tk.DISABLED)
        self.d_download_button.grid(row=0, column=0, sticky="ew", ipady=10, padx=(0, 5))
        self.d_audio_button = ttk.Button(button_frame, text="...", style='Audio.TButton', command=lambda: self.start_download_thread('audio'), state=tk.DISABLED)
        self.d_audio_button.grid(row=0, column=1, sticky="ew", ipady=10, padx=(5, 0))
        self.d_progress_bar = ttk.Progressbar(frame, mode='determinate')
        self.d_progress_bar.grid(row=5, column=0, sticky="ew", pady=(5, 5), ipady=2)
        self.d_status_label = ttk.Label(frame, text="...", anchor='center')
        self.d_status_label.grid(row=6, column=0, sticky="ew")

    def create_converter_tab(self):
        frame = self.converter_frame
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        top_frame = ttk.Frame(frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)
        self.c_select_button = ttk.Button(top_frame, text="...", command=self.c_select_files)
        self.c_select_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.c_clear_button = ttk.Button(top_frame, text="...", command=self.c_clear_list)
        self.c_clear_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        self.c_listbox = tk.Listbox(frame, bg="#3c3c3c", fg="white", font=('Calibri', 10), selectbackground="#0078d4", relief="flat", borderwidth=0)
        self.c_listbox.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        self.c_listbox.drop_target_register(DND_FILES)
        self.c_listbox.dnd_bind('<<Drop>>', self.c_handle_drop)
        self.c_convert_button = ttk.Button(frame, text="...", style="Convert.TButton", command=self.c_start_conversion_thread, state=tk.DISABLED)
        self.c_convert_button.grid(row=2, column=0, columnspan=2, sticky="ew", ipady=10, pady=(5, 10))
        self.c_progress_bar = ttk.Progressbar(frame, mode='determinate', style='Converter.Horizontal.TProgressbar')
        self.c_progress_bar.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        self.c_status_label = ttk.Label(frame, text="...", anchor="center")
        self.c_status_label.grid(row=4, column=0, columnspan=2, sticky="ew")

    def select_download_path(self):
        path = filedialog.askdirectory(initialdir=self.downloader_vars["path"].get(), title="Kaydedilecek Klasörü Seçin")
        if path: self.downloader_vars["path"].set(path)

    def paste_from_clipboard(self):
        try:
            self.downloader_vars["url"].set(self.clipboard_get())
            self.start_fetch_info_thread()
        except tk.TclError:
            self.d_status_label.config(text=self.languages[self.current_lang.get()]["paste_error"])

    def start_fetch_info_thread(self, event=None):
        url = self.downloader_vars["url"].get().strip()
        if not url: return
        self.reset_ui_for_new_url()
        threading.Thread(target=self.fetch_video_info, args=(url,), daemon=True).start()

    def fetch_video_info(self, url):
        try:
            command = ['yt-dlp', '--dump-json', '--skip-download', url]
            process = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8', startupinfo=self.startupinfo)
            self.downloader_vars["info"] = json.loads(process.stdout)
            self.after(0, self.update_ui_with_video_info)
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            self.after(0, self.update_ui_on_error, self.languages[self.current_lang.get()]["info_error"])

    def update_ui_with_video_info(self):
        info = self.downloader_vars["info"]
        if not info: return
        self.downloader_vars["title"].set(info.get('title', '...'))
        self.parse_and_set_formats()
        thumbnail_url = info.get('thumbnail')
        if thumbnail_url:
            threading.Thread(target=self.load_thumbnail, args=(thumbnail_url,), daemon=True).start()
        else:
            self.update_ui_on_error(self.languages[self.current_lang.get()]["thumb_error"])

    def parse_and_set_formats(self):
        self.downloader_vars["formats"] = []
        unique_formats = {}
        formats = self.downloader_vars["info"].get('formats', [])
        for f in formats:
            if f.get('vcodec') != 'none' and f.get('height') is not None:
                height, vcodec = f.get('height'), f.get('vcodec', 'unknown').split('.')[0]
                if 'avc' in vcodec: vcodec = 'h264'
                elif 'vp9' in vcodec: vcodec = 'vp9'
                elif 'av01' in vcodec: vcodec = 'av1'
                display_name, format_string = f"{height}p ({vcodec})", f.get('format_id')
                if f.get('acodec') == 'none': format_string += "+bestaudio"
                quality = f.get('quality', f.get('tbr', 0))
                if display_name not in unique_formats or quality > unique_formats[display_name][2]:
                    unique_formats[display_name] = (display_name, format_string, quality, height)
        sorted_formats = sorted(list(unique_formats.values()), key=lambda x: x[3], reverse=True)
        self.downloader_vars["formats"] = [(item[0], item[1]) for item in sorted_formats]
        if self.downloader_vars["formats"]:
            self.d_quality_combobox['values'] = [item[0] for item in self.downloader_vars["formats"]]
            h264_index = next((i for i, (name, _) in enumerate(self.downloader_vars["formats"]) if 'h264' in name), -1)
            self.d_quality_combobox.current(h264_index if h264_index != -1 else 0)
            self.d_quality_combobox.config(state='readonly')
        else:
            self.update_ui_on_error(self.languages[self.current_lang.get()]["format_error"])

    def load_thumbnail(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            image_data = BytesIO(response.content)
            img = Image.open(image_data)
            self.after(0, self.update_thumbnail_image, img)
        except requests.RequestException:
            self.after(0, self.update_ui_on_error, self.languages[self.current_lang.get()]["thumb_error"])

    def update_thumbnail_image(self, img):
        w, h = self.d_thumbnail_label.winfo_width(), self.d_thumbnail_label.winfo_height()
        img.thumbnail((w - 20, h - 20), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        self.d_thumbnail_label.config(image=photo)
        self.d_thumbnail_label.image = photo
        self.d_status_label.config(text=self.languages[self.current_lang.get()]["ready_to_download"])
        self.d_progress_bar.config(mode='determinate', value=0)
        self.d_download_button.config(state=tk.NORMAL)
        self.d_audio_button.config(state=tk.NORMAL)

    def start_download_thread(self, download_type):
        self.set_downloader_ui_for_download(True)
        url = self.downloader_vars["url"].get().strip()
        if download_type == 'video':
            selected_format_display = self.d_quality_combobox.get()
            format_code = next((code for name, code in self.downloader_vars["formats"] if name == selected_format_display), None)
            if not format_code:
                self.update_downloader_ui_on_complete("HATA: Geçerli format seçilemedi.", False, None)
                return
            command = ['yt-dlp', '-f', format_code, '--merge-output-format', 'mp4', '--progress', '-o', f"{self.downloader_vars['path'].get()}/%(title)s.%(ext)s", url]
        elif download_type == 'audio':
            command = ['yt-dlp', '-x', '--audio-format', 'mp3', '--audio-quality', '0', '--progress', '-o', f"{self.downloader_vars['path'].get()}/%(title)s.%(ext)s", url]
        threading.Thread(target=self.run_download_process, args=(command,), daemon=True).start()

    def run_download_process(self, command):
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', startupinfo=self.startupinfo)
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None: break
                if output: self.parse_downloader_progress(output.strip())
            stderr = process.communicate()[1]
            if process.returncode != 0: raise subprocess.CalledProcessError(process.returncode, command, stderr=stderr)
            info = self.downloader_vars["info"]
            title = info.get('title')
            ext = 'mp4' if '--merge-output-format' in command else 'mp3'
            sane_title = re.sub(r'[\\/*?:"<>|]', "", title)
            output_path = os.path.join(self.downloader_vars['path'].get(), f"{sane_title}.{ext}")
            self.after(0, self.update_downloader_ui_on_complete, self.languages[self.current_lang.get()]["download_success"], True, output_path)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            error_details = e.stderr.strip().split('\n')[-1] if hasattr(e, 'stderr') else str(e)
            self.after(0, self.update_downloader_ui_on_complete, f"{self.languages[self.current_lang.get()]['download_error_generic']} {error_details}", False, None)

    def parse_downloader_progress(self, line):
        progress_match = re.search(r'\[download\]\s+([0-9.]+)%', line)
        if progress_match:
            percent = float(progress_match.group(1))
            self.after(0, lambda: self.d_progress_bar.config(value=percent))
            self.after(0, lambda: self.d_status_label.config(text=line))

    def set_downloader_ui_for_download(self, is_downloading):
        state = tk.DISABLED if is_downloading else tk.NORMAL
        self.d_download_button.config(state=state)
        self.d_audio_button.config(state=state)
        self.d_url_entry.config(state=state)
        self.d_quality_combobox.config(state='disabled' if is_downloading else 'readonly')
        if is_downloading:
            self.d_status_label.config(text=self.languages[self.current_lang.get()]["download_start"])
            self.d_progress_bar.config(mode='determinate', value=0)

    def update_downloader_ui_on_complete(self, message, success, output_path):
        self.set_downloader_ui_for_download(False)
        self.d_status_label.config(text=message)
        self.d_progress_bar['value'] = 100 if success else 0
        lang = self.current_lang.get()
        if success:
            if messagebox.askyesno(self.languages[lang]["success_title"], f"{self.languages[lang]['download_success']}\n\n{self.languages[lang]['ask_convert']}"):
                self.add_files_to_converter_list([output_path])
                self.notebook.select(self.converter_frame)
        else:
            messagebox.showerror(self.languages[lang]["error_title"], message)

    def reset_ui_for_new_url(self):
        self.set_downloader_ui_for_download(True)
        self.d_status_label.config(text=self.languages[self.current_lang.get()]["fetching_info"])
        self.d_progress_bar.config(mode='indeterminate')
        self.d_progress_bar.start(10)
        self.d_quality_combobox.set('')
        self.downloader_vars["title"].set("...")
        self.d_thumbnail_label.config(image='')
        self.d_thumbnail_label.image = None

    def update_ui_on_error(self, message):
        self.d_progress_bar.stop()
        self.d_progress_bar.config(mode='determinate')
        self.d_status_label.config(text=message)
        self.set_downloader_ui_for_download(False)
        self.d_download_button.config(state=tk.DISABLED)
        self.d_audio_button.config(state=tk.DISABLED)

    def c_handle_drop(self, event):
        files = self.tk.splitlist(event.data)
        self.add_files_to_converter_list(files)

    def c_select_files(self):
        files = filedialog.askopenfilenames(title="Dönüştürülecek Videoları Seçin")
        if files: self.add_files_to_converter_list(files)

    def add_files_to_converter_list(self, files):
        for file_path in files:
            if file_path not in self.converter_vars["file_list"]:
                self.converter_vars["file_list"].append(file_path)
                self.c_listbox.insert(tk.END, os.path.basename(file_path))
        self.c_update_button_state()

    def c_clear_list(self):
        self.converter_vars["file_list"].clear()
        self.c_listbox.delete(0, tk.END)
        self.c_update_button_state()

    def c_update_button_state(self):
        if self.converter_vars["file_list"] and not self.converter_vars["is_converting"]:
            self.c_convert_button.config(state=tk.NORMAL)
        else:
            self.c_convert_button.config(state=tk.DISABLED)

    def c_start_conversion_thread(self):
        lang = self.current_lang.get()
        if not self.converter_vars["file_list"]:
            messagebox.showwarning(self.languages[lang]["no_files_warning_title"], self.languages[lang]["no_files_warning_msg"])
            return
        self.converter_vars["is_converting"] = True
        self.c_update_button_state()
        threading.Thread(target=self.c_run_conversion_loop, daemon=True).start()

    def c_run_conversion_loop(self):
        lang = self.current_lang.get()
        total_files = len(self.converter_vars["file_list"])
        for i, file_path in enumerate(self.converter_vars["file_list"]):
            self.c_listbox.selection_clear(0, tk.END)
            self.c_listbox.selection_set(i)
            self.c_listbox.itemconfig(i, {'bg':'#0078d4'})
            filename = os.path.basename(file_path)
            status_text = self.languages[lang]["conversion_loop_status"].format(i=i+1, total=total_files, filename=filename)
            self.after(0, lambda s=status_text: self.c_status_label.config(text=s))
            self.c_convert_file(file_path)
            self.c_listbox.itemconfig(i, {'bg':'#3c3c3c', 'fg':'#55ff55'})
        self.after(0, lambda: self.c_status_label.config(text=self.languages[lang]["conversion_complete"]))
        self.converter_vars["is_converting"] = False
        self.after(0, self.c_update_button_state)

    def c_convert_file(self, input_path):
        path, original_filename = os.path.split(input_path)
        filename, _ = os.path.splitext(original_filename)
        output_path = os.path.join(path, f"{filename}_h264.mp4")
        command = ['ffmpeg', '-y', '-i', input_path, '-c:v', 'libx264', '-preset', 'fast', '-crf', '22', '-c:a', 'aac', '-b:a', '192k', output_path]
        try:
            duration = self.c_get_video_duration(input_path)
            if duration is None: raise ValueError("Video süresi alınamadı.")
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', startupinfo=self.startupinfo)
            for line in iter(process.stdout.readline, ''):
                if "time=" in line: self.c_parse_ffmpeg_progress(line, duration)
            process.wait()
            if process.returncode != 0: raise subprocess.CalledProcessError(process.returncode, command)
        except Exception as e:
            lang = self.current_lang.get()
            msg = self.languages[lang]["conversion_error_msg"].format(filename=original_filename)
            self.after(0, lambda: messagebox.showerror(self.languages[lang]["conversion_error_title"], msg))

    def c_get_video_duration(self, file_path):
        command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, startupinfo=self.startupinfo)
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError):
            messagebox.showerror("FFprobe Error", self.languages[self.current_lang.get()]["ffprobe_error"])
            return None

    def c_parse_ffmpeg_progress(self, line, total_duration):
        match = re.search(r"time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})", line)
        if match:
            h, m, s, ms = map(int, match.groups())
            current_seconds = h * 3600 + m * 60 + s + ms / 100
            progress = (current_seconds / total_duration) * 100
            self.after(0, lambda p=progress: self.c_progress_bar.config(value=min(100, p)))

if __name__ == "__main__":
    app = AllInOneApp()
    app.mainloop()
