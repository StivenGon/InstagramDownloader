# Automated Instagram photo downloader using Selenium

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import requests
import tkinter as tk
from threading import Thread

USERNAME = "USERNAME_HERE"  # Change to the target username
SAVE_DIR = USERNAME
os.makedirs(SAVE_DIR, exist_ok=True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(f"https://www.instagram.com/{USERNAME}/")
time.sleep(5)  # Wait for page to load

# --- PAUSE FOR USER TO MOVE WINDOW ---
def wait_for_button():
	root = tk.Tk()
	root.title("Instagram Downloader")
	label = tk.Label(root, text="Move the Chrome window, then click Proceed to start downloading.")
	label.pack(padx=20, pady=10)
	proceed = tk.BooleanVar(value=False)
	def on_click():
		proceed.set(True)
		root.destroy()
	btn = tk.Button(root, text="Proceed", command=on_click)
	btn.pack(pady=10)
	root.mainloop()
	return proceed.get()

wait_for_button()

# Scroll to load all posts
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	time.sleep(3)
	new_height = driver.execute_script("return document.body.scrollHeight")
	if new_height == last_height:
		break
	last_height = new_height

# Find all post links
post_links = set()
for a in driver.find_elements(By.TAG_NAME, "a"):
	href = a.get_attribute("href")
	if href and f"/p/" in href:
		post_links.add(href)

print(f"Found {len(post_links)} posts.")

img_count = 0
for link in post_links:
	driver.get(link)
	time.sleep(2)


	# Try to click through carousels (multiple images per post)
	downloaded_srcs = set()
	while True:
		# Print debug info about current URL
		print(f"Processing post: {driver.current_url}")
		# Try to find all images in the post (Instagram may change class names, so use a more generic selector)
		imgs = driver.find_elements(By.XPATH, '//article//img')
		print(f"Found {len(imgs)} images in this post.")
		for img in imgs:
			src = img.get_attribute("src")
			alt = img.get_attribute("alt")
			print(f"Image src: {src}, alt: {alt}")
			if src and src not in downloaded_srcs:
				img_count += 1
				img_path = os.path.join(SAVE_DIR, f"{img_count}.jpg")
				try:
					r = requests.get(src)
					with open(img_path, "wb") as f:
						f.write(r.content)
					print(f"Downloaded {img_path}")
					downloaded_srcs.add(src)
				except Exception as e:
					print(f"Failed to download {src}: {e}")
		# Try to click the next arrow for carousels
		try:
			next_btn = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Next")] | //button[contains(@class, "coreSpriteRightChevron")]')
			next_btn.click()
			time.sleep(1)
		except Exception as e:
			print(f"No more carousel images or error: {e}")
			break

driver.quit()
print("Done downloading all images.")
