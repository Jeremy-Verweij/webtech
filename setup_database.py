import sqlite3
import os

db_path = 'database/db.sqlite'

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("SELECT 1")  
        conn.close()
    except sqlite3.DatabaseError:
        print("Database is corrupt! Verwijderen en opnieuw aanmaken...")
        os.remove(db_path) 
else:
    print("Database bestaat niet. Een nieuwe database wordt aangemaakt.")

conn = sqlite3.connect(db_path)
c = conn.cursor()

tables = [
    '''CREATE TABLE IF NOT EXISTS Users (
        UUID INTEGER PRIMARY KEY AUTOINCREMENT,
        PasswordHash TEXT NOT NULL,
        EmailAdress TEXT NOT NULL UNIQUE,
        UserName TEXT NOT NULL,
        Prive BOOLEAN DEFAULT 0,
        ProfilePicture INTEGER,
        FOREIGN KEY (ProfilePicture) REFERENCES ProfilePictures(PictureID)
    )''',
    
    '''CREATE TABLE IF NOT EXISTS Following (
        FollowingID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER NOT NULL,
        FollowedUserID INTEGER NOT NULL,
        FOREIGN KEY (UserID) REFERENCES Users(UUID),
        FOREIGN KEY (FollowedUserID) REFERENCES Users(UUID)
    )''',
    
    '''CREATE TABLE IF NOT EXISTS Likes (
        UserID INTEGER NOT NULL,
        PostID INTEGER NOT NULL,
        PRIMARY KEY (UserID, PostID),
        FOREIGN KEY (UserID) REFERENCES Users(UUID),
        FOREIGN KEY (PostID) REFERENCES Posts(PostID)
    )''',
    
    '''CREATE TABLE IF NOT EXISTS Posts (
        PostID INTEGER PRIMARY KEY AUTOINCREMENT,
        ParentPost INTEGER,
        RepostID INTEGER,
        UserID INTEGER NOT NULL,
        Title TEXT,
        Content TEXT,
        FOREIGN KEY (ParentPost) REFERENCES Posts(PostID),
        FOREIGN KEY (RepostID) REFERENCES Posts(PostID),
        FOREIGN KEY (UserID) REFERENCES Users(UUID)
    )''',
    
    '''CREATE TABLE IF NOT EXISTS ProfilePictures (
        PictureID INTEGER PRIMARY KEY AUTOINCREMENT,
        ImageData BLOB
    )''',
    
    '''CREATE TABLE IF NOT EXISTS Settings (
        UserID INTEGER PRIMARY KEY,
        DarkMode BOOLEAN DEFAULT 0,
        Language TEXT DEFAULT 'EN',
        FOREIGN KEY (UserID) REFERENCES Users(UUID)
    )'''
]

for table in tables:
    c.execute(table)

try:
    c.execute("INSERT INTO Users (PasswordHash, EmailAdress, UserName) VALUES ('password123', 'jan@example.com', 'Jan Jansen')")
    c.execute("INSERT INTO Users (PasswordHash, EmailAdress, UserName) VALUES ('password456', 'piet@example.com', 'Piet Pietersen')")
    c.execute("INSERT INTO Users (PasswordHash, EmailAdress, UserName) VALUES ('password789', 'marie@example.com', 'Marie Meijer')")
except sqlite3.IntegrityError:
    print("Records bestaan al.")

conn.commit()
conn.close()

print("Database en tabellen zijn succesvol aangemaakt!")
