"""Instagram downloader desktop app."""

import os
import queue
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class InstagramDownloaderApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Instagram Downloader")
		self.root.geometry("720x520")
		self.root.minsize(640, 460)
		self.root.configure(background="#111827")

		self.message_queue = queue.Queue()
		self.is_running = False
		self.last_output_dir = None
		self.username_var = tk.StringVar(value="")
		self.status_var = tk.StringVar(value="Ready")
		self.progress_text_var = tk.StringVar(value="0 / 0 posts")
		self.progress_value_var = tk.IntVar(value=0)

		self._setup_theme()
		self._set_window_icon()
		self._build_ui()
		self.root.after(100, self._process_queue)

	def _setup_theme(self):
		style = ttk.Style()
		style.theme_use("clam")
		style.configure("App.TFrame", background="#111827")
		style.configure("Card.TFrame", background="#18212f")
		style.configure("App.TLabel", background="#111827", foreground="#e5eef9")
		style.configure("Card.TLabel", background="#18212f", foreground="#e5eef9")
		style.configure("Title.TLabel", background="#111827", foreground="#ffffff", font=("Segoe UI", 18, "bold"))
		style.configure("Subtitle.TLabel", background="#111827", foreground="#a7b3c6", font=("Segoe UI", 10))
		style.configure("Status.TLabel", background="#18212f", foreground="#7dd3fc", font=("Segoe UI", 10, "bold"))
		style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=(14, 9))
		style.configure("Secondary.TButton", font=("Segoe UI", 10), padding=(12, 9))
		style.configure("App.Horizontal.TProgressbar", troughcolor="#0f172a", background="#38bdf8", bordercolor="#0f172a", lightcolor="#38bdf8", darkcolor="#38bdf8")

	def _set_window_icon(self):
		icon = tk.PhotoImage(width=32, height=32)
		for x in range(32):
			for y in range(32):
				if x in (0, 31) or y in (0, 31):
					color = "#0f172a"
				elif 6 <= x <= 25 and 6 <= y <= 25:
					color = "#f97316" if x < 16 else "#38bdf8"
				elif 10 <= x <= 21 and 10 <= y <= 21:
					color = "#f8fafc"
				else:
					color = "#111827"
				icon.put(color, (x, y))
		self._window_icon = icon
		self.root.iconphoto(True, icon)

	def _build_ui(self):
		main_frame = ttk.Frame(self.root, padding=16, style="App.TFrame")
		main_frame.pack(fill=tk.BOTH, expand=True)

		header_frame = ttk.Frame(main_frame, style="App.TFrame")
		header_frame.pack(fill=tk.X, pady=(0, 16))

		title_label = ttk.Label(header_frame, text="Instagram Downloader", style="Title.TLabel")
		title_label.pack(anchor="w")

		description = ttk.Label(
			header_frame,
			text="Desktop app for downloading images from public Instagram profiles. Enter a username, start the run, and the app will save the images locally.",
			style="Subtitle.TLabel",
			wraplength=640,
		)
		description.pack(anchor="w", pady=(6, 0))

		card_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=16)
		card_frame.pack(fill=tk.BOTH, expand=True)

		form_frame = ttk.Frame(card_frame, style="Card.TFrame")
		form_frame.pack(fill=tk.X, pady=(0, 12))

		username_label = ttk.Label(form_frame, text="Instagram username", style="Card.TLabel")
		username_label.grid(row=0, column=0, sticky="w")

		self.username_entry = ttk.Entry(form_frame, textvariable=self.username_var)
		self.username_entry.grid(row=1, column=0, sticky="ew", pady=(6, 0))
		self.username_entry.focus_set()

		buttons_frame = ttk.Frame(form_frame, style="Card.TFrame")
		buttons_frame.grid(row=1, column=1, padx=(12, 0), sticky="e")

		self.start_button = ttk.Button(buttons_frame, text="Start download", style="Accent.TButton", command=self.start_download)
		self.start_button.grid(row=0, column=0, sticky="e")

		self.open_folder_button = ttk.Button(buttons_frame, text="Open output folder", style="Secondary.TButton", command=self.open_output_folder)
		self.open_folder_button.grid(row=0, column=1, padx=(10, 0), sticky="e")
		self.open_folder_button.configure(state="disabled")

		form_frame.columnconfigure(0, weight=1)

		progress_frame = ttk.Frame(card_frame, style="Card.TFrame")
		progress_frame.pack(fill=tk.X, pady=(0, 12))

		self.progress_bar = ttk.Progressbar(progress_frame, maximum=1, variable=self.progress_value_var, style="App.Horizontal.TProgressbar")
		self.progress_bar.pack(fill=tk.X)

		progress_label = ttk.Label(progress_frame, textvariable=self.progress_text_var, style="Card.TLabel")
		progress_label.pack(anchor="w", pady=(6, 0))

		status_frame = ttk.Frame(card_frame, style="Card.TFrame")
		status_frame.pack(fill=tk.X, pady=(0, 12))

		status_label = ttk.Label(status_frame, textvariable=self.status_var, style="Status.TLabel")
		status_label.pack(anchor="w")

		log_frame = ttk.LabelFrame(card_frame, text="Log")
		log_frame.pack(fill=tk.BOTH, expand=True)

		self.log_text = tk.Text(log_frame, wrap="word", height=16, state="disabled")
		log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
		self.log_text.configure(yscrollcommand=log_scrollbar.set)

		self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		self._append_log("Ready to download.")

	def _append_log(self, message):
		self.log_text.configure(state="normal")
		self.log_text.insert(tk.END, f"{message}\n")
		self.log_text.see(tk.END)
		self.log_text.configure(state="disabled")

	def _set_status(self, message):
		self.status_var.set(message)

	def _set_progress_max(self, total_posts):
		total_posts = max(total_posts, 1)
		self.progress_bar.configure(maximum=total_posts)
		self.progress_value_var.set(0)
		self.progress_text_var.set(f"0 / {total_posts} posts")

	def _set_progress(self, current_posts, total_posts):
		total_posts = max(total_posts, 1)
		self.progress_value_var.set(current_posts)
		self.progress_text_var.set(f"{current_posts} / {total_posts} posts")

	def _queue_log(self, message):
		self.message_queue.put(("log", message))

	def _queue_status(self, message):
		self.message_queue.put(("status", message))

	def _queue_progress_max(self, total_posts):
		self.message_queue.put(("progress_max", total_posts))

	def _queue_progress(self, current_posts, total_posts):
		self.message_queue.put(("progress", (current_posts, total_posts)))

	def _process_queue(self):
		try:
			while True:
				message_type, payload = self.message_queue.get_nowait()
				if message_type == "log":
					self._append_log(payload)
				elif message_type == "status":
					self._set_status(payload)
				elif message_type == "progress_max":
					self._set_progress_max(payload)
				elif message_type == "progress":
					current_posts, total_posts = payload
					self._set_progress(current_posts, total_posts)
				elif message_type == "done":
					self.is_running = False
					self.start_button.configure(state="normal")
					self.username_entry.configure(state="normal")
					self.open_folder_button.configure(state="normal" if self.last_output_dir else "disabled")
				elif message_type == "error":
					self.is_running = False
					self.start_button.configure(state="normal")
					self.username_entry.configure(state="normal")
					self.open_folder_button.configure(state="normal" if self.last_output_dir else "disabled")
					messagebox.showerror("Download failed", payload)
		except queue.Empty:
			pass
		finally:
			self.root.after(100, self._process_queue)

	def start_download(self):
		if self.is_running:
			return

		username = self.username_var.get().strip().lstrip("@")
		if not username:
			messagebox.showwarning("Missing username", "Enter an Instagram username first.")
			return

		self.is_running = True
		self.start_button.configure(state="disabled")
		self.username_entry.configure(state="disabled")
		self.open_folder_button.configure(state="disabled")
		self.log_text.configure(state="normal")
		self.log_text.delete("1.0", tk.END)
		self.log_text.configure(state="disabled")
		self._queue_status("Starting download...")
		self._queue_progress_max(1)
		threading.Thread(target=self._download_profile, args=(username,), daemon=True).start()

	def open_output_folder(self):
		if self.last_output_dir and os.path.isdir(self.last_output_dir):
			os.startfile(self.last_output_dir)
			return
		messagebox.showinfo("No folder yet", "Run a download first to create the output folder.")

	def _download_profile(self, username):
		save_dir = username
		self.last_output_dir = os.path.abspath(save_dir)
		os.makedirs(save_dir, exist_ok=True)
		driver = None

		try:
			self._queue_log(f"Saving images to: {os.path.abspath(save_dir)}")
			self._queue_log("Starting Chrome... move the window if you want, then wait for the download to continue.")
			driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
			driver.get(f"https://www.instagram.com/{username}/")
			time.sleep(5)

			last_height = driver.execute_script("return document.body.scrollHeight")
			while True:
				driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				time.sleep(3)
				new_height = driver.execute_script("return document.body.scrollHeight")
				if new_height == last_height:
					break
				last_height = new_height

			post_links = set()
			for anchor in driver.find_elements(By.TAG_NAME, "a"):
				href = anchor.get_attribute("href")
				if href and "/p/" in href:
					post_links.add(href)

			total_posts = len(post_links)
			self._queue_log(f"Found {total_posts} posts.")
			self._queue_progress_max(total_posts)

			image_count = 0
			processed_posts = 0
			for link in post_links:
				self._queue_log(f"Processing post: {link}")
				driver.get(link)
				time.sleep(2)

				downloaded_sources = set()
				while True:
					images = driver.find_elements(By.XPATH, "//article//img")
					for image in images:
						source = image.get_attribute("src")
						if source and source not in downloaded_sources:
							image_count += 1
							image_path = os.path.join(save_dir, f"{image_count}.jpg")
							try:
								response = requests.get(source, timeout=30)
								response.raise_for_status()
								with open(image_path, "wb") as file_handle:
									file_handle.write(response.content)
								self._queue_log(f"Downloaded {image_path}")
								downloaded_sources.add(source)
							except Exception as exc:
								self._queue_log(f"Failed to download image: {exc}")

					try:
						next_button = driver.find_element(
							By.XPATH,
							'//button[contains(@aria-label, "Next")] | //button[contains(@class, "coreSpriteRightChevron")]',
						)
						next_button.click()
						time.sleep(1)
					except Exception:
						break

				processed_posts += 1
				self._queue_progress(processed_posts, total_posts)

			self._queue_status("Download complete")
			self._queue_log("Done downloading all images.")
		except Exception as exc:
			self._queue_status("Download failed")
			self.message_queue.put(("error", str(exc)))
		finally:
			if driver is not None:
				driver.quit()
			self.message_queue.put(("done", None))


def main():
	root = tk.Tk()
	InstagramDownloaderApp(root)
	root.mainloop()


if __name__ == "__main__":
	main()
