# 燕雲十六聲 Discord 兌換碼比對機器人

這是一個給 Discord 社群使用的兌換碼比對的機器人~

主要功能是讓使用者在 Discord 頻道中 `@機器人` 並貼上兌換碼，機器人會自動判斷這些兌換碼是否已經在本月出現過，並把未重複的兌換碼加入本月清單。

---

## 目前功能

* 支援 `@機器人` 後一次貼上多組兌換碼
* 自動抓取 10 碼兌換碼
* 支援英文與數字組合，例如：

  * `ABCDEFGHIJ`
  * `sample0000`
* 不分大小寫，自動轉成大寫儲存
* 自動比對本月是否重複
* 未重複兌換碼會自動加入本月列表
* 每個月自動重新計算，不需要手動清空
* 回覆下方自動附上兩個按鈕：

  * 本月兌換碼
  * 上個月兌換碼
* 支援 Slash Command：

  * `/本月兌換碼`
  * `/上月兌換碼`
* 使用 SQLite 儲存資料，機器人重開後資料不會消失
* 支援 Discord 伺服器自訂 emoji

---

## 使用畫面範例

使用者輸入：

```text
@你的機器人 abcdefghij
sample0000
zzzzzzzzzz
```

機器人回覆：

```text
未重複如下：
ABCDEFGHIJ
SAMPLE0000
ZZZZZZZZZZ

🔁 重複的共：0 個
✅ 未重複的共：3 個，已新增到本月列表裡

可使用下方按鈕查看本月或上個月兌換碼。
```

如果再次輸入：

```text
@你的機器人 abcdefghij
sample0000
newcode001
```

機器人會回覆：

```text
未重複如下：
NEWCODE001

🔁 重複的共：2 個
✅ 未重複的共：1 個，已新增到本月列表裡
```

---

## 專案結構

建議資料夾結構如下：

```text
yanyun-code-bot/
│
├── main.py
├── .env
├── yanyun_codes.db
└── README.md
```

其中：

```text
main.py             主程式
.env                機器人 Token 與設定檔
requirements.txt    Python 套件清單
yanyun_codes.db     SQLite 資料庫，第一次執行後自動建立
README.md           使用說明
```

---

## 環境需求

建議使用：

```text
Python 3.10 以上
discord.py
python-dotenv
```

Windows、Linux、macOS 。

---

## 安裝方式

### 1. 下載專案

可以直接下載本專案，或使用 Git：

```bash
git clone 你的專案網址
cd yanyun-code-bot
```

---

### 2. 建立 Python 虛擬環境

#### Windows CMD

```bash
python -m venv venv
venv\Scripts\activate
```

#### Windows Anaconda

```bash
conda create -n discord python=3.10 -y
conda activate discord
```

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. 安裝套件

如果你有 `requirements.txt`：

```bash
pip install -r requirements.txt
```

或直接安裝：

```bash
pip install -U discord.py python-dotenv
```

---

## 建立 Discord Bot

### 1. 建立 Application

1. 打開 Discord Developer Portal
2. 建立一個新的 Application
3. 左側選單選擇 Bot
4. 建立 Bot
5. 複製 Bot Token

Token 之後會放到 `.env` 裡。

P.S：Token 等同密碼 不要輕易公開RR。

---

### 2. 開啟 Message Content Intent

因為本機器人需要讀取使用者在 Discord 頻道中貼上的兌換碼，所以必須開啟 Message Content Intent。

路徑：

```text
Discord Developer Portal
→ 你的 Application
→ Bot
→ Privileged Gateway Intents
→ Message Content Intent
→ 開啟
→ Save Changes
```

目前只需要開啟：

```text
Message Content Intent
```
---

## 邀請機器人到伺服器

到 Discord Developer Portal 裡的 OAuth2 URL Generator。

### Scopes 勾選

請勾選：

```text
bot
```

### Bot Permissions 建議勾選

```text
View Channels
Send Messages
Read Message History
Use Slash Commands
Use External Emojis
Add Reactions
```

如果你只使用同伺服器內的自訂 emoji，通常不一定需要 `Use External Emojis`。
但建議先勾選，避免按鈕或訊息中的 emoji 顯示異常~

產生邀請連結後，使用該連結把機器人邀請進伺服器。

---

## .env 設定

請在 `main.py` 同一層建立 `.env` 檔案。

範例：

```env
DISCORD_TOKEN=你的BOT_TOKEN
TEST_CHANNEL_ID=你的測試頻道ID

DUP_EMOJI=🔁
NEW_EMOJI=✅

THIS_MONTH_BUTTON_EMOJI=📅
LAST_MONTH_BUTTON_EMOJI=🗓️
```

---

## 設定說明

### DISCORD_TOKEN

你的 Discord Bot Token。

```env
DISCORD_TOKEN=你的BOT_TOKEN
```

請勿公開。

---

### TEST_CHANNEL_ID

指定機器人只在哪個頻道運作。

```env
TEST_CHANNEL_ID=123456789012345678
```

如果你只想先在測試頻道使用，請填入測試頻道 ID。

如果你想讓機器人在所有頻道都能使用，可以把這行刪掉，或留空：

```env
TEST_CHANNEL_ID=
```

---

### DUP_EMOJI

重複兌換碼統計前面的 emoji。

```env
DUP_EMOJI=🔁
```

也可以使用伺服器自訂 emoji：

```env
DUP_EMOJI=<:repeat_code:123456789012345678>
```

如果是動態 emoji：

```env
DUP_EMOJI=<a:repeat_code:123456789012345678>
```

---

### NEW_EMOJI

未重複兌換碼統計前面的 emoji。

```env
NEW_EMOJI=✅
```

也可以使用伺服器自訂 emoji：

```env
NEW_EMOJI=<:new_code:987654321098765432>
```

---

### THIS_MONTH_BUTTON_EMOJI

本月兌換碼按鈕上的 emoji。

```env
THIS_MONTH_BUTTON_EMOJI=📅
```

---

### LAST_MONTH_BUTTON_EMOJI

上個月兌換碼按鈕上的 emoji。

```env
LAST_MONTH_BUTTON_EMOJI=🗓️
```

---

## 如何取得 Discord 頻道 ID

1. Discord 使用者設定
2. 進階
3. 開啟開發者模式
4. 回到伺服器
5. 右鍵你的測試頻道
6. 點選「複製頻道 ID」

把複製到的 ID 填入：

```env
TEST_CHANNEL_ID=你的頻道ID
```

---

## 如何取得自訂 emoji ID

在 Discord 頻道輸入你的 emoji，例如：

```text
:new_code:
```

在前面加上反斜線：

```text
\:new_code:
```

送出後 Discord 會顯示類似：

```text
<:new_code:987654321098765432>
```

把整串放進 `.env`：

```env
NEW_EMOJI=<:new_code:987654321098765432>
```

如果是動態 emoji，格式會長這樣：

```text
<a:new_code:987654321098765432>
```

---

## 執行機器人

確認 `.env` 設定完成後，執行：

```bash
python main.py
```

正常啟動時，終端機會看到類似：

```text
logging in using static token
Slash commands synced: 2
Logged in as 你的Bot名稱
```

如果看到 `Logged in as ...`，代表機器人已經成功上線。

---

## 使用方式

### 1. 貼兌換碼

在指定頻道輸入：

```text
@你的機器人 abcdefghij
sample0000
zzzzzzzzzz
```

機器人會自動抓出符合規則的兌換碼並比對。

---

### 2. 查看本月兌換碼

有三種方式。

第一種：點機器人回覆下方的「本月兌換碼」按鈕。

第二種：輸入 Slash Command：

```text
/本月兌換碼
```

第三種：再次貼兌換碼後，從新的回覆下方按鈕查看。

---

### 3. 查看上個月兌換碼

有兩種方式。

第一種：點機器人回覆下方的「上個月兌換碼」按鈕。

第二種：輸入 Slash Command：

```text
/上月兌換碼
```

---

## 每個月會自動清空嗎？

功能上等於每個月自動清空。

實際上資料庫不會刪掉舊資料，而是用月份分開儲存：

```text
2026-06 ABCDEFGHIJ
2026-06 SAMPLE0000
2026-07 ABCDEFGHIJ
```

所以：

```text
6 月貼過 ABCDEFGHIJ
7 月再貼 ABCDEFGHIJ
```

在 7 月會被視為新的兌換碼。

---

## 測試流程

### 1. 測試新增兌換碼

輸入：

```text
@你的機器人 abcdefghij
sample0000
```

預期回覆：

```text
未重複如下：
ABCDEFGHIJ
SAMPLE0000

🔁 重複的共：0 個
✅ 未重複的共：2 個，已新增到本月列表裡
```

---

### 2. 測試重複兌換碼

再次輸入：

```text
@你的機器人 abcdefghij
sample0000
newcode001
```

預期回覆：

```text
未重複如下：
NEWCODE001

🔁 重複的共：2 個
✅ 未重複的共：1 個，已新增到本月列表裡
```

---

### 3. 測試本月按鈕

點擊機器人回覆下方：

```text
本月兌換碼
```

預期會顯示本月所有已收錄兌換碼。

---

### 4. 測試上個月按鈕

點擊機器人回覆下方：

```text
上個月兌換碼
```

如果上個月沒有資料，會顯示：

```text
上個月 YYYY-MM 目前沒有兌換碼。
```

---

## 常見問題

### Q1：機器人上線了，但是 @ 它沒反應

請檢查：

```text
1. 你是否在 TEST_CHANNEL_ID 指定的頻道測試
2. Bot 是否有 View Channels 權限
3. Bot 是否有 Send Messages 權限
4. Bot 是否有 Read Message History 權限
5. Developer Portal 是否已開啟 Message Content Intent
6. 程式是否正在執行
```

---

### Q2：出現 PrivilegedIntentsRequired 錯誤

錯誤類似：

```text
discord.errors.PrivilegedIntentsRequired
```

代表你程式要求 Message Content Intent，但 Discord Developer Portal 沒有開。

請到：

```text
Developer Portal
→ Application
→ Bot
→ Privileged Gateway Intents
→ Message Content Intent
→ 開啟
```

然後重新執行：

```bash
python main.py
```

---

### Q3：Slash Command 看不到

請先確認：

```text
1. 邀請機器人時有勾 applications.commands
2. 機器人有 Use Slash Commands 權限
3. main.py 啟動時有顯示 Slash commands synced
4. Discord 客戶端重新整理或重開
```

有時候 Slash Command 需要等一小段時間才會出現。

---

### Q4：自訂 emoji 沒有顯示

請檢查：

```text
1. .env 裡的 emoji 格式是否完整
2. 是否使用 <:名稱:ID> 或 <a:名稱:ID>
3. Bot 是否在該 emoji 所在的伺服器
4. Bot 是否有 Use External Emojis 權限
```

---

### Q5：為什麼我貼的兌換碼沒有被抓到？

預設只抓：

```text
英文或數字，共 10 碼
```

如果你的兌換碼不是 10 碼，請修改：

```python
CODE_PATTERN = re.compile(r"\b[A-Za-z0-9]{10}\b")
```

---


## License

This repository is licensed under the MIT License.

---


## Version

### v1.0.0

* 支援兌換碼比對
* 支援本月資料庫
* 支援上個月查詢
* 支援 Discord 按鈕
* 支援 Slash Command
* 支援 SQLite 永久保存
* 支援自訂 emoji
