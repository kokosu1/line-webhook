import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# =========================
# 環境変数設定（Render対応）
# =========================
TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID"))
PRODUCTS_FILE = "products.json"

# =========================
# 商品データ管理
# =========================
def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return []
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []


def save_products(products):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=4, ensure_ascii=False)


# =========================
# Bot設定
# =========================
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


# =========================
# チケット閉鎖View
# =========================
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="閉じる",
        style=discord.ButtonStyle.red,
        custom_id="close_ticket_button"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("チケットを閉じます...", ephemeral=True)
        await interaction.channel.delete()


# =========================
# チケット作成View
# =========================
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="チケット作成",
        style=discord.ButtonStyle.green,
        custom_id="create_ticket_button"
    )
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        admin_role = guild.get_role(ADMIN_ROLE_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="サポートチケット",
            description="管理者が対応します。下のボタンで閉じられます。",
            color=discord.Color.green()
        )

        await channel.send(
            content=f"{user.mention} <@&{ADMIN_ROLE_ID}>",
            embed=embed,
            view=CloseTicketView()
        )

        await interaction.response.send_message(
            f"チケットを作成しました: {channel.mention}",
            ephemeral=True
        )


# =========================
# 商品購入View
# =========================
class ShopView(discord.ui.View):
    def __init__(self, products):
        super().__init__(timeout=300)

        for index, product in enumerate(products):
            button = discord.ui.Button(
                label=f"購入: {product['name']} ({product['price']}円)",
                style=discord.ButtonStyle.blurple,
                custom_id=f"buy_{index}"
            )
            button.callback = self.make_callback(index, products)
            self.add_item(button)

    def make_callback(self, index, products):
        async def callback(interaction: discord.Interaction):
            product = products[index]
            await interaction.response.send_message(
                f"**{product['name']}**\n価格: {product['price']}円\n内容: {product['content']}",
                ephemeral=True
            )
        return callback


# =========================
# Slash Commands
# =========================
@tree.command(name="ticketpanel", description="チケット作成パネルを送信")
async def ticketpanel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="サポートチケット",
        description="下のボタンを押してチケットを作成してください。",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, view=TicketView())


@tree.command(name="addproduct", description="商品追加")
@app_commands.describe(name="商品名", price="価格", content="内容")
async def addproduct(interaction: discord.Interaction, name: str, price: int, content: str):
    if ADMIN_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("権限がありません。", ephemeral=True)
        return

    products = load_products()
    products.append({
        "name": name,
        "price": price,
        "content": content
    })
    save_products(products)

    await interaction.response.send_message(f"商品『{name}』を追加しました。", ephemeral=True)


@tree.command(name="shop", description="ショップ表示")
async def shop(interaction: discord.Interaction):
    products = load_products()

    if not products:
        await interaction.response.send_message("商品がありません。", ephemeral=True)
        return

    embed = discord.Embed(
        title="自販機ショップ",
        description="購入したい商品を選んでください。",
        color=discord.Color.gold()
    )

    for product in products:
        embed.add_field(
            name=f"{product['name']} - {product['price']}円",
            value=product['content'],
            inline=False
        )

    await interaction.response.send_message(
        embed=embed,
        view=ShopView(products)
    )


@tree.command(name="deleteproduct", description="商品削除")
@app_commands.describe(name="削除する商品名")
async def deleteproduct(interaction: discord.Interaction, name: str):
    if ADMIN_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("権限がありません。", ephemeral=True)
        return

    products = load_products()
    new_products = [p for p in products if p["name"] != name]

    if len(products) == len(new_products):
        await interaction.response.send_message("商品が見つかりません。", ephemeral=True)
        return

    save_products(new_products)
    await interaction.response.send_message(f"商品『{name}』を削除しました。", ephemeral=True)


# =========================
# 起動処理
# =========================
@bot.event
async def on_ready():
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())

    guild = discord.Object(id=GUILD_ID)
    await tree.sync(guild=guild)

    print(f"ログイン成功: {bot.user}")


bot.run(TOKEN)
