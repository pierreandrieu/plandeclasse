# plan_classe/model/eleve.py
from typing import Optional, Tuple


class Eleve:
    """
    Représente un élève pouvant être placé sur une table dans le plan de classe.
    """

    def __init__(self, nom: str, genre: str) -> None:
        """
        Initialise un nouvel élève.

        Args:
            nom: Le nom de l'élève.
            genre: Le genre, typiquement "F" ou "M".
        """

        self._nom: str = nom.strip()
        self._genre: str = genre.strip()
        self._position: Optional[Tuple[int, int]] = None
        self._fixe: bool = False

        # Détection du nom de famille et du prénom à partir de la casse
        mots = self._nom.split()
        i = 0
        while i < len(mots) and mots[i].isupper():
            i += 1

        self._nom_famille = " ".join(mots[:i])
        self._prenom = " ".join(mots[i:])

    def get_nom(self) -> str:
        """Retourne le nom et le prénom de l'élève."""
        return self._nom

    def get_nom_famille(self) -> str:
        """Retourne le nom de famille de l'élève."""
        return self._nom_famille

    def get_prenom(self) -> str:
        """Retourne le prénom de l'élève."""
        return self._prenom

    def get_genre(self) -> str:
        """Retourne le genre de l'élève."""
        return self._genre

    def get_position(self) -> Optional[Tuple[int, int]]:
        """Retourne la position actuelle de l'élève (x, y) ou None."""
        return self._position

    def set_position(self, position: Tuple[int, int]) -> None:
        """Définit la position actuelle de l'élève."""
        self._position = position

    def est_fixe(self) -> bool:
        """Indique si l'élève a été fixé manuellement sur une table."""
        return self._fixe

    def fixer(self) -> None:
        """Fixe l'élève à sa position actuelle."""
        self._fixe = True

    def liberer(self) -> None:
        """Libère l'élève pour un placement automatique."""
        self._fixe = False

    def __str__(self) -> str:
        return f"{self._nom} ({self._genre})"

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return hash(self._nom)

    def __eq__(self, other) -> bool:
        return isinstance(other, Eleve) and self._nom == other._nom

    def __lt__(self, other: "Eleve") -> bool:
        """
        Permet de comparer deux élèves : d'abord par nom de famille, puis par prénom.
        """
        if self.get_nom_famille() != other.get_nom_famille():
            return self.get_nom_famille() < other.get_nom_famille()
        return self.get_prenom() < other.get_prenom()



