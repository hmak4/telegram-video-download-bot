# 🎥 টেলিগ্রাম ভিডিও ডাউনলোড বট

একটি শক্তিশালী টেলিগ্রাম বট যা ফেসবুক, টিকটক, ইউটিউব, ইনস্টাগ্রাম, টুইটার সহ ১০০০+ সাইট থেকে ভিডিও ডাউনলোড করে পাঠায়।

## 🚀 ফিচারসমূহ
- ফেসবুক রিল/ভিডিও, টিকটক, ইউটিউব, ইনস্টাগ্রাম রিলস/পোস্ট, টুইটার ভিডিও ডাউনলোড।
- স্বয়ংক্রিয়ভাবে MP4 ফরম্যাটে কনভার্ট করে।
- 50MB এর বেশি ফাইল টেলিগ্রামের সীমার কারণে পাঠায় না (ব্যবহারকারীকে জানায়)।
- ডাউনলোড করা ফাইল অটো-ডিলিট হয়।
- SSL সার্টিফিকেট ইস্যু হ্যান্ডেল করা আছে।
- টিকটকের জন্য কুকিজ সাপোর্ট (নির্দেশনা নিচে দেওয়া আছে)।

## 🔧 সেটআপ নির্দেশিকা

### ১. টেলিগ্রাম বট তৈরি করুন
- [@BotFather](https://t.me/botfather) - এ গিয়ে `/newbot` কমান্ড দিন।
- বটের নাম ও ইউজারনেম দিন। শেষে একটি টোকেন পাবেন, সেটি সংরক্ষণ করুন।

### ২. লোকাল মেশিন বা ভিপিএস-এ কোড চালানো
```bash
# ১. রিপোজিটরি ক্লোন করুন
git clone https://github.com/yourusername/telegram-video-download-bot.git
cd telegram-video-download-bot

# ২. পাইথন ও পিপ ইনস্টল করুন (উবুন্টু/ডেবিয়ান)
sudo apt update && sudo apt install python3 python3-pip ffmpeg -y

# ৩. প্যাকেজ ইনস্টল করুন
pip3 install -r requirements.txt

# ৪. bot.py ফাইল এডিট করে BOT_TOKEN বসান (অথবা পরিবেশ চলকে দিন)
nano bot.py   # টোকেন পরিবর্তন করুন

# ৫. বট চালান
python3 bot.py
```

### ৩. টারমাক্সে চালাতে চাইলে
```bash
pkg update && pkg upgrade -y
pkg install python ffmpeg git -y
pip install yt-dlp python-telegram-bot curl_cffi
git clone https://github.com/yourusername/telegram-video-download-bot.git
cd telegram-video-download-bot
# টোকেন সেট করুন
nano bot.py
python bot.py
```

### ৪. টিকটক ভিডিও ডাউনলোডের জন্য কুকিজ ফাইল তৈরি
টিকটক বর্তমানে কুকিজ ছাড়া ডাউনলোড দেয় না। নিচের পদ্ধতিতে কুকিজ বের করুন:

1. আপনার কম্পিউটারে ক্রোম ব্রাউজার খুলুন।
2. **Get cookies.txt LOCALLY** এক্সটেনশন ইনস্টল করুন।
3. **ছদ্মবেশী মোডে (Incognito)** [tiktok.com](https://tiktok.com) এ যান এবং লগইন করুন।
4. এক্সটেনশন আইকনে ক্লিক করে **"Export All Cookies"** বাটনে ক্লিক করুন। ফাইলটি `tiktok_cookies.txt` নামে সেভ করুন।
5. এই ফাইলটি বটের ফোল্ডারে (যেখানে `bot.py` আছে) রাখুন।

> 📌 মনে রাখবেন: কুকিজ কিছুদিন পর মেয়াদ শেষ হয়। তখন আবার নতুন করে এক্সপোর্ট করে ফাইলটি প্রতিস্থাপন করুন।

## ☁️ গিটহাবে রিপোজিটরি তৈরি করা

1. [GitHub](https://github.com) এ লগইন করুন।
2. ডানপাশে সবুজ **New** বাটনে ক্লিক করে নতুন রিপোজিটরি তৈরি করুন (যেমন: `telegram-video-download-bot`)।
3. লোকাল ফোল্ডারে নিচের কমান্ডগুলো দিন:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/telegram-video-download-bot.git
   git branch -M main
   git push -u origin main
   ```
4. এখন আপনার রিপোজিটরি GitHub-এ প্রকাশিত।

## 🛠️ কন্ট্রিবিউট
বাগ ফিক্স বা নতুন ফিচার যোগ করতে পুল রিকোয়েস্ট দিন।

## ⚠️ সীমাবদ্ধতা
- টেলিগ্রামের 50MB ফাইল সীমা।
- টিকটকের জন্য কুকিজ ফাইল রিনিউ করতে হয়।
- কিছু প্রাইভেট/গ্রুপ ভিডিও ডাউনলোড করতে ফেসবুকের জন্যও কুকিজ লাগতে পারে (সেক্ষেত্রে একই নিয়ম প্রযোজ্য)।

## লাইসেন্স
MIT
