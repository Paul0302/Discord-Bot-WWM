import os
import re
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
TEST_CHANNEL_ID = os.getenv("TEST_CHANNEL_ID")

DUP_EMOJI = os.getenv("DUP_EMOJI", "🔁")
NEW_EMOJI = os.getenv("NEW_EMOJI", "✅")

THIS_MONTH_BUTTON_EMOJI = os.getenv("THIS_MONTH_BUTTON_EMOJI", "📅")
LAST_MONTH_BUTTON_EMOJI = os.getenv("LAST_MONTH_BUTTON_EMOJI", "🗓️")

DB_PATH = "yanyun_codes.db"
TZ = ZoneInfo("Asia/Taipei")

CODE_PATTERN = re.compile(r"\b[A-Za-z0-9]{10}\b")


def month_text(offset=0):
    now = datetime.now(TZ)
    year = now.year
    month = now.month + offset

    while month <= 0:
        month += 12
        year -= 1

    while month > 12:
        month -= 12
        year += 1

    return f"{year:04d}-{month:02d}"


def current_month():
    return month_text(0)


def previous_month():
    return month_text(-1)


def now_text():
    return datetime.now(TZ).isoformat(timespec="seconds")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS codes (
            guild_id TEXT NOT NULL,
            month TEXT NOT NULL,
            code TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (guild_id, month, code)
        )
        """
    )

    conn.commit()
    conn.close()


def is_test_channel(channel_id):
    if not TEST_CHANNEL_ID:
        return True

    return str(channel_id) == TEST_CHANNEL_ID


def split_message(text, limit=1900):
    chunks = []
    current = ""

    for line in text.splitlines():
        if len(current) + len(line) + 1 > limit:
            chunks.append(current)
            current = line
        else:
            current += ("\n" if current else "") + line

    if current:
        chunks.append(current)

    return chunks


def add_codes(guild_id, codes):
    month = current_month()
    created_at = now_text()

    new_codes = []
    duplicate_codes = []
    seen_in_this_message = set()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for raw_code in codes:
        code = raw_code.upper()

        if code in seen_in_this_message:
            duplicate_codes.append(code)
            continue

        seen_in_this_message.add(code)

        cur.execute(
            """
            SELECT 1 FROM codes
            WHERE guild_id = ? AND month = ? AND code = ?
            """,
            (str(guild_id), month, code),
        )

        exists = cur.fetchone()

        if exists:
            duplicate_codes.append(code)
        else:
            cur.execute(
                """
                INSERT INTO codes (guild_id, month, code, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (str(guild_id), month, code, created_at),
            )
            new_codes.append(code)

    conn.commit()
    conn.close()

    return new_codes, duplicate_codes


def get_codes_by_month(guild_id, month):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT code FROM codes
        WHERE guild_id = ? AND month = ?
        ORDER BY created_at ASC, code ASC
        """,
        (str(guild_id), month),
    )

    rows = cur.fetchall()
    conn.close()

    return [row[0] for row in rows]


async def send_month_codes(interaction, month, title):
    if interaction.guild is None:
        await interaction.response.send_message(
            "這個功能只能在伺服器使用。",
            ephemeral=True,
        )
        return

    if not is_test_channel(interaction.channel_id):
        await interaction.response.send_message(
            "目前這個功能只開放在測試頻道使用。",
            ephemeral=True,
        )
        return

    codes = get_codes_by_month(interaction.guild.id, month)

    if not codes:
        await interaction.response.send_message(
            f"{title} {month} 目前沒有兌換碼。",
            ephemeral=True,
        )
        return

    text = f"{title} {month} 兌換碼共 {len(codes)} 組：\n\n" + "\n".join(codes)
    chunks = split_message(text)

    await interaction.response.send_message(chunks[0], ephemeral=True)

    for chunk in chunks[1:]:
        await interaction.followup.send(chunk, ephemeral=True)


class MonthCodeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="本月兌換碼",
        style=discord.ButtonStyle.success,
        emoji=THIS_MONTH_BUTTON_EMOJI,
        custom_id="list_this_month_codes_button",
    )
    async def list_this_month_codes(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await send_month_codes(
            interaction,
            current_month(),
            "本月",
        )

    @discord.ui.button(
        label="上個月兌換碼",
        style=discord.ButtonStyle.primary,
        emoji=LAST_MONTH_BUTTON_EMOJI,
        custom_id="list_last_month_codes_button",
    )
    async def list_last_month_codes(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await send_month_codes(
            interaction,
            previous_month(),
            "上個月",
        )


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    init_db()
    bot.add_view(MonthCodeView())

    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {len(synced)}")
    except Exception as e:
        print(f"Slash sync error: {e}")

    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.guild is None:
        return

    if not is_test_channel(message.channel.id):
        return

    if bot.user is None:
        return

    if not bot.user.mentioned_in(message):
        await bot.process_commands(message)
        return

    codes = CODE_PATTERN.findall(message.content)

    if not codes:
        await message.reply(
            "沒有找到兌換碼。請貼上 10 碼兌換碼，例如：ABCDEFGHIJ 或 SAMPLE0000",
            mention_author=False,
            view=MonthCodeView(),
        )
        return

    new_codes, duplicate_codes = add_codes(message.guild.id, codes)

    lines = []
    lines.append("未重複如下：")

    if new_codes:
        lines.extend(new_codes)
    else:
        lines.append("無")

    lines.append("")
    lines.append(f"{DUP_EMOJI} 重複的共：{len(duplicate_codes)} 個")
    lines.append(f"{NEW_EMOJI} 未重複的共：{len(new_codes)} 個，已新增到本月列表裡")
    lines.append("")
    lines.append("可使用下方按鈕查看本月或上個月兌換碼。")

    reply_text = "\n".join(lines)
    chunks = split_message(reply_text)

    first = True

    for chunk in chunks:
        if first:
            await message.reply(
                chunk,
                mention_author=False,
                view=MonthCodeView(),
            )
            first = False
        else:
            await message.channel.send(chunk)

    await bot.process_commands(message)


@bot.tree.command(name="本月兌換碼", description="列出本月已收錄的燕雲十六聲兌換碼")
async def month_codes(interaction: discord.Interaction):
    await send_month_codes(
        interaction,
        current_month(),
        "本月",
    )


@bot.tree.command(name="上月兌換碼", description="列出上個月已收錄的燕雲十六聲兌換碼")
async def last_month_codes(interaction: discord.Interaction):
    await send_month_codes(
        interaction,
        previous_month(),
        "上個月",
    )


if not TOKEN:
    raise RuntimeError("找不到 DISCORD_TOKEN，請確認 .env 是否有設定。")

bot.run(TOKEN)