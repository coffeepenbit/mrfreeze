import discord
from discord.ext import commands
import collections, random, signal, re
import traceback, sys, asyncio

# Importing commands from ./botfunctions
from botfunctions import *


class MrFreezeClient(commands.Bot):
    # This modification of commands.Bot is based on the following example:
    # https://github.com/Rapptz/discord.py/blob/rewrite/examples/background_task.py
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Background task manager
        self.bg_task = self.loop.create_task(self.bg_task_manager())

    async def on_ready(self):
        # Escape sequences:
        # 0 reset, 1 bold, 36 cyan
        print('\033[36;1m' + 'We have logged in as {0.user}'.format(bot))
        print('\033[0;36m' + 'User name:           \033[1m{}'.format(bot.user.name))
        print('\033[0;36m' + 'User ID:             \033[1m{}'.format(bot.user.id))
        print('\033[0;36m' + 'Number of servers:   \033[1m{}'.format(len(bot.guilds)))
        print('\033[0;36m' + 'Number of users:     \033[1m{}'.format(len(bot.users)))
        print('\033[0m')

        # Making sure that the userdb exists.
        userdb.create()

        # Creating dict of all pins in channels in the guilds.
        # pinsDict is first set to None so we know that it's not done
        # if there's a pin made while the bot is loading.
        global pinsDict
        pinsDict = None
        pinsDict = await pinlists.create_dict(bot.guilds)

        # Greetings message for all the servers now that all is setup.
        # This has been disabled due to being annoying as fuck.
        # Replaced with writing a single line to the terminal instead.
        print('\033[37;1m\n' + 'READY WHEN YOU ARE CAP\'N!' + '\033[0m')
        #
        # for i in bot.guilds:
        #     try:
        #         bot_trash = discord.utils.get(i.channels, name='bot-trash')
        #         await bot_trash.send(':wave: ' + native.mrfreeze())
        #     except:
        #         print ('ERROR: No channel bot-trash in ' + str(i.name) + '. Can\'t greet them.')

        # Set activity to "Listening to your commands"
        await bot.change_presence(status=None, activity=
            discord.Activity(name='your commands...', type=discord.ActivityType.listening))


    async def bg_task_manager(self):
        await self.wait_until_ready()

        channel = self.get_channel(466241532458958850)
        while not self.is_closed():
            await asyncio.sleep(15)

            # First we fix mutes.
            mute_status = userdb.list_mute()
            for guild in self.guilds:
                unmuted = list()
                not_unmuted = list()

                # Check that there's an antarctica role, otherwise set it to None.
                try:
                    antarctica_role = discord.utils.get(guild.roles, name='Antarctica')
                except:
                    antarctica_role = None

                # Check that there's a bot-trash channel, otherwise set it to None.
                try:
                    bot_trash = discord.utils.get(guild.channels, name='bot-trash')
                except:
                    bot_trash = None

                # Go through all the entries in mute_status.
                for entry in mute_status:
                    if entry['server'] == guild.id:
                        user = discord.utils.get(guild.members, id=entry['user'])

                        # If the user doesn't have the antarctica role (i.e. manually deleted)
                        # we'll just delete the database entry silently.
                        if antarctica_role and not (antarctica_role in user.roles):
                            userdb.fix_mute(user, delete=True)

                        # If the user does have the antarctica role and entry['time'] is
                        # true, we will try to delete the role and add them to the list
                        # of successfully unmuted people. Then we'll delete the db entry.
                        elif antarctica_role and entry['time']:
                            try:
                                await user.remove_roles(antarctica_role, reason='Time, the sentence is served.')
                                unmuted.append(user)
                                userdb.fix_mute(user, delete=True)
                            except:
                                pass
                                # not_unmuted.append(user)

                if (len(unmuted) + len(not_unmuted)) > 0:
                    unmuted_mentions = native.mentions_list(unmuted)

                    # Currently these actually aren't used because I'm not sure where to put them.
                    # not_unmuted_mentions = native.mentions_list(not_unmuted)

                    if bot_trash != None:
                        replystr = 'It\'s with great regreat that I need to inform y\'all that the exile of %s has come to an end.'
                        await bot_trash.send(replystr % (unmuted_mentions,))
                    else:
                        print ('There is no bot-trash.')



# Starting the bot, then removing help command
# because we're going to implement our own help.
bot = MrFreezeClient(command_prefix='!')

# Cogs starting with cmd contains only one command,
# Cogs starting with cmds has multiple commands sharing some common trait.
load_cogs = [ 'cogs.maintenance',    # Owner-only commands
              'cogs.moderation',     # Mod-only commands.
              'cogs.about',          # !dummies, !readme, !source
              'cogs.quotes',         # !quote
              'cogs.user_cmds',      # Various smaller commands: !rules, !vote, !mrfreeze
              'cogs.inkcyclopedia',  # Listen for inkzzz.

              # Silent(ish) bot functions.
              'cogs.error_handling',     # How the bot deals with errors.
              'cogs.message_handling',   # How the bot deals with messages.
              'cogs.departure_handling', # How the bot deals with departures
              ]

# Here's where the actual loading of the cogs go.
if __name__ == '__main__':
    for cog in load_cogs:
        try:
            bot.load_extension(cog)
        except Exception as e:
            print(f'Failed to load extension {cog}.', file=sys.stderr)
            traceback.print_exc()


# A message was pinned.
@bot.event
async def on_guild_channel_pins_update(channel, last_pin):
    global pinsDict

    # Unfortunately we have to cast an empty return
    # if the dict isn't finished yet.
    if pinsDict == None:
        print ('The PinsDict isn\'t finished yet!')
        return

    # The channel might be new, if so we need to create an entry for it.
    try:
        pinsDict[channel.guild.id][channel.id]
    except KeyError:
        pinsDict[channel.guild.id][channel.id] = 0

    # For comparisson between the two. These numbers will be
    # used to determine whether a pin was added or removed.
    channel_pins = await channel.pins()
    old_pins = pinsDict[channel.guild.id][channel.id]
    new_pins = len(channel_pins)

    # Was a new pin added?
    # If a pin was added when the bot was starting up, this won't work.
    # But it will work the next time as the pinsDict is updated.
    was_added = False
    if new_pins > old_pins:
        was_added = True

    # Updating the list of pins.
    pinsDict[channel.guild.id][channel.id] = new_pins

    if was_added:
        message = channel_pins[0]
        pinned_message = discord.Embed(description = message.content, color=0x00dee9)
        pinned_message.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)

        # Attaching first attachment of the post, if there are any.
        if message.attachments:
            pinned_message.set_image(url=message.attachments[0].url)

        channel_history = message.channel.history(limit=10)
        for i in range(10):
            sys_msg = await channel_history.next()
            if isinstance(sys_msg.type, type(discord.MessageType.pins_add)):
                author = sys_msg.author.mention # This is the person who pinned the message.
                await sys_msg.delete()
                break # No need to look further.

        replystr = 'The following message was just pinned by %s:\n'
        await channel.send(replystr % (author), embed=pinned_message)



### Program ends here
# Client.run with the bots token
# Place your token in a file called 'token'
# Put the file in the same directory as the bot.
try:
    token = open('token', 'r').read().strip()
    bot.run(token, bot=True, reconnect=True)
except:
    print ('\nERROR: BOT TOKEN MISSING\n' +
           'Please put your bot\'s token in a separate text file called \'token\'.\n' +
           'This file should be located in the same directory as the bot files.\n')
    sys.exit(0)

# Graceful exit
def signal_handler(sig, frame):
        print('\n\nYou pressed Ctrl+C!\nI will now do like the tree, and get out of here.')
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.pause()
