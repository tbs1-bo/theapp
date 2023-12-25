# https://flet.dev/docs/
import flet as ft
import sqlite3

PORT = 5566
DB_FILE = "ideas.db"


def init_db():
    print("init db", DB_FILE)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
              CREATE TABLE IF NOT EXISTS ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idea TEXT
              )
              """)
    conn.commit()
    conn.close()

def add_idea(idea):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO ideas (idea) VALUES (?)", (idea,))
    conn.commit()
    conn.close()

def get_ideas():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM ideas")
    ideas = c.fetchall()
    conn.close()
    return ideas

def main(page: ft.Page):
    def btn_clicked(e):
        if ideafield.value == "":
            idea.error_text = "Bitte gib eine Idee ein!"
            page.update()
            return

        print("adding idea:", ideafield.value)
        add_idea(ideafield.value)
        page.add(ft.Text(f"NEU {ideafield.value}"))
        ideafield.value = ""
        ideafield.focus()
        page.update()

    page.add(ft.Text("# Kummerkasten"))

    ideafield = ft.TextField(label="Idee", autofocus=True)
    row = ft.Row(controls= [
        ideafield,
        ft.ElevatedButton(text="Senden", on_click=btn_clicked)
    ])
    page.add(row)

    lv = ft.ListView(expand=False)
    for idead_id, idea in get_ideas():
        lv.controls.append(ft.Text(f"{idead_id}: {idea}"))
    page.add(lv)


init_db()
ft.app(target=main, port=PORT, view=ft.AppView.WEB_BROWSER)
