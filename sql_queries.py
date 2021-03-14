import configparser


# CONFIG
config = configparser.ConfigParser()
config.read("dwh.cfg")

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create = """
    CREATE TABLE IF NOT EXISTS staging_events(
        artist TEXT,
        auth TEXT,
        firstName TEXT,
        gender TEXT,
        ItemInSession INT,
        lastName TEXT,
        length FLOAT,
        level TEXT,
        location TEXT,
        method TEXT,
        page TEXT,
        registration TEXT,
        sessionId INT,
        song TEXT,
        status INT,
        ts BIGINT, 
        userAgent TEXT, 
        userId INT
    )
"""

staging_songs_table_create = """
    CREATE TABLE IF NOT EXISTS staging_songs(
        song_id TEXT PRIMARY KEY,
        artist_id TEXT,
        artist_latitude FLOAT,
        artist_longitude FLOAT,
        artist_location TEXT,
        artist_name VARCHAR(255),
        duration FLOAT,
        num_songs INT,
        title TEXT,
        year INT
    )
"""

songplay_table_create = """
    CREATE TABLE IF NOT EXISTS songplays(
        songplay_id INT IDENTITY(0,1) PRIMARY KEY,
        start_time TIMESTAMP NOT NULL,
        user_id INT NOT NULL,
        level VARCHAR,
        song_id VARCHAR,
        artist_id VARCHAR,
        session_id INT,
        location VARCHAR,
        user_agent VARCHAR
    )
"""

user_table_create = """
    CREATE TABLE IF NOT EXISTS users(
        user_id VARCHAR PRIMARY KEY NOT NULL,
        first_name VARCHAR,
        last_name VARCHAR,
        gender VARCHAR,
        level VARCHAR
    )
"""

song_table_create = """
    CREATE TABLE IF NOT EXISTS songs(
        song_id VARCHAR PRIMARY KEY NOT NULL,
        title VARCHAR NOT NULL,
        artist_id VARCHAR NOT NULL,
        year INT,
        duration FLOAT
    )
"""

artist_table_create = """
    CREATE TABLE IF NOT EXISTS artists(
        artist_id VARCHAR PRIMARY KEY NOT NULL,
        name VARCHAR,
        location VARCHAR,
        latitude VARCHAR,
        longitude VARCHAR
    )
"""

time_table_create = """
    CREATE TABLE IF NOT EXISTS time(
        start_time TIME PRIMARY KEY NOT NULL,
        hour INT,
        day INT,
        week INT,
        month INT,
        year INT,
        weekday INT
    )
"""

# STAGING TABLES

staging_events_copy = f"""
    copy staging_events
    from {config['S3']['LOG_DATA']}
    iam_role {config['IAM_ROLE']['ARN']}
    compupdate off region 'us-west-2'
    json {config['S3']['LOG_JSONPATH']}
    EMPTYASNULL
    BLANKSASNULL
"""

staging_songs_copy = f"""
    copy staging_songs
    from {config['S3']['SONG_DATA']}
    iam_role {config['IAM_ROLE']['ARN']}
    compupdate off region 'us-west-2'
    json 'auto'
    TRUNCATECOLUMNS
    EMPTYASNULL
    BLANKSASNULL
"""

# FINAL TABLES

# start_time is taken from https://knowledge.udacity.com/questions/154533. Thank you Survesh C :)
songplay_table_insert = """
    INSERT INTO songplays(
        start_time,
        user_id,
        level,
        song_id,
        artist_id,
        session_id,
        location,
        user_agent
    )
    SELECT
        timestamp 'epoch' + e.ts/1000*interval '1 second' AS start_time,
        e.userId AS user_id,
        e.level,
        s.song_id,
        s.artist_id,
        e.sessionId AS session_id,
        e.location,
        e.userAgent AS user_agent
    FROM staging_events AS e
    JOIN staging_songs AS s
        ON e.artist = s.artist_name
        AND e.song = s.title
        AND e.length = s.duration
    WHERE e.page = 'NextSong'
"""

user_table_insert = """
    INSERT INTO users
    SELECT
        userId AS user_id,
        firstName AS first_name,
        lastName AS last_name,
        gender,
        level
    FROM staging_events
    WHERE userId IS NOT NULL
"""

song_table_insert = """
    INSERT INTO songs
    SELECT
        song_id,
        title,
        artist_id,
        year,
        duration
    FROM staging_songs
"""

artist_table_insert = """
    INSERT INTO artists
    SELECT
        artist_id,
        artist_name AS name,
        artist_location AS location,
        artist_latitude AS latitude,
        artist_longitude AS longitude
    FROM staging_songs
"""

# start_time is taken from https://knowledge.udacity.com/questions/154533. Thank you Survesh C :)
time_table_insert = """
    INSERT INTO time
    SELECT
        timestamp 'epoch' + ts/1000*interval '1 second' AS start_time,
        DATE_PART(HOUR, start_time) AS hour,
        DATE_PART(DAY, start_time) AS day,
        DATE_PART(WEEK, start_time) AS week,
        DATE_PART(MONTH, start_time) AS month,
        DATE_PART(YEAR, start_time) AS year,
        DATE_PART(WEEKDAY, start_time) AS weekday
    FROM staging_events
"""

# QUERY LISTS

create_table_queries = [
    staging_events_table_create,
    staging_songs_table_create,
    songplay_table_create,
    user_table_create,
    song_table_create,
    artist_table_create,
    time_table_create,
]

drop_table_queries = [
    staging_events_table_drop,
    staging_songs_table_drop,
    songplay_table_drop,
    user_table_drop,
    song_table_drop,
    artist_table_drop,
    time_table_drop,
]

copy_table_queries = [staging_events_copy, staging_songs_copy]

insert_table_queries = [
    songplay_table_insert,
    user_table_insert,
    song_table_insert,
    artist_table_insert,
    time_table_insert,
]
