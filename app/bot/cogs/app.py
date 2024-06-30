from pickle import FALSE
from app.bot.helper.textformat import bcolors
from datetime import datetime
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
import app.bot.helper.db as db
import app.bot.helper.plexhelper as plexhelper
import app.bot.helper.jellyfinhelper as jelly
import app.bot.helper.embyhelper as emby
import texttable
from app.bot.helper.message import *
from app.bot.helper.confighelper import *

CONFIG_PATH = 'app/config/config.ini'
BOT_SECTION = 'bot_envs'

plex_configured = True
jellyfin_configured = True
emby_configured = True

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

plex_token_configured = True
try:
    PLEX_TOKEN = config.get(BOT_SECTION, 'plex_token')
    PLEX_BASE_URL = config.get(BOT_SECTION, 'plex_base_url')
except:
    print("No Plex auth token details found")
    plex_token_configured = False

# Get Plex config
try:
    PLEXUSER = config.get(BOT_SECTION, 'plex_user')
    PLEXPASS = config.get(BOT_SECTION, 'plex_pass')
    PLEX_SERVER_NAME = config.get(BOT_SECTION, 'plex_server_name')
except:
    print("No Plex login info found")
    if not plex_token_configured:
        print("Could not load plex config")
        plex_configured = False

# Get Plex roles config
try:
    plex_roles = config.get(BOT_SECTION, 'plex_roles')
except:
    plex_roles = None
if plex_roles:
    plex_roles = list(plex_roles.split(','))
else:
    plex_roles = []

# Get Plex libs config
try:
    Plex_LIBS = config.get(BOT_SECTION, 'plex_libs')
except:
    Plex_LIBS = None
if Plex_LIBS is None:
    Plex_LIBS = ["all"]
else:
    Plex_LIBS = list(Plex_LIBS.split(','))

# Get Plex users limit
try:
    plex_userlimit = int(config.get(BOT_SECTION, 'plex_userlimit'))
except:
    plex_userlimit = 0

    
# Get Jellyfin config
try:
    JELLYFIN_SERVER_URL = config.get(BOT_SECTION, 'jellyfin_server_url')
    JELLYFIN_API_KEY = config.get(BOT_SECTION, "jellyfin_api_key")
except:
    jellyfin_configured = False

# Get Jellyfin roles config
try:
    jellyfin_roles = config.get(BOT_SECTION, 'jellyfin_roles')
except:
    jellyfin_roles = None
if jellyfin_roles:
    jellyfin_roles = list(jellyfin_roles.split(','))
else:
    jellyfin_roles = []

# Get Jellyfin libs config
try:
    jellyfin_libs = config.get(BOT_SECTION, 'jellyfin_libs')
except:
    jellyfin_libs = None
if jellyfin_libs is None:
    jellyfin_libs = ["all"]
else:
    jellyfin_libs = list(jellyfin_libs.split(','))

# Get Jellyfin users limit
try:
    jellyfin_userlimit = int(config.get(BOT_SECTION, 'jellyfin_userlimit'))
except:
    jellyfin_userlimit = 0



# Get Emby config
try:
    EMBY_SERVER_URL = config.get(BOT_SECTION, 'emby_server_url')
    EMBY_API_KEY = config.get(BOT_SECTION, "emby_api_key")
except:
    emby_configured = False

# Get Emby roles config
try:
    emby_roles = config.get(BOT_SECTION, 'emby_roles')
except:
    emby_roles = None
if emby_roles:
    emby_roles = list(emby_roles.split(','))
else:
    emby_roles = []

# Get Emby libs config
try:
    emby_libs = config.get(BOT_SECTION, 'emby_libs')
except:
    emby_libs = None
if emby_libs is None:
    emby_libs = ["all"]
else:
    emby_libs = list(emby_libs.split(','))

# Get Emby users limit
try:
    emby_userlimit = int(config.get(BOT_SECTION, 'emby_userlimit'))
except:
    emby_userlimit = 0


# Get Enable config
try:
    USE_JELLYFIN = config.get(BOT_SECTION, 'jellyfin_enabled')
    USE_JELLYFIN = USE_JELLYFIN.lower() == "true"
except:
    USE_JELLYFIN = False

try:
    USE_EMBY = config.get(BOT_SECTION, 'emby_enabled')
    USE_EMBY = USE_EMBY.lower() == "true"
except:
    USE_EMBY = False

try:
    USE_PLEX = config.get(BOT_SECTION, "plex_enabled")
    USE_PLEX = USE_PLEX.lower() == "true"
except:
    USE_PLEX = False

try:
    USE_LOG = config.get(BOT_SECTION, "logchannel_id")
    #USE_LOG = USE_LOG.lower() == "true"
except:
    USE_LOG = False

try:
    JELLYFIN_EXTERNAL_URL = config.get(BOT_SECTION, "jellyfin_external_url")
    if not JELLYFIN_EXTERNAL_URL:
        JELLYFIN_EXTERNAL_URL = JELLYFIN_SERVER_URL
except:
    JELLYFIN_EXTERNAL_URL = JELLYFIN_SERVER_URL
    print("Could not get Jellyfin external url. Defaulting to server url.")

try:
    EMBY_EXTERNAL_URL = config.get(BOT_SECTION, "emby_external_url")
    if not EMBY_EXTERNAL_URL:
        EMBY_EXTERNAL_URL = EMBY_SERVER_URL
except:
    EMBY_EXTERNAL_URL = EMBY_SERVER_URL
    print("Could not get Emby external url. Defaulting to server url.")

if USE_PLEX and plex_configured:
    try:
        print("Connecting to Plex......")
        if plex_token_configured and PLEX_TOKEN and PLEX_BASE_URL:
            print("Using Plex auth token")
            plex = PlexServer(PLEX_BASE_URL, PLEX_TOKEN)
        else:
            print("Using Plex login info")
            account = MyPlexAccount(PLEXUSER, PLEXPASS)
            plex = account.resource(PLEX_SERVER_NAME).connect()  # returns a PlexServer instance
        print('Logged into plex!')
    except Exception as e:
        # probably rate limited.
        print('Error with plex login. Please check Plex authentication details. If you have restarted the bot multiple times recently, this is most likely due to being ratelimited on the Plex API. Try again in 10 minutes.')
        print(f'Error: {e}')
else:
    print(f"Plex {'disabled' if not USE_PLEX else 'not configured'}. Skipping Plex login.")


class app(commands.Cog):
    # App command groups
    plex_commands = app_commands.Group(name="plex", description="Butlerr Plex commands")
    jellyfin_commands = app_commands.Group(name="jellyfin", description="Butlerr Jellyfin commands")
    emby_commands = app_commands.Group(name="emby", description="Butlerr Emby commands")
    butlerr_commands = app_commands.Group(name="butlerr", description="Butlerr general commands")

    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('------')
        print("{:^41}".format(f"Butlerr V{BUTLERR_VERSION}"))
        print(f'Made by Velun https://github.com/fireitsoft\n')
        print(f'Forked from Membarr https://github.com/Yoruio/Membarr')
        print(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')
        print('------')
        await self.write_logs("Bot started")
        #await self.write_logs(f"{Discord_leave_message}")
        #await self.write_logs(f"{Discord_leave_message}")
        

        # TODO: Make these debug statements work. roles are currently empty arrays if no roles assigned.
        if plex_roles is None:
            print('Configure Plex roles to enable auto invite to Plex after a role is assigned.')
        if jellyfin_roles is None:
            print('Configure Jellyfin roles to enable auto invite to Jellyfin after a role is assigned.')
        if emby_roles is None:
            print('Configure Emby roles to enable auto invite to Emby after a role is assigned.')

    async def write_logs(self, message: str, mtype: str=None):
        if USE_LOG:
            channel_id = config.get(BOT_SECTION, 'logchannel_id')
            channel = self.bot.get_channel(int(channel_id))
            color = discord.Color.blue()
            title = "Info"
            if channel:
                if mtype:
                    if mtype == "info":
                        color = discord.Color.blue()
                        title = "Info"
                    elif mtype == "warning":
                        color = discord.Color.gold()
                        title = "Warning"
                    elif mtype == "error":
                        color = discord.Color.brand_red()
                        title = "Error"
                    elif mtype == "success":
                        color = discord.Color.green()
                        title = "Success"
                    elif mtype == "fancy":
                        color = discord.Color.fuchsia()
                        title = "Message"
                embed = discord.Embed(title=title, description=datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ": " + message, color=color)
                await channel.send(embed=embed)
                #await channel.send(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n" + message)
            else:
                print(f"Channel with ID {channel_id} not found.")
        else:
            print("Logging disabled")
    
    async def getemail(self, after):
        email = None
        await embedinfo(after,'Welcome To '+ PLEX_SERVER_NAME +'. Please reply with your email to be added to the Plex server!')
        await embedinfo(after,'If you do not respond within 24 hours, the request will be cancelled, and the server admin will need to add you manually.')
        while(email == None):
            def check(m):
                return m.author == after and not m.guild
            try:
                email = await self.bot.wait_for('message', timeout=86400, check=check)
                if(plexhelper.verifyemail(str(email.content))):
                    return str(email.content)
                else:
                    email = None
                    message = "The email you provided is invalid, please respond only with the email you used to sign up for Plex."
                    await embederror(after, message)
                    continue
            except asyncio.TimeoutError:
                message = "Timed out. Please contact the server admin directly."
                await embederror(after, message)
                return None
    
    async def getusername(self, after, platform):
        username = None
        if platform == "jelly":
            await embedinfo(after, f"Welcome To Jellyfin! Please reply with your desiered username to be added to the Jellyfin server!")
        elif platform == "emby":
            await embedinfo(after, f"Welcome To Emby! If you have an Emby Connect account then please reply with your email and if you don't have one or don't know what it is please reply with a username to be added to the Emby server!")
        await embedinfo(after, f"If you do not respond within 24 hours, the request will be cancelled, and you will need to be invited again.")
        while (username is None):
            def check(m):
                return m.author == after and not m.guild
            try:
                username = await self.bot.wait_for('message', timeout=86400, check=check)
                if platform == "jelly":
                    if(jelly.verify_username(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, str(username.content))):
                        return str(username.content)
                    else:
                        username = None
                        message = "This username is already choosen. Please select another username."
                        await embederror(after, message)
                        continue
                elif platform == "emby":
                    if(emby.verify_username(EMBY_SERVER_URL, EMBY_API_KEY, str(username.content))):
                        return str(username.content)
                    else:
                        username = None
                        message = "This username is already choosen. Please select another username."
                        await embederror(after, message)
                        continue                  
            except asyncio.TimeoutError:
                message = "The invite timed out. Please contact the server admin to be invited again."
                await embederror(after, message)
                return None
            except Exception as e:
                await embederror(after, "Something went wrong. Please try again with another username.")
                print (e)
                username = None             

    async def addtoplex(self, email, response):
        if(plexhelper.verifyemail(email)):
            if plexhelper.plexadd(plex,email,Plex_LIBS):
                await embedinfo(response, 'This email address has been added to plex')
                return True
            else:
                await embederror(response, 'There was an error adding this email address. Check logs.')
                return False
        else:
            await embederror(response, 'Invalid email.')
            return False

    async def removefromplex(self, email, response):
        if(plexhelper.verifyemail(email)):
            if plexhelper.plexremove(plex,email):
                await embedinfo(response, 'This email address has been removed from plex.')
                return True
            else:
                await embederror(response, 'There was an error removing this email address. Check logs.')
                return False
        else:
            await embederror(response, 'Invalid email.')
            return False
    
    async def addtojellyfin(self, username, password, response):
        if not jelly.verify_username(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, username):
            await embederror(response, f'An account with username {username} already exists.')
            return False

        if jelly.add_user(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, username, password, jellyfin_libs):
            return True
        else:
            await embederror(response, 'There was an error adding this user to Jellyfin. Check logs for more info.')
            return False

    async def removefromjellyfin(self, username, response):
        if jelly.verify_username(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, username):
            await embederror(response, f'Could not find account with username {username}.')
            return
        
        if jelly.remove_user(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, username):
            await embedinfo(response, f'Successfully removed user {username} from Jellyfin.')
            return True
        else:
            await embederror(response, f'There was an error removing this user from Jellyfin. Check logs for more info.')
            return False

    async def cleanupjellyfin(self, response, days):
        all = db.read_all_jellyfin()
        removed_count = 0
        for index, peoples in enumerate(all):
            user_id = int(peoples[1])
            dbuser = self.bot.get_user(user_id)
            if dbuser:
                last = jellyfin.get_lastactivity(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY,peoples[3])
                if last:
                    if last > days:
                        guild = response.guild
                        member = guild.get_member(user_id)
                        if member:
                            jellyfin_role = discord.utils.get(guild.roles, name="jelly")
                            if jellyfin_role and jellyfin_role in member.roles:
                                #await member.remove_roles(jellyfin_role)
                                #await response.send_message(f"Removed {emby_role_name} role from {member.display_name} due to inactivity.")
                                removed_count += 1
                    
        await response.channel.send(f"Removed {removed_count} users from the 'Jellyfin' role due to inactivity.")

        if removed_count > 0:
            return True
        else:
            return False

    async def cleanupemby(self, response, days):
        all = db.read_all_emby()
        removed_count = 0
        #all = db.read_all()
        for index, peoples in enumerate(all):
            user_id = int(peoples[1])
            dbuser = self.bot.get_user(user_id)
            if dbuser:
                last = emby.get_lastactivity(EMBY_SERVER_URL, EMBY_API_KEY,peoples[4])
                if last:
                    if last > days:
                        guild = response.guild
                        member = guild.get_member(user_id)
                        if member:
                            emby_role = discord.utils.get(guild.roles, name="emby")
                            if emby_role and emby_role in member.roles:
                                #await member.remove_roles(emby_role)
                                #await response.send_message(f"Removed {emby_role_name} role from {member.display_name} due to inactivity.")
                                removed_count += 1
                    
        await response.channel.send(f"Removed {removed_count} users from the 'Emby' role due to inactivity.")

        if removed_count > 0:
            return True
        else:
            return False

    async def addtoemby(self, username, password, response):
        if not emby.verify_username(EMBY_SERVER_URL, EMBY_API_KEY, username):
            await embederror(response, f'An account with username {username} already exists.')
            return False

        if emby.add_user(EMBY_SERVER_URL, EMBY_API_KEY, username, password, emby_libs):
            return True
        else:
            await embederror(response, 'There was an error adding this user to Emby. Check logs for more info.')
            return False

    async def removefromemby(self, username, response):
        if emby.verify_username(EMBY_SERVER_URL, EMBY_API_KEY, username):
            await embederror(response, f'Could not find account with username {username}.')
            return
        
        if jelly.remove_user(EMBY_SERVER_URL, EMBY_API_KEY, username):
            await embedinfo(response, f'Successfully removed user {username} from Emby.')
            return True
        else:
            await embederror(response, f'There was an error removing this user from Emby. Check logs for more info.')
            return False        

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        
        if plex_roles is None and jellyfin_roles is None and emby_roles is None:
            return
        roles_in_guild = after.guild.roles
        role = None

        plex_processed = False
        jellyfin_processed = False
        emby_processed = False


        # Check Plex roles
        if plex_configured and USE_PLEX:
            for role_for_app in plex_roles:
                for role_in_guild in roles_in_guild:
                    if role_in_guild.name == role_for_app:
                        role = role_in_guild

                    #if the user is added to plex then we remove him from waiting list
                    waiting = db.delete_user_waiting(after.id)
                    if(waiting):
                        await self.write_logs("User **" + after.mention + "** deleted from waiting list.")

                    # Plex role was added
                    if role is not None and (role in after.roles and role not in before.roles):
                        email = await self.getemail(after)
                        if email is not None:
                            await embedinfo(after, "Got it we will be adding your email to plex shortly!")
                            await self.write_logs("User **" + after.mention + "** sets plex email to **" + email + "**")
                            if plexhelper.plexadd(plex,email,Plex_LIBS):
                                db.save_user(str(after.id), email, 'plex')
                                await asyncio.sleep(5)
                                await embedinfo(after, 'You have Been Added To Plex! Login to plex and accept the invite!')
                                await self.write_logs("Email **" + email + "** was created on Plex for discord user **" + after.mention + "**", "success")
                            else:
                                await embedinfo(after, 'There was an error adding this email address. Message Server Admin.')
                                await self.write_logs("There was an error adding **" + email + "** on plex. Contact **" + after.name + "** on discord if you need info.", "error")
                        else:
                            await after.remove_roles(role)
                        plex_processed = True
                        break

                    # Plex role was removed
                    elif role is not None and (role not in after.roles and role in before.roles):
                        try:
                            user_id = after.id
                            email = db.get_username(user_id, 'plex')
                            plexhelper.plexremove(plex,email)
                            deleted = db.remove_username(user_id, 'plex')
                            if deleted:
                                print("Removed Plex email {} from db".format(after.name))
                                await self.write_logs("Removed Plex from **" + after.mention + "**", "success")
                                #await secure.send(plexname + ' ' + after.mention + ' was removed from plex')
                            else:
                                print("Cannot remove Plex from this user.")
                                await self.write_logs("Cannot remove **PLEX** from **" + after.mention + "** with id " + after.id + ". Please check your database.", "error")
                            await embedinfo(after, "You have been removed from Plex")
                        except Exception as e:
                            print(e)
                            print("{} Cannot remove this user from plex.".format(email))
                            await self.write_logs("Cannot remove **" + email + "** from Plex.", "error")
                        plex_processed = True
                        break
                if plex_processed:
                    break

        role = None
        # Check Jellyfin roles
        if jellyfin_configured and USE_JELLYFIN:
            for role_for_app in jellyfin_roles:
                for role_in_guild in roles_in_guild:
                    if role_in_guild.name == role_for_app:
                        role = role_in_guild

                    # Jellyfin role was added
                    if role is not None and (role in after.roles and role not in before.roles):
                        print("Jellyfin role added")
                        #if the user is added to jellyfin then we remove him from waiting list
                        waiting = db.delete_user_waiting(after.id)
                        if(waiting):
                            await self.write_logs("User **" + after.mention + "** deleted from waiting list.")                        
                        await self.write_logs("User **" + after.mention + "** invited to jellyfin.")
                        username = await self.getusername(after, 'jelly')
                        print("Username retrieved from user")
                        if username is not None:
                            await embedinfo(after, "Got it we will be creating your Jellyfin account shortly!")
                            await self.write_logs("User **" + after.mention + "** sets jellyfin username to **" + username + "**")
                            password = jelly.generate_password(16)
                            if jelly.add_user(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, username, password, jellyfin_libs):
                                db.save_user(str(after.id), username, 'jellyfin')
                                await asyncio.sleep(5)
                                #await embedcustom(after, "You have been added to Jellyfin!", {'Username': username, 'Password': f"||{password}||"})
                                #await embedinfo(after, f"You have been added to Jellyfin!")
                                #await embedinfo(after, f"Go to {JELLYFIN_EXTERNAL_URL} to log in!")
                                await embedcustom2(after, "You have been added to Jellyfin!", f"Go and download the Jellyfin app for you device and install it. Open the app and on host enter: ```{JELLYFIN_EXTERNAL_URL}``` and if the app asks for a port then leave it empty. After that click connect on the server and login with the following details:", "If you need additional help ask in the help-center channel", {'Username': username, 'Password': f"||{password}||"})
                                await self.write_logs("User **" + username + "** was created on jellyfin for discord user **" + after.mention + "**", "success")
                            else:
                                await embedinfo(after, 'There was an error adding this user to Jellyfin. Message Server Admin.')
                                await self.write_logs("There was an error adding **" + username + "** on jellyfin. Contact **" + after.name + "** on discord if you need info.", "error")
                        else:
                            await after.remove_roles(role)
                            await self.write_logs("The invite expired. We removed role " + str(role) + " from **" + after.mention + "**.", "warning")
                        jellyfin_processed = True
                        break

                    # Jellyfin role was removed
                    elif role is not None and (role not in after.roles and role in before.roles):
                        print("Jellyfin role removed")
                        await self.write_logs("Role **" + str(role) + "** was removed for discord user **" + after.mention + "**", "success")
                        try:
                            user_id = after.id
                            username = db.get_username(user_id, 'jellyfin')
                            jelly.remove_user(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, username)
                            deleted = db.remove_username(user_id, 'jellyfin')
                            if deleted:
                                print("Removed Jellyfin from {}".format(after.name))
                                await self.write_logs("Removed Jellyfin from **" + after.mention + "**", "success")
                            else:
                                print("Cannot remove Jellyfin from this user")
                                await self.write_logs("Cannot remove **Jellyfin** from **" + after.mention + "** with id " + after.mention + ".", "error")
                            await embedinfo(after, "You have been removed from Jellyfin")
                        except Exception as e:
                            print(e)
                            print("{} Cannot remove this user from Jellyfin.".format(username))
                            await self.write_logs("Cannot remove **" + after.mention + "** from Jellyfin.", "error")
                        jellyfin_processed = True
                        break
                if jellyfin_processed:
                    break

        role = None
        # Check Emby roles
        if emby_configured and USE_EMBY:
            for role_for_app in emby_roles:
                for role_in_guild in roles_in_guild:
                    if role_in_guild.name == role_for_app:
                        role = role_in_guild

                    # Emby role was added
                    if role is not None and (role in after.roles and role not in before.roles):
                        print("Emby role added")
                        #if the user is added to emby then we remove him from waiting list
                        waiting = db.delete_user_waiting(after.id)
                        if(waiting):
                            await self.write_logs("User **" + after.mention + "** deleted from waiting list.")                        
                        await self.write_logs("User **" + after.mention + "** invited to emby.")
                        username = await self.getusername(after, 'emby')
                        print("Username retrieved from user")
                        if username is not None:
                            await embedinfo(after, "Got it we will be creating your Emby account shortly!")
                            password = emby.generate_password(16)
                            await self.write_logs("User **" + after.mention + "** sets emby username to **" + username + "**")
                            if emby.add_user(EMBY_SERVER_URL, EMBY_API_KEY, username, password, emby_libs):
                                db.save_user(str(after.id), username, 'emby')
                                await asyncio.sleep(5)
                                #await embedcustom(after, "You have been added to Emby!", {'Username': username, 'Password': f"||{password}||"})
                                #await embedinfo(after, f"Go to {EMBY_EXTERNAL_URL} to log in!")
                                if emby.is_valid_email(username):
                                    await embedcustom2(after, "You have been added to Emby!", f"Go and check your email for an Confirm Emby Account email and click on I Confirm This Link. After that the server should appear in your account. Go and download the Emby app for you device, install it and log in.", "If you need additional help ask in the help-center channel", {})
                                else:
                                    await embedcustom2(after, "You have been added to Emby!", f"Go and download the Emby app for you device and install it. Open the app and on host enter: ```{EMBY_EXTERNAL_URL}``` and if the app asks for a port then leave it empty or set it to 8196. After that click connect on the server and login with the following details:", "If you need additional help ask in the help-center channel", {'Username': username, 'Password': f"||{password}||"})
                                await self.write_logs("User **" + username + "** was created on emby for discord user **" + after.mention + "**", "success")
                            else:
                                await embedinfo(after, 'There was an error adding this user to Emby. Message Server Admin.')
                                await self.write_logs("There was an error adding **" + username + "** on emby. Contact **" + after.name + "** on discord if you need info.", "error")
                        else:
                            await after.remove_roles(role)
                            await self.write_logs("The invite expired. We removed role " + str(role) + " from **" + after.mention + "**.", "warning")
                        emby_processed = True
                        break

                    # Emby role was removed
                    elif role is not None and (role not in after.roles and role in before.roles):
                        print("Emby role removed")
                        await self.write_logs("Role **" + str(role) + "** was removed for discord user **" + after.mention + "**", "success")
                        try:
                            user_id = after.id
                            username = db.get_username(user_id, 'emby')
                            emby.remove_user(EMBY_SERVER_URL, EMBY_API_KEY, username)
                            deleted = db.remove_username(user_id, 'emby')
                            if deleted:
                                print("Removed Emby from {}".format(after.name))
                                await self.write_logs("Removed Emby from **" + after.mention + "**", "success")
                                #await secure.send(plexname + ' ' + after.mention + ' was removed from plex')
                            else:
                                print("Cannot remove Emby from this user")
                                await self.write_logs("Cannot remove **Emby** from **" + after.mention + "** with id " + after.mention + ".", "error")
                            await embedinfo(after, "You have been removed from Emby")
                        except Exception as e:
                            print(e)
                            print("{} Cannot remove this user from Jellyfin.".format(username))
                            await self.write_logs("Cannot remove **" + after.mention + "** from Jellyfin.", "error")
                        emby_processed = True
                        break
                if emby_processed:
                    break

                

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send("The bat **" + member.mention +"** has left the colony.")
            
        if USE_PLEX and plex_configured:
            email = db.get_username(member.id, 'plex')
            plexhelper.plexremove(plex,email)
        
        if USE_JELLYFIN and jellyfin_configured:
            jellyfin_username = db.get_username(member.id, 'jellyfin')
            jelly.remove_user(JELLYFIN_SERVER_URL, JELLYFIN_API_KEY, jellyfin_username)

        if USE_EMBY and emby_configured:
            emby_username = db.get_username(member.id, 'emby')
            emby.remove_user(EMBY_SERVER_URL, EMBY_API_KEY, emby_username)            
            
        deleted = db.delete_user(member.id)
        if deleted:
            if USE_PLEX and plex_configured:
                if email is not False:
                    await self.write_logs("Removed {} from plex because user left discord server.".format(email))
            if USE_JELLYFIN and jellyfin_configured:
                if jellyfin_username is not False:
                    await self.write_logs("Removed {} from jellyfin because user left discord server.".format(jellyfin_username))
            if USE_EMBY and emby_configured:
                if emby_username is not False:
                    await self.write_logs("Removed {} from emby because user left discord server.".format(emby_username))

        waiting = db.delete_user_waiting(member.id)                   
        if(waiting):
            await self.write_logs("Removed {} from waiting list because user left discord server.".format(member.mention))

    #welcome message
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
           #await channel.send(f"Hey **" + member.mention +"**, welcome to BatCave!\n Head over to <#{Discord_waiting_list}> and type the platform you want to get invited. You type jellyfin for invite to jellyfin server or emby for emby server, and you will get invited when there are available spots.")
           await channel.send("Hey **" + member.mention + "**, welcome to BatCave!\nHead over to <#1208463345057800202> and type the platform you want to get invited. You type jellyfin for invite to jellyfin server or emby for emby server, and you will get invited when there are available spots.")
            
    @commands.Cog.listener()      
    async def on_message(self, message):
        #username = str(message.author).split("#")[0] 
        #channel = str(message.channel.id) 
        #user_message = str(message.content) 
        if(str(message.channel.id) == '1208463345057800202'):
            if message.content.lower() in ("emby", "jellyfin", "plex"):
                add_to_waiting_list = False
                if message.content.lower() == "jellyfin" and jellyfin_configured:
                    count = db.count_jellyfin()
                    if jellyfin_userlimit > 0:
                        if db.count_jellyfin() >= jellyfin_userlimit:
                            db.save_waiting(message.author.id, message.content.lower())
                            add_to_waiting_list = True
                           
                        else:
                            role = discord.utils.get(message.guild.roles, name="jelly")
                            if role:
                                # Adaugă rolul utilizatorului
                                await message.author.add_roles(role)
                            else:
                                await message.channel.send("Role not found!")
                            
                elif message.content.lower() == "emby" and emby_configured:
                    count = db.count_emby()
                    if jellyfin_userlimit > 0:
                        if db.count_emby() >= emby_userlimit:
                            db.save_waiting(message.author.id, message.content.lower())
                            add_to_waiting_list = True
                           
                        else:
                            role = discord.utils.get(message.guild.roles, name="emby")
                            if role:
                                # Adaugă rolul utilizatorului
                                await message.author.add_roles(role)
                            else:
                                await message.channel.send("Role not found!")

                            
                elif message.content.lower() == "plex" and plex_configured:
                    count = db.count_plex()
                    if plex_userlimit > 0:
                        if db.count_plex() >= plex_userlimit:
                            db.save_waiting(message.author.id, message.content.lower())
                            add_to_waiting_list = True
                        else:
                            role = discord.utils.get(message.guild.roles, name="plexy")
                            if role:
                                # Adaugă rolul utilizatorului
                                await message.author.add_roles(role)
                            else:
                                await message.channel.send("Role not found!")

                if add_to_waiting_list:
                    db.save_waiting(message.author.id, message.content.lower())
                    place = db.get_waiting_place(message.author.id)
                    if place == 1:
                        await embedinfo(message.author,"You are number {} on the waiting list! When your turn comes you will get an invite in DM by a bot, and you will have 24 hours to respond or the invite will expire. You can always check your position using the !spot command.".format(place))
                    elif place > 1 and place < 4:
                        await embedinfo(message.author,"You are on the {}rd place on the waiting list! When your turn comes you will get an invite in DM by a bot, and you will have 24 hours to respond or the invite will expire. You can always check your position using the !spot command.".format(place))
                    else:
                        await embedinfo(message.author,"You are on the {}th place on the waiting list! When your turn comes you will get an invite in DM by a bot, and you will have 24 hours to respond or the invite will expire. You can always check your position using the !spot command.".format(place))
                        #await message.author.send("You're name was added to the waiting list. You are on the {}th place on the list!".format(place))  


        #we make a public command
        if message.content.lower() == "!spot":
            place = db.get_waiting_place(message.author.id)
            if place == 1:
                await embedinfo(message.author,"You are number {} on the waiting list!".format(place))
            elif place > 1 and place < 4:
                await embedinfo(message.author,"You are on the {}rd place on the waiting list!".format(place))
            else:
                await embedinfo(message.author,"You are on the {}th place on the waiting list!".format(place))           

        #if message.content.lower() == "emby":
        #    await message.channel.send(f"{message.author.mention}, Pong!")
        #    #db.save_waiting(str(after.id), email, 'emby')


    @app_commands.checks.has_permissions(administrator=True)
    @plex_commands.command(name="invite", description="Invite a user to Plex")
    async def plexinvite(self, interaction: discord.Interaction, email: str):
        await self.addtoplex(email, interaction.response)
    
    @app_commands.checks.has_permissions(administrator=True)
    @plex_commands.command(name="remove", description="Remove a user from Plex")
    async def plexremove(self, interaction: discord.Interaction, email: str):
        await self.removefromplex(email, interaction.response)
    
    @app_commands.checks.has_permissions(administrator=True)
    @jellyfin_commands.command(name="invite", description="Invite a user to Jellyfin")
    async def jellyfininvite(self, interaction: discord.Interaction, username: str):
        password = jelly.generate_password(16)
        if await self.addtojellyfin(username, password, interaction.response):
            await embedcustom(interaction.response, "Jellyfin user created!", {'Username': username, 'Password': f"||{password}||"})

    @app_commands.checks.has_permissions(administrator=True)
    @jellyfin_commands.command(name="remove", description="Remove a user from Jellyfin")
    async def jellyfinremove(self, interaction: discord.Interaction, username: str):
        await self.removefromjellyfin(username, interaction.response)

    @app_commands.checks.has_permissions(administrator=True)
    @jellyfin_commands.command(name="cleanup", description="Run cleanup for jellyfin")
    async def jellycleanup(self, interaction: discord.Interaction, days: int):
        await self.cleanupjellyfin(interaction, days)
        await embedcustom(interaction.response, "Cleanup Done", {})

    @app_commands.checks.has_permissions(administrator=True)
    @emby_commands.command(name="invite", description="Invite a user to Emby")
    async def embyinvite(self, interaction: discord.Interaction, username: str):
        password = emby.generate_password(16)
        if await self.addtoemby(username, password, interaction.response):
            await embedcustom(interaction.response, "Emby user created!", {'Username': username, 'Password': f"||{password}||"})

    @app_commands.checks.has_permissions(administrator=True)
    @emby_commands.command(name="remove", description="Remove a user from Emby")
    async def embyremove(self, interaction: discord.Interaction, username: str):
        await self.removefromemby(username, interaction.response)

    @app_commands.checks.has_permissions(administrator=True)
    @emby_commands.command(name="cleanup", description="Run cleanup for emby")
    async def embycleanup(self, interaction: discord.Interaction, days: int):
        await self.cleanupemby(interaction, days)
        await embedcustom(interaction.response, "Cleanup Done", {})
    
    @app_commands.checks.has_permissions(administrator=True)
    @butlerr_commands.command(name="dbadd", description="Add a user to the Butlerr database")
    async def dbadd(self, interaction: discord.Interaction, member: discord.Member, email: str = "", jellyfin_username: str = "", emby_username: str = ""):
        email = email.strip()
        jellyfin_username = jellyfin_username.strip()
        
        # Check email if provided
        if email and not plexhelper.verifyemail(email):
            await embederror(interaction.response, "Invalid email.")
            return

        try:
            db.save_user_all(str(member.id), email, jellyfin_username, emby_username)
            await embedinfo(interaction.response,'User was added to the database.')
        except Exception as e:
            await embedinfo(interaction.response, 'There was an error adding this user to database. Check Butlerr logs for more info')
            print(e)

    @app_commands.checks.has_permissions(administrator=True)
    @butlerr_commands.command(name="dbls", description="View Butlerr database")
    async def dbls(self, interaction: discord.Interaction):

        embed = discord.Embed(title='Butlerr Database.')
        all = db.read_all()
        table = texttable.Texttable()
        table.set_cols_dtype(["t", "t", "t", "t", "t"])
        table.set_cols_align(["c", "c", "c", "c", "c"])
        header = ("#", "Name", "Email", "Jellyfin", "Emby")
        table.add_row(header)
        for index, peoples in enumerate(all):
            index = index + 1
            id = int(peoples[1])
            dbuser = self.bot.get_user(id)
            dbemail = peoples[2] if peoples[2] else "No Plex"
            dbjellyfin = peoples[3] if peoples[3] else "No Jellyfin"
            dbemby = peoples[4] if peoples[4] else "No Emby"
            try:
                username = dbuser.name
            except:
                username = "User Not Found."
            embed.add_field(name=f"**{index}. {username}**", value=dbemail+'\n'+dbjellyfin+'\n'+dbemby+'\n', inline=False)
            table.add_row((index, username, dbemail, dbjellyfin, dbemby))
        
        total = str(len(all))
        if(len(all)>25):
            f = open("db.txt", "w")
            f.write(table.draw())
            f.close()
            await interaction.response.send_message("Database too large! Total: {total}".format(total = total),file=discord.File('db.txt'), ephemeral=True)
        else:
            await interaction.response.send_message(embed = embed, ephemeral=True)
            
    @app_commands.checks.has_permissions(administrator=True)
    @butlerr_commands.command(name="dblw", description="View Waiting List database")
    async def dbls(self, interaction: discord.Interaction):

        embed = discord.Embed(title='Waiting List Database.')
        all = db.read_all_waiting()
        table = texttable.Texttable()
        table.set_cols_dtype(["t", "t", "t"])
        table.set_cols_align(["c", "c", "c"])
        header = ("#", "Name", "Platform")
        table.add_row(header)
        for index, peoples in enumerate(all):
            index = index + 1
            id = int(peoples[1])
            dbuser = self.bot.get_user(id)
            platform = peoples[2]
            try:
                username = dbuser.name
            except:
                username = "User Not Found."
            embed.add_field(name=f"**{index}. {username}**", value=platform+'\n', inline=False)
            table.add_row((index, username, platform))
        
        total = str(len(all))
        if(len(all)>25):
            f = open("waiting.txt", "w")
            f.write(table.draw())
            f.close()
            await interaction.response.send_message("Database too large! Total: {total}".format(total = total),file=discord.File('waiting.txt'), ephemeral=True)
        else:
            await interaction.response.send_message(embed = embed, ephemeral=True)            
        
            
    @app_commands.checks.has_permissions(administrator=True)
    @butlerr_commands.command(name="dbrm", description="Remove user from Butlerr database")
    async def dbrm(self, interaction: discord.Interaction, position: int):
        embed = discord.Embed(title='Butlerr Database.')
        all = db.read_all()
        for index, peoples in enumerate(all):
            index = index + 1
            id = int(peoples[1])
            dbuser = self.bot.get_user(id)
            dbemail = peoples[2] if peoples[2] else "No Plex"
            dbjellyfin = peoples[3] if peoples[3] else "No Jellyfin"
            dbemby = peoples[4] if peoples[4] else "No Emby"
            try:
                username = dbuser.name
            except:
                username = "User Not Found."
            embed.add_field(name=f"**{index}. {username}**", value=dbemail+'\n'+dbjellyfin+'\n'+dbemby+'\n', inline=False)

        try:
            position = int(position) - 1
            id = all[position][1]
            discord_user = await self.bot.fetch_user(id)
            username = discord_user.name
            deleted = db.delete_user(id)
            if deleted:
                print("Removed {} from db".format(username))
                await embedinfo(interaction.response,"Removed {} from db".format(username))
            else:
                await embederror(interaction.response,"Cannot remove this user from db.")
        except Exception as e:
            print(e)
        

async def setup(bot):
    await bot.add_cog(app(bot)) 
    

