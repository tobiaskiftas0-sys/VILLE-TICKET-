import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os

TOKEN = os.getenv("TOKEN")
GUILD_ID = 123456789
CATEGORIA_TICKET_ID = 123456789
RUOLO_STAFF_ID = 123456789
MAPPA_EH_URL = "https://i.imgur.com/INSERISCI_LINK_MAPPA.png"

VILLE = {
    "A1": {"nome": "Villa A1 - Vinewood Hills", "prezzo": "€250.000", "emoji": "🏡"},
    "A2": {"nome": "Villa A2 - Vinewood Hills", "prezzo": "€300.000", "emoji": "🏡"},
    "A3": {"nome": "Villa A3 - Rockford Hills", "prezzo": "€450.000", "emoji": "🏠"},
    "A4": {"nome": "Villa A4 - Vespucci Beach", "prezzo": "€500.000", "emoji": "🏖️"},
    "B1": {"nome": "Casa B1 - Mirror Park", "prezzo": "€120.000", "emoji": "🏠"},
    "B2": {"nome": "Casa B2 - Sandy Shores", "prezzo": "€80.000", "emoji": "🏜️"},
    "C1": {"nome": "Villa C1 - Paleto Bay", "prezzo": "€180.000", "emoji": "🌲"},
}

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class InfoVillaModal(discord.ui.Modal, title="Info Aggiuntive (Facoltativo)"):
    uso = discord.ui.TextInput(label="Uso della villa / casa", placeholder="Es: Abitazione, Base gang, Azienda... (facoltativo)", required=False, max_length=100)
    note = discord.ui.TextInput(label="Note aggiuntive", placeholder="Es: Ho gia i soldi, voglio visitarla... (facoltativo)", required=False, style=discord.TextStyle.paragraph, max_length=500)

    def __init__(self, villa_key: str):
        super().__init__()
        self.villa_key = villa_key

    async def on_submit(self, interaction: discord.Interaction):
        villa = VILLE[self.villa_key]
        guild = interaction.guild
        user = interaction.user
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.get_role(RUOLO_STAFF_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        categoria = guild.get_channel(CATEGORIA_TICKET_ID)
        channel = await guild.create_text_channel(name=f"villa-{self.villa_key.lower()}-{user.name}", category=categoria, overwrites=overwrites, topic=f"Ticket Villa {self.villa_key} | {user.id}")
        uso_text = self.uso.value if self.uso.value else "Non specificato"
        note_text = self.note.value if self.note.value else "Nessuna"
        embed = discord.Embed(title=f"Richiesta {villa['nome']}", description=f"Nuova richiesta da {user.mention}", color=discord.Color.gold())
        embed.add_field(name="Villa Selezionata", value=f"**{self.villa_key}** - {villa['nome']}", inline=False)
        embed.add_field(name="Prezzo", value=villa['prezzo'], inline=True)
        embed.add_field(name="Richiedente", value=f"{user.mention}", inline=True)
        embed.add_field(name="Uso Previsto", value=uso_text, inline=False)
        embed.add_field(name="Note", value=note_text, inline=False)
        embed.set_thumbnail(url=user.display_avatar.url)
        view = ChiudiTicketView()
        await channel.send(content=f"{user.mention} <@&{RUOLO_STAFF_ID}>", embed=embed, view=view)
        await interaction.response.send_message(f"Ticket aperto! Vai su {channel.mention}", ephemeral=True)

class ChiudiTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Chiudi Ticket", style=discord.ButtonStyle.red, custom_id="chiudi_ticket")
    async def chiudi(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket in chiusura tra 5 secondi...", ephemeral=False)
        await asyncio.sleep(5)
        await interaction.channel.delete()

class VillaSelect(discord.ui.Select):
    def __init__(self):
        options = []
        for key, data in VILLE.items():
            options.append(discord.SelectOption(label=f"{key} - {data['nome']}", description=f"Prezzo: {data['prezzo']}", emoji=data['emoji'], value=key))
        super().__init__(placeholder="Seleziona una villa / casa...", min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(InfoVillaModal(self.values[0]))

class VillaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(VillaSelect())

@bot.tree.command(name="ticket", description="Apri un ticket per comprare una villa / casa")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def ticket(interaction: discord.Interaction):
    embed = discord.Embed(title="MAPPA VILLE & CASE - EH", description="**Benvenuto nel sistema acquisto ville!**\n\nGuarda la mappa, seleziona dal menu la villa che vuoi e ti si aprira un ticket in automatico.\n\n**Zone:**\nA1 - A4 -> Lusso / Vinewood / Vespucci\nB1 - B2 -> Citta / Sandy\nC1 -> Paleto Bay\n\n*Info sull'uso facoltative.*", color=discord.Color.blue())
    embed.set_image(url=MAPPA_EH_URL)
    embed.set_footer(text="Sistema Ville EH")
    await interaction.response.send_message(embed=embed, view=VillaView(), ephemeral=True)

@bot.event
async def on_ready():
    print(f"Bot online come {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Sincronizzati {len(synced)} comandi")
    except Exception as e:
        print(e)

bot.run(TOKEN)