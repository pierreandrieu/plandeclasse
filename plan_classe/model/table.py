from typing import Optional, Tuple, List
from .eleve import Eleve


class Table:
    """
    Représente une table avec plusieurs places pouvant accueillir des élèves.
    """

    def __init__(self, x: int, y: int, capacite: int) -> None:
        """
        Initialise une table à l’emplacement donné avec un nombre de places.

        Args:
            x: Indice de colonne (de gauche à droite).
            y: Indice de rangée (du tableau vers le fond de la salle).
            capacite: Nombre de places disponibles sur cette table.
        """
        self._x: int = x
        self._y: int = y
        self._places: List[Optional[Eleve]] = [None] * capacite
        self._valides: List[bool] = [True] * capacite

    def get_position(self) -> Tuple[int, int]:
        """Retourne la position (colonne, rangée) de la table."""
        return self._x, self._y

    def get_capacite(self) -> int:
        """Retourne le nombre total de places de la table."""
        return len(self._places)

    def get_places(self) -> List[Optional[Eleve]]:
        """Retourne la liste des élèves placés (ou None si place vide)."""
        return self._places

    from typing import Optional
    # ...

    def placer_eleve(self, eleve: Optional[Eleve], index: int) -> bool:
        """
        Place un élève sur une place donnée, ou vide cette place si eleve=None.

        Args:
            eleve: Élève à placer, ou None pour libérer la place.
            index: Numéro de la place (0-indexé)

        Returns:
            True si l'opération a réussi, False sinon.
        """
        if not (0 <= index < self.get_capacite()):
            return False

        if eleve is None:
            # Libération de la place
            self._places[index] = None
            return True

        if self._places[index] is None:
            self._places[index] = eleve
            return True

        return False

    def liberer_place(self, index: int) -> None:
        """Libère la place donnée (ne fait rien si hors bornes)."""
        if 0 <= index < self.get_capacite():
            self._places[index] = None

    def est_valide(self, index: int) -> bool:
        """Retourne True si la place est valide."""
        return self._valides[index]

    def invalider(self, index: int) -> None:
        """ Invalide la place à l'indice index """
        self._valides[index] = False

    def revalider(self, index: int) -> None:
        """ Valide la place à l'indice index """
        self._valides[index] = True

    def est_libre(self, index: int) -> bool:
        """Retourne True si la place est vide."""
        return 0 <= index < self.get_capacite() and self.est_valide(index) and self._places[index] is None

    def __str__(self) -> str:
        places_str = ", ".join(
            eleve.get_nom() if eleve else "vide"
            for eleve in self._places
        )
        return f"Table ({self._x}, {self._y}) : [{places_str}]"

    def __repr__(self) -> str:
        return str(self)
