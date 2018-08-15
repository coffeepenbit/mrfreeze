import sqlite3
from sqlite3 import Error

# This file manages the userdb where we keep stuff like rps scores, mutes,
# etc. We also have a register of all channels and users which is constantly
# updated as new information is provided.

# This short function creates the connection to the database.
# It's used in almost every function so it's useful to have.
def connect_to_db():
    db_file = 'databases/user.db'
    conn = sqlite3.connect(db_file)
    return conn

# This function creates the database if it doesn't
# already exists, then closes the connection.
def create():
    conn = connect_to_db()

    # The tables are arranged by the foreign keys they are using.
    # 'servers' is essentially the top table. crt is short for create,
    # tbl is short for table.

    # Server names.
    crt_servers_tbl   = """   CREATE TABLE IF NOT EXISTS servers(
                        id integer PRIMARY KEY,
                        name text NOT NULL
    );"""

    # Channel IDs/Names.
    crt_channels_tbl  = """   CREATE TABLE IF NOT EXISTS channels(
                        id integer PRIMARY KEY,
                        server integer NOT NULL,
                        name text NOT NULL,
                        FOREIGN KEY (server) REFERENCES servers (id)
    );"""

    # List of user IDs/Names.
    crt_users_tbl     = """   CREATE TABLE IF NOT EXISTS users(
                        id integer NOT NULL,
                        server integer NOT NULL,
                        disp_name text NOT NULL,
                        name text NOT NULL,
                        discriminator integer NOT NULL,
                        FOREIGN KEY (server) REFERENCES servers (id),
                        CONSTRAINT server_user PRIMARY KEY (id, server)
    );"""

    # Quotes database.
    crt_quotes_tbl    = """  CREATE TABLE IF NOT EXISTS quotes(
                        id integer PRIMARY KEY NOT NULL,
                        quoter integer NOT NULL,
                        quotee integer NOT NULL,
                        server integer NOT NULL,
                        channel integer NOT NULL,
                        date_said datetime NOT NULL,
                        content text NOT NULL,
                        shortcut text,
                        FOREIGN KEY (quoter) REFERENCES users (id),
                        FOREIGN KEY (quotee) REFERENCES users (id),
                        FOREIGN KEY (server) REFERENCES servers (id),
                        FOREIGN KEY (channel) REFERENCES channels (id)
    );"""

    # Rock, Paper, Scissors stats.
    crt_rps_tbl       = """   CREATE TABLE IF NOT EXISTS rps(
                        id integer PRIMARY KEY NOT NULL,
                        wins integer NOT NULL,
                        losses integer NOT NULL,
                        drawn integer NOT NULL,
                        FOREIGN KEY (id) REFERENCES users (id)
    );"""

    # If a user gets antarctica'd, that's registered here.
    # A user can self-banish, in which case voluntary will be
    # True and they're allowed to unbanish themselves as well.
    crt_mutes_tbl     = """   CREATE TABLE IF NOT EXISTS mutes(
                        user integer NOT NULL,
                        until date NOT NULL,
                        voluntary boolean NOT NULL,
                        FOREIGN KEY (user) REFERENCES users (id)
    );"""

    # Here we'll create all the tables.
    with conn:
        try:
            c = conn.cursor()
            c.execute(crt_servers_tbl)
            c.execute(crt_channels_tbl)
            c.execute(crt_users_tbl)
            c.execute(crt_quotes_tbl)
            c.execute(crt_rps_tbl)
            c.execute(crt_mutes_tbl)

        # If an error occurs, it will be reported to the terminal with the
        # error printed.
        except Error as e:
            print ('Unable to create user.db quotes table\n' + str(e))

# Create or update server/channel/user/etc.
def fix_server(guild):
    conn = connect_to_db()
    # TODO Replace these values with guild.id and guild.name
    id = 123452
    name = 'test server'

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

def fix_channel(channel):
    conn = connect_to_db()
    # TODO Replace these values with channel.id, channel.guild.id and channel.name
    channel_id = 2345
    server_id = 12345
    name = 'test channel'

    # TODO Change 123 into channel.guild
    fix_server(123)

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


def fix_user(user):
    conn = connect_to_db()

    # TODO Change these values.
    user_id = 91522
    server_id = 2344
    discriminator = 453
    user_name = 'Terminal'
    user_disp_name = 'Terminal Noe'

    # TODO Change 123 into user.guild
    fix_server(123)

    with conn:
        c = conn.cursor()
        q_user = ''' SELECT * FROM users WHERE id = ? AND server = ? '''
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
                        name = ?
                    WHERE id = ? AND server = ?
                  '''

        if not user_exists:
            sql = '''
                  INSERT INTO users (disp_name, discriminator, name, id, server)
                  VALUES (?,?,?,?,?)
                  '''

        c.execute(sql, (user_disp_name, discriminator, user_name, user_id, server_id))


def fix_mute(user, duration, is_delete):
    conn = connect_to_db()

def fix_rps(user):
    conn = connect_to_db()

# Quote-related commands.
def crt_quote(ctx, quote):
    conn = connect_to_db()

def get_quote_id(id, name):
    conn = connect_to_db()

def get_quote_rnd(id, is_name):
    conn = connect_to_db()
