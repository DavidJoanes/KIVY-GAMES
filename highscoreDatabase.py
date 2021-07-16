# ========================Backend================#
import sqlite3


# ------------------------------Create main-table (for high score)----------------------------#

def createHighScoreTable():
    con = sqlite3.connect("highscoreDatabase.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS HighScores (Highscore INTEGER)")
    con.commit()
    con.close()


def addHighScore(Highscore):
    con = sqlite3.connect("highscoreDatabase.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM HighScores")
    rows = cur.fetchall()
    hsList = [0]
    for row in rows:
        hsList.append(row[-1])
    if Highscore > max(hsList):
        cur.execute("INSERT INTO HighScores VALUES (?)", [Highscore])
        con.commit()
        con.close()


def viewHighScores():
    con = sqlite3.connect("highscoreDatabase.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM HighScores")
    rows = cur.fetchall()
    hsList = [0]
    for row in rows:
        hsList.append(row[-1])
    return hsList[-4:]


def viewHighScores2():
    con = sqlite3.connect("highscoreDatabase.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM HighScores")
    rows = cur.fetchall()
    print(rows)
    con.close()
    return rows


def newHighScore(Highscore):
    con = sqlite3.connect("highscoreDatabase.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM HighScores")
    rows = cur.fetchall()
    hsList = [0]
    for row in rows:
        hsList.append(row[-1])
    if Highscore > max(hsList):
        return Highscore
    else:
        return ""


createHighScoreTable()
