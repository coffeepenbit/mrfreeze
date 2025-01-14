# MrFreeze 2.0
The next big thing, this is gonna be huuuuge! At time of writing, most things I want in place are already in place. However some early design choices, it has dawned on me, are kind of shitty and needs fixing. The features and tasks that made this cut are such that I feel they need adressing before release. The criterias for this can be any of the following:
* The feature is trivial to implement or is at least low effort compared to potential gains.
* The feature is absolutely essential to the release and not including it will cause problems down the line.

The reason why 2.0 and 2.1+ are split is that this project has been in the works for so long it's becoming a meme. Version 1 has been hotfixed multiple times during development and really needs to be retired ASAP. 

## Improvements
### Remake the !region command
Status: work not started

The !region command was deleted because it was terribly written and needs to be redone.

### Inkcyclopedia
Status: work in progress

Semi-automatic ink lookup based on klundtasaur's inkcyclopedia:
https://www.reddit.com/r/fountainpens/comments/5egjsa/klundtasaurs_inkcyclopedia_for_rfountainpens/

### !move <ID> #channel
Status: work not started

Move one or more posts to a specified channel
* Use post IDs to specify which posts.
* Use a quote-like embed for reposting.

### !disable <ID>
Status: work not started

Owner-only command. Disable a certain MrFreeze in one server (enabling multiple concurrent versions to be present).
This is useful because MrFreeze can pull info from multiple servers, enabling *some* support for certain nitro emojis and the like.

## Bug testing
All these features and improvements will need to be tested once implemented.

Some points not to forget. Check that...
**Temp conversion**
* ...Yoss' helldog spawns for sufficiently high temperatures.

**Region**
* ...blacklisted users can't and non-blacklisted users can change regions.
* ...mods can and non-mods can't edit the blacklist.
* ...listing of regions work.
* ...mods can and non-mods can't produce a list of blacklisted people.

**Mute/banish etc**
* ...banishing a single/multiple user works.
* ...users who are manually unmuted don't get prolonged mutes when remuted.

**Ban**
* ...banning single/multiple users via mention works.
* ...banning single/multiple users via user ID works.
* ...banning multiple users via mention and user ID (mixed) works.
* ...unbanning single/multiple users via name#discriminator works.
* ...unbanning single/multiple users via user ID works.
* ...unbanning multiple users via mention and name#discriminator (mixer) works.
* ...listing banned users works.
* ...errors report correctly.

**Kick**
* ...kicking single/multiple users via mention works.
* ...kicking single/multiple users via user ID works.
* ...kicking multiple users via mention and user ID (mixed) works.
* ...errors report correctly.

**Vote**
* ...number emoji work.
* ...animated emoji work.
* ...flags, letters and number emojis work.
* ...skin colour emoji work.
* ...out of server emoji work as long as Freeze is in that server.

**Say**
* ...out of server emoji work.
* ...out of server emoji MrFreeze doesn't have access to should stop the operation.
* ...animated emoji work.
* ...conversion of user ID to user mention works.
* ...copying of existing user IDs work.

----------

# MrFreeze 2.1+
This is the post-release plans for MrFreeze that will likely not make it in for version 2.0 (but might)

## New features
Features that will (probably) not be present in MF 2.0.

### !settings
Status: work not started.

A database saving a certain number of settings keys that can be modified without going into the bot source code. The disable feature planned for 2.0 should be one of those, and thus the database may be delivered earlier.

### !quotes
Status: somewhat completed, but going to need a lot of reworking.

* Make a new database for it it.
* Check that the name isn't all numbers.
* Check for double name entries, all names must be unique.
* Allow adding last post by a certain user with !quote add @username
* Merge 'read' and 'random' in cmd_quote.py.
* Some way of saving image attachments.
* Perhaps some kind of emoji-vote function which also adds quotes? React with some obscure(?) emoji, if enough people do it it becomes a quote.

### !blackjack
Status: work not started

Multiplayer game of blackjack.

### !rps (Rock, paper, scissors)
Status: work not started

Rock, paper scissors with a scoreboard.

### !dice
Status: work not started

Command for dice throws. Should be able to parse multiple dice and multiple types of dice.
