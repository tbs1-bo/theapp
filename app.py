# https://flet.dev/docs/
import flet as ft
import sqlite3
import logging as log

PORT = 5566
DB_FILE = "ideas.db"

log.basicConfig(level=log.DEBUG)
# https://flet.dev/docs/guides/python/logging
# To reduce verbosity you may suppress logging messages from flet_core module, but adding:
log.getLogger("flet_core").setLevel(log.INFO)

# TODO add auth https://flet.dev/docs/guides/python/authentication

def init_db():
    log.debug("init db", DB_FILE)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
              CREATE TABLE IF NOT EXISTS ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT,
                idea TEXT
              )
              """)
    conn.commit()
    conn.close()

def add_idea(author, idea):
    log.debug(f"add idea: {author} {idea}")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO ideas (author, idea) VALUES (?,?)", 
              (author,idea))
    conn.commit()
    conn.close()

def get_ideas():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT author,idea FROM ideas")
    ideas = c.fetchall()
    conn.close()
    return ideas

def main(page: ft.Page):
    def btn_clicked(e):
        if ideafield.value == "":
            idea.error_text = "Bitte gib eine Idee ein!"
            page.update()
            return
        if authorfield.value != "Anonym":
            page.client_storage.set("author", authorfield.value)

        log.debug("adding idea:", ideafield.value)
        add_idea(authorfield.value, ideafield.value)
        page.add(ft.Text(f"NEU {ideafield.value}"))
        ideafield.value = ""
        ideafield.focus()
        page.update()

    page.add(ft.Text("# Kummerkasten"))

    ideafield = ft.TextField(label="Idee", autofocus=True)    
    authorfield = ft.TextField(label="Autor", value="Anonym")
    if page.client_storage.contains_key("author"):
        authorfield.value = page.client_storage.get("author")
    row = ft.Row(controls= [
        ideafield,
        ft.ElevatedButton(text="Senden", on_click=btn_clicked)
    ])
    page.add(authorfield)
    page.add(row)

    lv = ft.ListView(expand=False)
    for idea in get_ideas():
        lv.controls.append(ft.Text(f"{idea['author']}: {idea['idea']}"))
    page.add(lv)


log.info("starting app")
init_db()
ft.app(target=main, port=PORT, 
       view=ft.AppView.WEB_BROWSER,
       assets_dir="assets")
