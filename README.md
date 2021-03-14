# udacity-nd027-data_warehouse
My Submission of Project: Data Warehouse

## Summary

The goal of this project is to define fact and dimension tables for a star schema for a particular analytic focus, and write an ETL pipeline that transfers data from sets in Amazon S3 into five tables in Amazon Redshift.

### Raw Data

The raw data is in Amazon S3 and contains

1. \*song_data\*.jsons ('artist_id', 'artist_latitude', 'artist_location',
       'artist_longitude', 'artist_name', 'duration', 'num_songs',
       'song_id', 'title', 'year') - a subset of real data from the [Million Song Dataset](http://millionsongdataset.com/).
2. \*log_data\*.jsons ('artist', 'auth', 'firstName', 'gender', 'itemInSession',
       'lastName', 'length', 'level', 'location', 'method', 'page',
       'registration', 'sessionId', 'song', 'status', 'ts', 'userAgent',
       'userId') - [simulated](https://github.com/Interana/eventsim) activity logs from a music streaming app based on specified configurations.

### Create Redshift Cluster an and IAM Role that makes Redshift able to access S3 bucket (ReadOnly)

Make sure you have an AWS secret and access key. Then edit the `dwh.cfg` file and replace the following `XXX` entries (like in Exercise 2):

```
[AWS]
KEY=YOUR_AWS_KEY
SECRET=YOUR_AWS_SECRET

[DWH] 
DWH_CLUSTER_TYPE=multi-node
DWH_NUM_NODES=4
DWH_NODE_TYPE=dc2.large

DWH_IAM_ROLE_NAME=XXX
DWH_CLUSTER_IDENTIFIER=XXX
DWH_DB=XXX
DWH_DB_USER=XXX
DWH_DB_PASSWORD=XXX
DWH_PORT=XXX
```

Afterward run all blocks in `create_aws_infrastructure.ipynb` until `Step 2.2`. Note the values for `DWH_ENDPOINT` and `DWH_ROLE_ARN`.

### Final edits in dwh.cfg

Replace the following `XXX`s in `dwh.cfg`

```
[CLUSTER]
HOST=XXX  # Cluster Endpoint
DB_NAME=XXX  # same as DWH_DB
DB_USER=XXX  # same as DWH_DB_USER
DB_PASSWORD=XXX  # same as DWH_DB_PASSWORD
DB_PORT=XXX  # same as DWH_PORT

[IAM_ROLE]
ARN=XXX  # Role ARN
```

### Define Fact and Dimension Tables for a Star Schema in Redshift

Run `python3 create_tables.py` in a terminal to create the Database containing:

#### A Fact Table

1. songplays (songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent) - records in log data associated with song plays

#### Four Dimension Tables

1. users (user_id, first_name, last_name, gender, level) - users in the app
1. songs (song_id, title, artist_id, year, duration) - songs in music database
1. artists (artist_id, name, location, latitude, longitude) - artists in music database
1. time (start_time, hour, day, week, month, year, weekday) - timestamps of records in songplays broken down into specific units
        
### Run ETL Pipeline

Fill the five star schema tables with data from the raw sets from S3 by running `python3 etl.py` in a terminal.

### Delete your redshift cluster

Delete your redshift cluster by running the Code Blocks in `create_aws_infrastructure.ipynb` `Step 5` when finished.

## 1. Discuss the Purpose of this Database in the Context of the Startup, Sparkify, and their Analytical Goals.

The startup Sparkify is an audio streaming services provider. "As a freemium service, basic features are free with advertisements and limited control, while additional features, such as offline listening and commercial-free listening, are offered via paid subscriptions. Users can search for music based on artist, album, or genre, and can create, edit, and share playlists." (Taken from [https://en.wikipedia.org/wiki/Spotify](https://en.wikipedia.org/wiki/Spotify))

So the commercial goal is to get as many users as long as possible to use sparkify. In order to achieve this, sparkify must meet/exceed the users expectations and satisfy them. Ways of doing this are
- providing a huge database of artists and songs
- a fancy and usable (Browser, Mobile-App, Desktop-App) GUI
- a good search engine (Analytical goal!)
- a good recommendation system (Analytical goal!)

This database serves the needs of a good recommendation system: The favourite songs of user `X` can easily be extracted of our fact_table given their number_of_plays (by `X`). So we can put users in clusters based on their favourite songs. And if `X` likes the songs `a`, `b`, & `c` and there are other Users in (one of) his cluster(-s) which likes the songs `a`, `b`, `c`, & `d` he also might like song `d`. Let's recommend this song to him. He supposably enjoys that and thus enjoys sparkify.

## 2. State and Justify your Database Schema Design and ETL pipeline.

### Database Schema Design

The denormalized fact table `songplays` provides most information sparkify needs for its basic analytical goals. Reading and aggregation is very fast and if we need additional information from the dimension tables
- `users`
- `artists`
- `songs` (missing genre here 'tho)
- `time`

the joins are very simple -> high readability.
