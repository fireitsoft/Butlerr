import discord
import app.bot.helper.db as db
from app.bot.helper.confighelper import *

async def get_stats(client):

    #print(ctx.guild.member_count)
    # print(client.guild.member_count)
    
    
    guilds = client.get_guild 
    all=online=robot=emby=jelly=waiting=0  
    #print(guilds.member_count) 
    for guild in client.guilds:
        #print(guild.name)
        total_members = 'Total Members:' + f' {len(guild.members)}'
        
        # here we take the roles from the current server
        jrole = discord.utils.get(guild.roles, name="jelly")
        erole = discord.utils.get(guild.roles, name="emby")
        wrole = discord.utils.get(guild.roles, name="waiting")
        
        for member in guild.members:
            if member.bot:
                robot += 1
            else:
                all += 1
                #print(member.status)
                if member.status != discord.Status.offline:
                    online += 1
                    
                if jrole in member.roles:
                     jelly += 1  
                if erole in member.roles:
                     emby += 1                       
                if wrole in member.roles:
                     waiting += 1    
                     
        tchannel = client.get_channel(1231332797315027035) # total stats channel
        ochannel = client.get_channel(1231333588327333968) # online users
        jchannel = client.get_channel(1231334096278655056) # jellyfin users
        echannel = client.get_channel(1231334282258284686) # emby users
        wchannel = client.get_channel(1231334796370776074) # waiting users
        
        await tchannel.edit(name = total_members)         
        await ochannel.edit(name = 'Online Users:' + f' {online}')   
        await jchannel.edit(name = 'Jellyfin Users:' + f' {jelly} / {jellyfin_userlimit}')
        await echannel.edit(name = 'Emby Users:' + f' {emby} / {emby_userlimit}') 
        await wchannel.edit(name = 'Waiting Users:' + f' {db.count_waiting()}') 
        #print(db.count_waiting())                               
        #print(emby)
    
