import tkinter as tk
from tkinter import filedialog, messagebox
from plan_classe.model.eleve import Eleve
from plan_classe.model.salle import Salle
from main import lancer_pygame
import csv
import threading


def charger_eleves_depuis_csv(path: str) -> list[Eleve]:
    """
    Charge les élèves depuis un fichier CSV exporté depuis Pronote.
    Détecte le nom complet (colonne 0) et le genre (colonne 3).
    """
    eleves = []
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        for ligne in reader:
            if len(ligne) >= 4:
                nom = ligne[0].strip('"').strip()
                genre = ligne[3].strip()
                eleves.append(Eleve(nom, genre))
    return eleves


def lancer() -> None:
    """
    Récupère les données des champs, construit la salle et lance Pygame dans un thread.
    """
    try:
        path_csv = entry_csv.get()
        nb_lignes = int(entry_lignes.get())
        capacites = list(map(int, entry_capacites.get().split(",")))

        eleves = charger_eleves_depuis_csv(path_csv)
        salle = Salle.depuis_mode_compact(nb_lignes=nb_lignes, capacites_par_table=capacites)

        # Lancement de Pygame dans un thread séparé
        threading.Thread(target=lancer_pygame, args=(salle, eleves), daemon=True).start()

    except Exception as e:
        messagebox.showerror("Erreur", str(e))


# -------------------------- Interface Tkinter --------------------------

root = tk.Tk()
root.title("Configuration du plan de classe")
root.geometry("+0+0")  # Position à gauche de l'écran

tk.Label(root, text="Fichier CSV de la classe (export PRONOTE) :").pack()
entry_csv = tk.Entry(root, width=50)
entry_csv.pack()
tk.Button(root, text="Parcourir", command=lambda: entry_csv.insert(0, filedialog.askopenfilename(
    filetypes=[("Fichier CSV", "*.csv")]))).pack()

tk.Label(root, text="Nombre de rangées (profondeur) :").pack()
entry_lignes = tk.Entry(root)
entry_lignes.insert(0, "9")
entry_lignes.pack()

tk.Label(root, text="Capacités par colonne (ex: 3,4,4) :").pack()
entry_capacites = tk.Entry(root)
entry_capacites.insert(0, "3,4,4")
entry_capacites.pack()

tk.Button(root, text="Lancer", command=lancer).pack(pady=10)

root.mainloop()
