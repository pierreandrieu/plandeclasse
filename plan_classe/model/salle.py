from typing import List
from .table import Table


class Salle:
    """
    Représente une salle de classe composée de tables disposées par rangées.
    """

    def __init__(self, schema: List[List[int]]) -> None:
        """
        Initialise une salle à partir d’un schéma précis de rangées.

        Args:
            schema: Liste de rangées, chaque rangée est une liste d’entiers indiquant
                    le nombre de places par table (vue verticale du prof).
        """
        self._tables: List[Table] = []
        for row_index, ligne in enumerate(schema):
            for col_index, capacite in enumerate(ligne):
                print(col_index, row_index, capacite)
                self._tables.append(Table(x=col_index, y=row_index, capacite=capacite))

    @classmethod
    def depuis_mode_compact(cls, nb_lignes: int, capacites_par_table: List[int]) -> "Salle":
        """
        Crée une salle avec un nombre donné de lignes, chacune composée de plusieurs tables
        dont les capacités sont données dans une liste.

        Exemple : 5 lignes, [2, 3, 2] →
            [
                [2, 3, 2],
                [2, 3, 2],
                [2, 3, 2],
                [2, 3, 2],
                [2, 3, 2],
            ]
        """
        schema = [capacites_par_table.copy() for _ in range(nb_lignes)]
        return cls(schema)

    def get_tables(self) -> List[Table]:
        """Retourne toutes les tables de la salle."""
        return self._tables

    def get_schema(self) -> List[List[int]]:
        """Retourne le schéma brut sous forme de liste de listes."""
        max_x = max(t.get_position()[0] for t in self._tables) + 1
        # max_y = max(t.get_position()[1] for t in self._tables) + 1

        schema: List[List[int]] = [[] for _ in range(max_x)]
        for table in self._tables:
            x, y = table.get_position()
            if len(schema) <= x:
                schema.append([])
            if len(schema[x]) <= y:
                schema[x].extend([0] * (y - len(schema[x]) + 1))
            schema[x][y] = table.get_capacite()
        return schema

    def __str__(self) -> str:
        lignes: dict[int, list[Table]] = {}
        for table in self._tables:
            _, y = table.get_position()
            lignes.setdefault(y, []).append(table)

        result = []
        for y in sorted(lignes):
            ligne = sorted(lignes[y], key=lambda t: t.get_position()[0])
            result.append(" | ".join(str(table) for table in ligne))
        return "\n".join(result)

    def __repr__(self) -> str:
        return str(self)

    def get_largeurs_colonnes(self, largeur_siege: int = 100, marge_inter_colonne: int = 15) -> List[int]:
        """
        Renvoie la largeur totale occupée par chaque colonne, pour placement graphique.

        Args:
            largeur_siege: Largeur d’un siège (par défaut 75 px)
            marge_inter_colonne: Marge entre deux tables (par défaut 20 px)

        Returns:
            Liste des largeurs cumulées (en pixels) par colonne.
        """
        schema = self.get_schema()
        largeurs = []
        for colonne in schema:
            # On prend la capacité max dans la colonne
            capacite_max = max(colonne)
            largeur = capacite_max * largeur_siege + marge_inter_colonne
            largeurs.append(largeur)
        return largeurs
