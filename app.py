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
# TODO add notification mechanism https://flet.dev/docs/guides/python/pub-sub

def init_db():
    log.debug("init db", DB_FILE)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
              CREATE TABLE IF NOT EXISTS ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT,
                idea TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    c.execute("SELECT author,idea,created_at FROM ideas")
    ideas = c.fetchall()
    conn.close()
    return ideas

def make_datatable():
    dt = ft.DataTable()
    dt.columns = [
        ft.DataColumn(ft.Text("Autor")),
        ft.DataColumn(ft.Text("Idee")),
        ft.DataColumn(ft.Text("Erstellt am"))
        ]    
    for idea in get_ideas():
        dt.rows.append(
            ft.DataRow(cells= [
                ft.DataCell(ft.Text(idea["author"])),
                ft.DataCell(ft.Text(idea["idea"])),
                ft.DataCell(ft.Text(idea["created_at"]))
            ]))

    return dt


def main(page: ft.Page):
    def msg_received(topic, msg):
        page.add(ft.Text(f"msg received: ({topic}) {msg}"))

    def btn_clicked(e):
        if ideafield.value == "":
            ideafield.error_text = "Bitte gib eine Idee ein!"
            page.update()
            return
        if authorfield.value != "Anonym":
            page.client_storage.set("author", authorfield.value)

        log.debug("adding idea:", ideafield.value)
        add_idea(authorfield.value, ideafield.value)
        page.pubsub.send_all_on_topic("ideas", 
                f"Neue Idee von {authorfield.value}: {ideafield.value}")
        page.add(ft.Text(f"NEU {ideafield.value}"))
        ideafield.value = ""
        ideafield.focus()
        page.update()

    page.add(ft.Markdown("# Kummerkasten"))

    authorfield = ft.TextField(label="Autor", value="Anonym")
    ideafield = ft.TextField(label="Idee", autofocus=True, multiline=True)
    if page.client_storage.contains_key("author"):
        authorfield.value = page.client_storage.get("author")
    row = ft.Column(controls= [
        authorfield,
        ideafield,
        ft.ElevatedButton(text="Senden", on_click=btn_clicked)
    ])
    page.add(row)

    page.add(ft.Markdown("## Alle Ideen"))
    page.add(make_datatable())

    page.pubsub.subscribe_topic("ideas", msg_received)


log.info("starting app")
init_db()
ft.app(target=main, port=PORT, 
       view=ft.AppView.WEB_BROWSER,
       assets_dir="assets")
