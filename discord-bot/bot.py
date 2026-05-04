import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# ======================
# 設定読み込み
# ======================

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID"))

PRODUCTS_FILE = "products.json"


# ======================
# 商品データ管理
# ======================
def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return []



def save_products(products):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=4, ensure_ascii=False)


# ======================
# Bot設定
# ======================
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


# ======================
# チケット閉鎖
# ======================
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="閉じる",
        style=discord.ButtonStyle.red,
        custom_id="close_ticket_button"
    )
    async def close_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "チケットを閉じます...",
            ephemeral=True
        )
        await interaction.channel.delete()


# ======================
# チケット作成
# ======================
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="チケット作成",
        style=discord.ButtonStyle.green,
        custom_id="create_ticket_button"
    )
    async def create_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        guild = interaction.guild
        user = interaction.user

        category = discord.utils.get(
            guild.categories,
            name="Tickets"
        )

        if category is None:
            category = await guild.create_category("Tickets")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),
            user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True
            ),
            guild.get_role(
                ADMIN_ROLE_ID
            ): discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True
            )
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category,
            overwrites=overwrites
        )

        await channel.send(
            f"{user.mention} チケットを作成しました。\n"
            f"管理者が対応します。",
            view=CloseTicketView()
        )

        await interaction.response.send_message(
            f"チケットを作成しました: {channel.mention}",
            ephemeral=True
        )


# ======================
# 自販機
# ======================
class ShopView(discord.ui.View):
    def __init__(self, products):
        super().__init__(timeout=None)

        for index, product in enumerate(products):
            button = discord.ui.Button(
                label=f"{product['name']} - ¥{product['price']}",
                style=discord.ButtonStyle.blurple,
                custom_id=f"buy_{index}"
            )

            button.callback = self.make_callback(index)
            self.add_item(button)

    def make_callback(self, index):
        async def callback(interaction: discord.Interaction):
            products = load_products()
            product = products[index]

            guild = interaction.guild
            user = interaction.user

            category = discord.utils.get(
                guild.categories,
                name="Tickets"
            )

            if category is None:
                category = await guild.create_category("Tickets")

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    view_channel=False
                ),
                user: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True
                ),
                guild.get_role(
                    ADMIN_ROLE_ID
                ): discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True
                )
            }

            channel = await guild.create_text_channel(
                name=f"purchase-{user.name}",
                category=category,
                overwrites=overwrites
            )

            await channel.send(
                f"購入希望商品:\n"
                f"**商品名:** {product['name']}\n"
                f"**価格:** ¥{product['price']}\n"
                f"**内容:** {product['content']}\n\n"
                f"{user.mention} 管理者が対応します。",
                view=CloseTicketView()
            )

            await interaction.response.send_message(
                f"購入チケットを作成しました: {channel.mention}",
                ephemeral=True
            )

        return callback


# ======================
# 起動時
# ======================
@bot.event
async def on_ready():
    print(f"ログイン成功: {bot.user}")

    guild = discord.Object(id=GUILD_ID)
    await tree.sync(guild=guild)


# ======================
# チケットパネル
# ======================
@tree.command(
    name="ticketpanel",
    description="チケットパネルを作成",
    guild=discord.Object(id=GUILD_ID)
)
async def ticketpanel(interaction: discord.Interaction):
    if ADMIN_ROLE_ID not in [
        role.id for role in interaction.user.roles
    ]:
        await interaction.response.send_message(
            "権限がありません。",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="サポートチケット",
        description="下のボタンを押してチケットを作成してください。",
        color=discord.Color.green()
    )

    await interaction.channel.send(
        embed=embed,
        view=TicketView()
    )

    await interaction.response.send_message(
        "チケットパネルを作成しました。",
        ephemeral=True
    )


# ======================
# 商品追加
# ======================
@tree.command(
    name="addproduct",
    description="商品追加",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    name="商品名",
    price="価格",
    content="内容"
)
async def addproduct(
    interaction: discord.Interaction,
    name: str,
    price: int,
    content: str
):
    if ADMIN_ROLE_ID not in [
        role.id for role in interaction.user.roles
    ]:
        await interaction.response.send_message(
            "権限がありません。",
            ephemeral=True
        )
        return

    products = load_products()

    products.append({
        "name": name,
        "price": price,
        "content": content
    })

    save_products(products)

    await interaction.response.send_message(
        f"商品追加完了: {name}",
        ephemeral=True
    )


# ======================
# 商品編集
# ======================
@tree.command(
    name="editproduct",
    description="商品編集",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    index="商品番号(0から)",
    name="新しい名前",
    price="新しい価格",
    content="新しい内容"
)
async def editproduct(
    interaction: discord.Interaction,
    index: int,
    name: str,
    price: int,
    content: str
):
    if ADMIN_ROLE_ID not in [
        role.id for role in interaction.user.roles
    ]:
        await interaction.response.send_message(
            "権限がありません。",
            ephemeral=True
        )
        return

    products = load_products()

    if index < 0 or index >= len(products):
        await interaction.response.send_message(
            "商品番号が無効です。",
            ephemeral=True
        )
        return

    products[index] = {
        "name": name,
        "price": price,
        "content": content
    }

    save_products(products)

    await interaction.response.send_message(
        f"商品更新完了: {name}",
        ephemeral=True
    )


# ======================
# 商品削除
# ======================
@tree.command(
    name="deleteproduct",
    description="商品削除",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    index="商品番号(0から)"
)
async def deleteproduct(
    interaction: discord.Interaction,
    index: int
):
    if ADMIN_ROLE_ID not in [
        role.id for role in interaction.user.roles
    ]:
        await interaction.response.send_message(
            "権限がありません。",
            ephemeral=True
        )
        return

    products = load_products()

    if index < 0 or index >= len(products):
        await interaction.response.send_message(
            "商品番号が無効です。",
            ephemeral=True
        )
        return

    removed = products.pop(index)

    save_products(products)

    await interaction.response.send_message(
        f"削除完了: {removed['name']}",
        ephemeral=True
    )


# ======================
# 自販機表示
# ======================
@tree.command(
    name="shop",
    description="自販機表示",
    guild=discord.Object(id=GUILD_ID)
)
async def shop(interaction: discord.Interaction):
    products = load_products()

    if not products:
        await interaction.response.send_message(
            "商品がありません。",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="自販機",
        description="購入したい商品を選択してください。",
        color=discord.Color.blue()
    )

    for i, product in enumerate(products):
        embed.add_field(
            name=f"{i}. {product['name']} - ¥{product['price']}",
            value=product["content"],
            inline=False
        )

    await interaction.channel.send(
        embed=embed,
        view=ShopView(products)
    )

    await interaction.response.send_message(
        "自販機を表示しました。",
        ephemeral=True
    )


# ======================
# 起動
# ======================
bot.run(TOKEN)
