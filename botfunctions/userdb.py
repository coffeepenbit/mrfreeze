import sqlite3, discord
from sqlite3 import Error

### This file manages the userdb where we keep stuff like rps scores, mutes,
### etc. We also have a register of all channels and users which is constantly
### updated as new information is provided.

### This short function creates the connection to the database.
### It's used in almost every function so it's useful to have.
def connect_to_db():
    db_file = 'databases/user.db'
    conn = sqlite3.connect(db_file)
    return conn

### This function creates the database if it doesn't
### already exists, then closes the connection.
def create():
    conn = connect_to_db()

    ### The tables are arranged by the foreign keys they are using.
    ### 'servers' is essentially the top table.
    ###
    ### Full list of current tables:
    ### servers     (server ids and names)
    ### channels    (channel ids and names)
    ### users       (users and the nicks they use on different servers)
    ### quotes      (quote entries, duh)
    ### rps         (rock, paper, scissors)
    ### mutes       (list of people with antarctica-tag and why they have them)
    ### region_bl   (blacklist from using the region command)

    ### Server names.
    servers_tbl   = """
                    CREATE TABLE IF NOT EXISTS servers(
                        id integer PRIMARY KEY,
                        name text NOT NULL
                    );"""

    ### Channel IDs/Names.
    channels_tbl  = """
                    CREATE TABLE IF NOT EXISTS channels(
                        id integer PRIMARY KEY,
                        server integer NOT NULL,
                        name text NOT NULL,
                        FOREIGN KEY (server) REFERENCES servers (id)
                    );"""

    ### List of user IDs/Names.
    users_tbl     = """
                    CREATE TABLE IF NOT EXISTS users(
                        id integer NOT NULL,
                        server integer NOT NULL,
                        disp_name text NOT NULL,
                        name text NOT NULL,
                        avatar text NOT NULL,
                        discriminator integer NOT NULL,
                        FOREIGN KEY (server) REFERENCES servers (id),
                        CONSTRAINT server_user PRIMARY KEY (id, server)
                    );"""

    ### Quotes database.
    quotes_tbl    = """
                    CREATE TABLE IF NOT EXISTS quotes(
                        id integer PRIMARY KEY NOT NULL,
                        quoter integer NOT NULL,
                        quotee integer NOT NULL,
                        server integer NOT NULL,
                        channel integer NOT NULL,
                        date_said text NOT NULL,
                        content text NOT NULL,
                        name text,
                        FOREIGN KEY (quoter) REFERENCES users (id),
                        FOREIGN KEY (quotee) REFERENCES users (id),
                        FOREIGN KEY (server) REFERENCES servers (id),
                        FOREIGN KEY (channel) REFERENCES channels (id)
                    );"""

    ### Rock, Paper, Scissors stats.
    rps_tbl       = """
                    CREATE TABLE IF NOT EXISTS rps(
                        id integer NOT NULL,
                        server integer NOT NULL,
                        wins integer NOT NULL,
                        losses integer NOT NULL,
                        drawn integer NOT NULL,
                        FOREIGN KEY (id) REFERENCES users (id),
                        FOREIGN KEY (server) REFERENCES servers (id),
                        CONSTRAINT server_user PRIMARY KEY (id, server)
                    );"""

    ### If a user gets antarctica'd, that's registered here.
    ### A user can self-banish, in which case voluntary will be
    ### True and they're allowed to unbanish themselves as well.
    mutes_tbl     = """
                    CREATE TABLE IF NOT EXISTS mutes(
                        id integer NOT NULL,
                        server integer NOT NULL,
                        until date NOT NULL,
                        voluntary boolean NOT NULL,
                        FOREIGN KEY (id) REFERENCES users (id),
                        FOREIGN KEY (server) REFERENCES servers(id),
                        CONSTRAINT server_user PRIMARY KEY (id, server)
                    );"""

    ### A user can get banned from changing their region if
    ### mods detect abuse. They will then be put on this blacklist.
    region_bl_tbl = """
                    CREATE TABLE IF NOT EXISTS region_bl(
                        id integer NOT NULL,
                        server integer NOT NULL,
                        FOREIGN KEY (id) REFERENCES users (id),
                        FOREIGN KEY (server) REFERENCES servers (id),
                        CONSTRAINT server_user PRIMARY KEY (id, server)
                    );"""

    ### Here we'll create all the tables.
    with conn:
        try:
            c = conn.cursor()
            c.execute(servers_tbl)
            c.execute(channels_tbl)
            c.execute(users_tbl)
            c.execute(quotes_tbl)
            c.execute(rps_tbl)
            c.execute(mutes_tbl)
            c.execute(region_bl_tbl)

        ### If an error occurs, it will be reported to the terminal with the
        ### error printed.
        except Error as e:
            print ('Unable to create user.db quotes table\n' + str(e))

### This function creates/updates the db entry for a certain server/guild.
def fix_server(guild):
    conn = connect_to_db()
    id = guild.id
    name = guild.name

    with conn:
        c = conn.cursor()
        q_server = ''' SELECT * FROM servers WHERE id = ? '''
        c.execute(q_server, (id,))
        fetch = c.fetchall()
        server_exists = True
        if len(fetch) == 0:
            server_exists = False

        # If the server exists, we'll update it.
        if server_exists:
            sql = '''
                  UPDATE servers
                  SET name = ?
                  WHERE id = ?
                  '''

        # If the server doesn't exist, we'll create it.
        if not server_exists:
            sql = '''
                  INSERT INTO servers (name, id)
                  VALUES (?,?)
                  '''

        c.execute(sql, (name, id))

### This function creates/updates the db entry for a certain channel.
def fix_channel(channel):
    conn = connect_to_db()
    channel_id = channel.id
    server_id = channel.guild.id
    name = channel.name

    fix_server(channel.guild)

    with conn:
        c = conn.cursor()
        q_channel = ''' SELECT * FROM channels WHERE id = ? '''
        c.execute(q_channel, (channel_id,))
        fetch = c.fetchall()
        channel_exists = True
        if len(fetch) == 0:
            channel_exists = False

        # If the channel exists, we'll update it.
        if channel_exists:
            sql = '''
                  UPDATE channels
                  SET name = ?,
                      server = ?
                  WHERE id = ?
                  '''

        # If the channel doesn't exist, we'll create it.
        if not channel_exists:
            sql = '''
                  INSERT INTO channels (name, server, id)
                  VALUES (?,?,?)
                  '''

        c.execute(sql, (name, server_id, channel_id))

### This function creates/updates the db entry for a certain user in a certain server.
def fix_user(ctx):
    conn = connect_to_db()

    user_id = ctx.author.id
    server_id = ctx.guild.id
    discriminator = ctx.author.discriminator
    user_name = ctx.author.name
    user_disp_name = ctx.author.display_name
    avatar = ctx.author.avatar_url

    fix_server(ctx.guild)

    with conn:
        c = conn.cursor()
        q_user = ''' SELECT * FROM users WHERE id=? AND server=? '''
        c.execute(q_user, (user_id,server_id))
        fetch = c.fetchall()
        user_exists = True
        if len(fetch) == 0:
            user_exists = False

        # If the user exists, we'll update it.
        # Discriminator can change if they have nitro for example.
        if user_exists:
            sql = '''
                  UPDATE users
                  SET disp_name = ?,
                      discriminator = ?,
                      name = ?,
                      avatar = ?
                  WHERE id = ? AND server = ?
                  '''

        if not user_exists:
            sql = '''
                  INSERT INTO users (disp_name, discriminator, name, avatar, id, server)
                  VALUES (?,?,?,?,?,?)
                  '''

        try:
            c.execute(sql, (user_disp_name, discriminator, user_name, avatar, user_id, server_id))
        except Error as e:
            print(e)

### This function creates/updates the db entry for a certain users mute status in a certain server.
def fix_mute(user, duration, is_delete):
    conn = connect_to_db()

### This function creates/updates the db entry for a certain user in a certain server.
def fix_rps(user):
    conn = connect_to_db()
##########
### Quote-related commands.
##########

### This function returns an embed with the requested quote
### which can then be posted to the chat and looks beautiful.
def quote_embed(db_entry):
    conn = connect_to_db()

    ### [ ( db_entry ) ] -> ( db_entry )
    db_entry   = db_entry[0]
    ### Unpacking (db_entry) into some variables we'll be using.
    id         = str(db_entry[0])
    quoter_id  = db_entry[1]
    quotee_id  = db_entry[2]
    server_id  = db_entry[3]
    channel_id = db_entry[4]
    date_said  = db_entry[5]
    content    = db_entry[6]
    name       = db_entry[7]

    ### Using the quoter and quotee information, we can
    ### Retrieve some additional information from the users db
    with conn:
        c = conn.cursor()
        u_sql = ''' SELECT * FROM users WHERE id = ? AND server = ? '''
        c.execute(u_sql, (quoter_id, server_id))
        quoter_tuple = c.fetchall()[0]
        c.execute(u_sql, (quotee_id, server_id))
        quotee_tuple = c.fetchall()[0]

    ### The following is the information we'll be getting:
    ### DNAME    = display_name
    ### HASHNAME = NAME#DISCRIMINATOR (eg. TerminalNode#5986)
    ### AVATAR   = URLs for the quoter/quotee avatars.
    quoter_dname = quoter_tuple[2]
    quotee_dname = quotee_tuple[2]
    quoter_hashname = (quoter_tuple[3] + '#' + str(quoter_tuple[5]))
    quotee_hashname = (quotee_tuple[3] + '#' + str(quotee_tuple[5]))
    quoter_avatar = quoter_tuple[4]
    quotee_avatar = quotee_tuple[4]

    embed = discord.Embed(color=0x00dee9)
    # embed.set_author(name = quotee_dname)
    embed.set_thumbnail(url=quotee_avatar)
    if name == None:
        embed.add_field(name = (quotee_dname + ', ' + date_said), value = ('%s\n\n(**ID:** %s)' % (content, id)))
    else:
        embed.add_field(name = (quotee_dname + ', ' + date_said), value = ('%s\n\n(**ID:** %s)\n(**Name:** %s)' % (content, id, name)))
    embed.set_footer(icon_url = quoter_avatar, text=("Added by %s" % (quoter_dname)))

    return embed

### This function creates a new quote entry.
### The input required is ctx from !quote-command
### and the message quoted (which will be retrived
### from a provided ID via !quote, not here).
def crt_quote(ctx, quote):
    conn = connect_to_db()
    id        = quote.id
    quoter    = ctx.author.id
    quotee    = quote.author.id
    server    = quote.guild.id
    channel   = quote.channel.id
    date_said = '{:%Y-%m-%d}'.format(quote.created_at)
    content   = quote.content

    fix_user(ctx)
    fix_user(quote)
    fix_channel(quote.channel)

    with conn:
        c = conn.cursor()

        q_quote = ''' SELECT * FROM quotes WHERE id = ? '''
        c.execute(q_quote, (id,))
        fetch = c.fetchall()
        quote_exists = True
        if len(fetch) == 0:
            quote_exists = False

        if not quote_exists:
            sql =   '''
                    INSERT INTO quotes (id, quoter, quotee, server, channel, date_said, content)
                    VALUES (?,?,?,?,?,?,?)
                    '''
            try:
                c.execute(sql, (id, quoter, quotee, server, channel, date_said, content))
                c.execute('SELECT * FROM quotes WHERE id = ?', (c.lastrowid,))
                new_entry = c.fetchall()
            except Error as e:
                print(e)

    # Now we're ready for out return values
    if not quote_exists:
        return quote_embed(new_entry)
    else:
        return None

### This function assigns the optional field 'name' to a given quote.
def name_quote(id, name):
    conn = connect_to_db()

    with conn:
        c = conn.cursor()
        q_quote = ''' SELECT * FROM quotes WHERE id = ? '''
        c.execute(q_quote, (id,))
        fetch = c.fetchall()

        # The following variables are necessary
        # to know what went wrong, if anything.
        found_quote = False
        updated_quote = False
        old_name = None
        if len(fetch) != 0:
            found_quote = True
            old_name = fetch[0][7]

            sql =   '''
                    UPDATE quotes
                    SET name = ?
                    WHERE id = ?
                    '''

            if old_name != name:
                try:
                    c.execute(sql, (name, id))
                    updated_quote = True
                except Error as e:
                    print (e)

    return (found_quote, updated_quote, old_name)

### This function retrieves a quote based on an ID or name.
### Quote is then sent to the quote_embed()-function (if
### a quote is found) and returns the resulting embed.
def get_quote_id(id):
    conn = connect_to_db()

    with conn:
        c = conn.cursor()
        q_quote = ''' SELECT * FROM quotes WHERE id = ? OR name = ? '''
        fetch = list()
        try:
            c.execute(q_quote, (id,id))
            fetch = c.fetchall()
        except Error as e:
            print (e)
        if len(fetch) != 0:
            return quote_embed(fetch)
        else:
            return None

### This function retrieves a random quote from the dictionary.
### Can optionally look for a random quote by a certain user.
### Quote is then sent to quote_embed()-function (if a quote
### is found) and returns the resulting embed.
def get_quote_rnd(id, user):
    conn = connect_to_db()
