import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import re

TOKEN = os.getenv("TOKEN")
GUILD_ID = 1488262125708116198
CATEGORIA_TICKET_ID = 1488541441373241364
RUOLO_STAFF_ID = 1498676038937481246
MAPPA_EH_URL = "INSERISCI_QUI_LINK_MAPPA"

VILLE = {
    "A1": {"nome": "Villa A1 - Collina Nord", "prezzo": "€30.000", "emoji": "🏡", "tipo": "VILLA", "zona": "Nord-Ovest, sopra il fiume"},
    "A2": {"nome": "Villa A2 - Ponte Centrale", "prezzo": "€35.000", "emoji": "🏡", "tipo": "VILLA", "zona": "Centro-Nord, vicino al ponte"},
    "A3": {"nome": "Villa A3 - Porto Est", "prezzo": "€40.000", "emoji": "🏠", "tipo": "VILLA", "zona": "Est, zona porto"},
    "A4": {"nome": "Villa A4 - Costa Sud-Est", "prezzo": "€45.000", "emoji": "🏖️", "tipo": "VILLA", "zona": "Sud-Est, vicino al mare"},
    "B1": {"nome": "Casa B1 - Quartiere Ovest", "prezzo": "€15.000", "emoji": "🏠", "tipo": "CASA", "zona": "Ovest, quartiere residenziale"},
    "B2": {"nome": "Casa B2 - Centro Citta", "prezzo": "€10.000", "emoji": "🏜️", "tipo": "CASA", "zona": "Centro, centro citta"},
    "B3": {"nome": "Casa B3 - Periferia Sud", "prezzo": "€20.000", "emoji": "🌲", "tipo": "CASA", "zona": "Sud, vicino autostrada"},
}

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

def nome_sicuro(nome):
    # Toglie spazi e caratteri strani che fanno crashare Discord
    nome = nome.lower()
    nome = re.sub(r'[^a-z0-9-]', '-', nome)
    nome = re.sub(r'-+', '-', nome)
    return nome[:20] or "utente"

class InfoModal(discord.ui.Modal, title="Info Facoltative"):
    uso = discord.ui.TextInput(label="Uso villa/casa", placeholder="Es: Abitazione, Base gang...", required=False, max_length=100)
    note = discord.ui.TextInput(label="Note", placeholder="Es: Ho gia i soldi...", required=False, style=discord.TextStyle.paragraph, max_length=500)
    def __init__(self, key):
        super().__init__()
        self.key = key
    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            v = VILLE[self.key]
            guild = interaction.guild
            user = interaction.user
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
            }
            staff = guild.get_role(RUOLO_STAFF_ID)
            if staff:
                overwrites[staff] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
            cat = guild.get_channel(CATEGORIA_TICKET_ID)
            nome_canale = f"{self.key.lower()}-{nome_sicuro(user.name)}"
            ch = await guild.create_text_channel(name=nome_canale, category=cat if isinstance(cat, discord.CategoryChannel) else None, overwrites=overwrites)
            embed = discord.Embed(title=f"{v['emoji']} {v['tipo']} - {v['nome']}", description=f"Richiesta di {user.mention}", color=discord.Color.gold())
            embed.add_field(name="Scelta", value=f"**{self.key}** - {v['nome']}", inline=False)
            embed.add_field(name="Zona", value=v['zona'], inline=False)
            embed.add_field(name="Prezzo", value=v['prezzo'], inline=True)
            embed.add_field(name="Tipo", value=v['tipo'], inline=True)
            embed.add_field(name="Utente", value=user.mention, inline=False)
            embed.add_field(name="Uso", value=self.uso.value or "Non specificato", inline=False)
            embed.add_field(name="Note", value=self.note.value or "Nessuna", inline=False)
            await ch.send(content=f"{user.mention} <@&{RUOLO_STAFF_ID}>", embed=embed, view=ChiudiView())
            await interaction.followup.send(f"Ticket aperto! Vai su {ch.mention}", ephemeral=True)
        except Exception as e:
            print(f"ERRORE TICKET: {e}")
            try:
                await interaction.followup.send(f"Errore nel creare il ticket: `{e}`\nControlla che il bot abbia permesso Gestisci Canali e che la categoria sia giusta.", ephemeral=True)
            except:
                pass

class ChiudiView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Chiudi Ticket", style=discord.ButtonStyle.red, custom_id="chiudi_ticket_fisso")
    async def chiudi(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Chiusura tra 5 secondi...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class Scelta(discord.ui.Select):
    def __init__(self):
        opts = [discord.SelectOption(label=f"{k} - {d['nome']}", description=f"{d['zona']} - Prezzo: {d['prezzo']}", emoji=d['emoji'], value=k) for k, d in VILLE.items()]
        super().__init__(placeholder="Scegli Villa o Casa...", custom_id="scelta_villa_fissa", options=opts)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(InfoModal(self.values[0]))

class Pannello(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Scelta())

@bot.tree.command(name="ticket_pannel", description="Apri pannello ville e case")
async def ticket_pannel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="MAPPA VILLE & CASE - EH",
        description="**Scegli la tua Villa o Casa!**\n\n**VILLE (A):**\nA1 Collina Nord - €30.000\nA2 Ponte Centrale - €35.000\nA3 Porto Est - €40.000\nA4 Costa Sud-Est - €45.000\n\n**CASE (B):**\nB1 Quartiere Ovest - €15.000\nB2 Centro Citta - €10.000\nB3 Periferia Sud - €20.000\n\nSeleziona dal menu qui sotto",
        color=discord.Color.blue()
    )
    if MAPPA_EH_URL.startswith("http"):
        embed.set_image(url=MAPPA_EH_URL)
    await interaction.response.send_message(embed=embed, view=Pannello())

@bot.event
async def on_ready():
    print(f"ONLINE {bot.user}")
    # Rende il pannello persistente anche dopo il restart
    bot.add_view(Pannello())
    bot.add_view(ChiudiView())
    await bot.tree.sync()
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print("Comandi sincronizzati")

bot.run(TOKEN)