# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect("certifica.db")
cursor = conn.cursor()

def createDB():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS signatures(
        id INTEGER PRIMARY KEY NOT NULL,
        name VARCHAR(62) NOT NULL,
        role VARCHAR(20) NOT NULL,
        email VARCHAR(30) NOT NULL,
        register VARCHAR(20) NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY NOT NULL,
        title VARCHAR(62) NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        hours INTEGER,
        content TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients(
        id INTEGER PRIMARY KEY NOT NULL,
        name VARCHAR(62) NOT NULL,
        email VARCHAR(20) NOT NULL,
        register VARCHAR(20)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions(
        id INTEGER PRIMARY KEY NOT NULL,
        event_id INTEGER,
        client_id INTEGER,
        FOREIGN KEY(event_id) REFERENCES events(id),
        FOREIGN KEY(client_id) REFERENCES clients(id)
    );
    """)
