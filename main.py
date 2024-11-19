import tkinter as tk
import random
from tkinter import messagebox
from tkinter import ttk
import os
import sqlite3

# Diccionario de temas y palabras
themes = {
    "Frutas": [
        "manzana", "platano", "naranja", "fresa", "uva",
        "kiwi", "sandia", "mango", "cereza", "limon",
        "peras", "melocoton", "pina", "coco", "papaya"
    ],
    "Conceptos Informaticos": [
        "algoritmo", "programacion", "codigo", "variable", "funcion",
        "bucle", "compilador", "debugging", "red", "sistema",
        "base de datos", "nube", "software", "hardware", "enlace"
    ],
    "Nombres de Personas": [
        "ana", "juan", "pedro", "maria", "lucia",
        "javier", "carlos", "laura", "daniel", "marta",
        "victor", "sofia", "gabriel", "elena", "pedro"
    ]
}

def salir():
    root.quit()

def get_random_word_and_theme():
    theme = random.choice(list(themes.keys()))
    word = random.choice(themes[theme])
    return theme, word.lower()

# Crear base de datos
def create_db():
    conn = sqlite3.connect('hangman_game.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            name TEXT,
            wins INTEGER,
            losses INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Actualizar estadísticas del jugador
def update_player_stats(player_name, win):
    conn = sqlite3.connect('hangman_game.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE name = ?", (player_name,))
    player = cursor.fetchone()

    if player:
        if win:
            cursor.execute("UPDATE players SET wins = wins + 1 WHERE name = ?", (player_name,))
        else:
            cursor.execute("UPDATE players SET losses = losses + 1 WHERE name = ?", (player_name,))
    else:
        if win:
            cursor.execute("INSERT INTO players (name, wins, losses) VALUES (?, 1, 0)", (player_name,))
        else:
            cursor.execute("INSERT INTO players (name, wins, losses) VALUES (?, 0, 1)", (player_name,))

    conn.commit()
    conn.close()

# Mostrar estadísticas
def show_stats():
    conn = sqlite3.connect('hangman_game.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players ORDER BY wins DESC")
    players = cursor.fetchall()
    conn.close()

    stats_window = tk.Toplevel()
    stats_window.title("Estadísticas de Jugadores")
    stats_window.geometry("500x400")
    stats_window.configure(bg="#C3E4E7")

    title_label = tk.Label(stats_window, text="Estadísticas de Jugadores", font=("Arial", 24), fg="#00474F", bg="#C3E4E7")
    title_label.pack(pady=20)

    stats_text = tk.Text(stats_window, width=40, height=10, bg="white", fg="#00474F", font=("Arial", 16))
    stats_text.pack(pady=20)

    for player in players:
        stats_text.insert(tk.END, f"{player[1]} - Victorias: {player[2]}, Derrotas: {player[3]}\n")

    stats_text.config(state=tk.DISABLED)

class HangmanGame:
    def __init__(self, root, player_name):
        self.root = root
        self.player_name = player_name
        self.root.title("Ahorcado")
        self.root.geometry("1000x1000")
        self.root.configure(bg="#C3E4E7")

        boton = ttk.Button(self.root, text="Salir", command=salir)
        boton.place(x=30, y=550)

        self.root.resizable(False, False)
        self.theme, self.word = get_random_word_and_theme()
        self.lives = 8
        self.guessed_word = ["_"] * len(self.word)
        self.guessed_letters = set()

        self.images = self.load_images_from_folder("Fases")
        if len(self.images) != 8:
            messagebox.showerror("Error",
                                 "La carpeta 'Fases' debe contener exactamente 8 imágenes numeradas (fase1.png a fase8.png).")
            self.root.destroy()
            return

        self.create_widgets()

    def load_images_from_folder(self, folder):
        images = []
        for i in range(1, 9):
            try:
                image_path = os.path.join(folder, f"fase{i}.png")
                images.append(tk.PhotoImage(file=image_path))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen: {image_path}\n{e}")
                self.root.destroy()
                return []
        return images

    def create_widgets(self):
        self.theme_label = tk.Label(self.root, text=f"Tema: {self.theme}", font=("Arial", 24), fg="#00474F", bg="#C3E4E7")
        self.theme_label.pack(pady=10)

        self.player_name_label = tk.Label(self.root, text=f"Jugador: {self.player_name}", font=("Arial", 22), fg="#00474F", bg="#C3E4E7")
        self.player_name_label.pack(pady=10)

        self.image_label = tk.Label(self.root, image=self.images[0], bg="#C3E4E7")
        self.image_label.pack(pady=10)

        self.word_label = tk.Label(self.root, text=" ".join(self.guessed_word), font=("Arial", 22), fg="#00474F", bg="#C3E4E7")
        self.word_label.pack(pady=10)

        self.letters_frame = tk.Frame(self.root, bg="#C3E4E7")
        self.letters_frame.pack(pady=10)

        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for letter in alphabet:
            button = ttk.Button(self.letters_frame, text=letter, width=4, command=lambda l=letter: self.guess_letter(l))
            button.grid(row=alphabet.index(letter) // 7, column=alphabet.index(letter) % 7)

        self.used_letters_label = tk.Label(self.root, text="Letras usadas: ", font=("Arial", 14), fg="#00474F", bg="#C3E4E7")
        self.used_letters_label.pack(pady=10)

    def guess_letter(self, letter):
        if letter in self.guessed_letters:
            messagebox.showinfo("Ya adivinaste", f"Ya intentaste con la letra '{letter}'.")
            return

        self.guessed_letters.add(letter)
        self.used_letters_label.config(text=f"Letras usadas: {' '.join(sorted(self.guessed_letters))}")

        if letter.lower() in self.word:
            for i, char in enumerate(self.word):
                if char == letter.lower():
                    self.guessed_word[i] = letter
            self.word_label.config(text=" ".join(self.guessed_word))

            if "_" not in self.guessed_word:
                update_player_stats(self.player_name, win=True)
                messagebox.showinfo("¡Ganaste!", f"¡Felicidades! Adivinaste la palabra: {self.word.upper()}.")
                self.root.destroy()
        else:
            self.lives -= 1
            image_index = 8 - self.lives if self.lives > 0 else 7
            self.image_label.config(image=self.images[image_index])

            if self.lives == 0:
                update_player_stats(self.player_name, win=False)
                messagebox.showinfo("Perdiste", f"Te quedaste sin vidas. La palabra era: {self.word.upper()}.")
                self.root.destroy()
