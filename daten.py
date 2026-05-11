Python
import sqlite3

DB_NAME = "example.db"

def get_connection():
    """Erstellt eine Verbindung zur Datenbank und gibt sie zurück."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    """Initialisiert die Tabellenstruktur."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                age INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def create_user(name, email, age):
    """CREATE: Fügt einen neuen User hinzu."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                (name, email, age)
            )
            conn.commit()
            return cur.lastrowid
            
    except sqlite3.IntegrityError:
        print(f"Fehler: Email {email} existiert bereits.")
        return None

def read_users():
    """READ: Gibt alle User als Liste von Dicts zurück."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users ORDER BY id")
        return [dict(row) for row in cur.fetchall()]

def update_user_age(user_id, new_age):
    """UPDATE: Aktualisiert das Alter eines spezifischen Users."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET age = ? WHERE id = ?",
            (new_age, user_id)
        )
        conn.commit()

def delete_user(user_id):
    """DELETE: Löscht einen User anhand der ID."""
    with get_connection() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()


# 1. Datenbank vorbereiten
setup_database()

# 2. CREATE
new_id = create_user("Alex", "alex@web.de", 28)
create_user("Sam", "sam@example.com", 31)
print(f"User mit ID {new_id} erstellt.")

# 3. READ (Vor dem Update)
print("Alle User aktuell:")
for user in read_users():
    print(user)

# 4. UPDATE
if new_id:
    update_user_age(new_id, 29)
    print(f"Alter von User {new_id} auf 29 aktualisiert.")

# 5. DELETE
# delete_user(new_id)

# Finales Ergebnis
print("Endergebnis in der Datenbank:")
print(read_users())