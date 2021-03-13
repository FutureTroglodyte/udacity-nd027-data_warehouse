import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries


def load_staging_tables(cur, conn):
    """Bulk inserting staging tables from s3 into Redshift"""
    for query in copy_table_queries:
        cur.execute(query)
        conn.commit()


def insert_tables(cur, conn):
    """Load into star schema in Redshift"""
    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    """
    01. Establishes connection to the reshift cluster
    02. Bulk inserting s3 raw songs and events data  into Redshift staging tables,
        staging_events and staging_songs
    03. Bulk inserting Redshift staging tables data into Redshift star schema
    04. Finally, closes the connection
    """
    config = configparser.ConfigParser()
    config.read("dwh.cfg")

    conn = psycopg2.connect(
        "host={} dbname={} user={} password={} port={}".format(
            *config["CLUSTER"].values()
        )
    )
    cur = conn.cursor()

    print("--- loading staging tables ---")
    load_staging_tables(cur, conn)
    print("\nDone!\n")

    print("--- insert into star schema ---")
    insert_tables(cur, conn)
    print("\nDone!\n")

    conn.close()


if __name__ == "__main__":
    main()
