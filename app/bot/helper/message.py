import discord

# these were copied from the app object. They could be made static instead but I'm lazy.
async def embederror(recipient, message, ephemeral=True):
    embed = discord.Embed(title="ERROR",description=message, color=0xf50000)
    await send_embed(recipient, embed, ephemeral)

async def embedinfo(recipient, message, ephemeral=True):
    embed = discord.Embed(title=message, color=0x00F500)
    await send_embed(recipient, embed, ephemeral)

async def embedcustom(recipient, title, fields, ephemeral=True):
    embed = discord.Embed(title=title)
    for k in fields:
        embed.add_field(name=str(k), value=str(fields[k]), inline=True)
    await send_embed(recipient, embed, ephemeral)

async def embedcustom2(recipient, title, description, footer, fields, ephemeral=True):
    embed = discord.Embed(title=title, description=description)
    embed.set_footer(text=footer)
    for k in fields:
        embed.add_field(name=str(k), value=str(fields[k]), inline=True)
    await send_embed(recipient, embed, ephemeral)    

async def send_info(recipient, message, ephemeral=True):
    if isinstance(recipient, discord.InteractionResponse):
        await recipient.send_message(message, ephemeral=ephemeral)
    elif isinstance(recipient, discord.User) or isinstance(recipient, discord.member.Member) or isinstance(recipient, discord.Webhook):
        await recipient.send(message)

async def send_embed(recipient, embed, ephemeral=True):
    if isinstance(recipient, discord.User) or isinstance(recipient, discord.member.Member) or isinstance(recipient, discord.Webhook):
        await recipient.send(embed=embed)
    elif isinstance(recipient, discord.InteractionResponse):
        await recipient.send_message(embed=embed, ephemeral = ephemeral)
