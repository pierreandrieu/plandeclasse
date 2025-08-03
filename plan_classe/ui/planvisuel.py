from typing import List, Optional, Tuple, Callable, Dict
import pygame
from collections import defaultdict
from plan_classe.model.salle import Salle
from plan_classe.model.eleve import Eleve
from plan_classe.model.table import Table


class PlanVisuel:
    """
    Gère l'affichage graphique d'une salle de classe avec Pygame.
    Permet de visualiser les tables, les élèves, le bureau, et de déplacer les élèves
    depuis une zone latérale vers une place ou en échange avec un autre élève.
    """

    LARGEUR_FENETRE: int = 1280
    HAUTEUR_FENETRE: int = 720
    MARGE: int = 30

    LARGEUR_ZONE_ELEVES: int = 200
    HAUTEUR_RECT_ELEVE: int = 35

    COULEUR_FOND: Tuple[int, int, int] = (230, 230, 230)
    COULEUR_BUREAU: Tuple[int, int, int] = (160, 160, 160)
    DIM_BUREAU: Tuple[int, int] = (200, 60)

    LARGEUR_SIEGES: int = 100
    HAUTEUR_SIEGES: int = 30
    ECART_VERTICAL: int = 20
    ECART_HORIZONTAL: int = 40

    def __init__(self, salle: Salle, eleves: List[Eleve]) -> None:
        """
        Initialise le visuel à partir de la salle et des élèves.

        Args:
            salle: La salle à dessiner.
            eleves: Liste des élèves à afficher dans la zone de droite.
        """
        pygame.init()
        self._font: pygame.font.Font = pygame.font.SysFont(None, 22)
        self._screen: pygame.Surface = pygame.display.set_mode((self.LARGEUR_FENETRE, self.HAUTEUR_FENETRE))
        pygame.display.set_caption("Plan de classe")

        self._salle: Salle = salle
        self._eleves: List[Eleve] = eleves
        self._scroll_offset: int = 0
        self._table_scroll_offset: int = 0
        self._surface_eleves: pygame.Surface = pygame.Surface((self.LARGEUR_ZONE_ELEVES, self.HAUTEUR_FENETRE))

        self._eleve_selectionne: Optional[Eleve] = None
        self._pos_souris: Tuple[int, int] = (0, 0)
        self._dragging: bool = False
        self._zones_places: List[Tuple[int, int, int, int, Table, int]] = []
        self._centres_colonnes: List[int] = []
        self._siege_survole: Optional[Tuple[int, int, int]] = None

        self._menu_contextuel_actif: bool = False
        self._menu_position: Tuple[int, int] = (0, 0)
        self._menu_table: Optional[Table] = None
        self._menu_index: Optional[int] = None

        schema: List[List[int]] = salle.get_schema()
        capacite_max_par_colonne: List[int] = [max(col) for col in schema]
        x_courant: int = self.MARGE

        for capacite_max in capacite_max_par_colonne:
            largeur_colonne: int = capacite_max * self.LARGEUR_SIEGES
            centre_colonne: int = x_courant + largeur_colonne // 2
            self._centres_colonnes.append(centre_colonne)
            x_courant += largeur_colonne + self.ECART_HORIZONTAL

    def afficher(self) -> None:
        """
        Affiche tous les éléments à l'écran :
        - le fond
        - le bureau
        - les tables et les élèves placés
        - la zone des élèves non placés
        - l'élève en train d'être déplacé (si applicable)
        """
        self._screen.fill(self.COULEUR_FOND)
        self._dessiner_bureau()
        self._dessiner_tables()
        self._dessiner_zone_eleves()

        if self._dragging and self._eleve_selectionne:
            x, y = self._pos_souris
            rect: pygame.Rect = pygame.Rect(x - 50, y - 15, 100, 30)
            pygame.draw.rect(self._screen, (100, 100, 255), rect)
            texte: pygame.Surface = self._font.render(self._eleve_selectionne.get_nom(), True, (255, 255, 255))
            self._screen.blit(texte, (x - 45, y - 5))

        self._dessiner_menu_contextuel()
        pygame.display.flip()

    def _dessiner_bureau(self) -> None:
        """Dessine le bureau du professeur centré en haut de la salle."""
        largeur_bureau, hauteur_bureau = self.DIM_BUREAU
        x: int = (self.LARGEUR_FENETRE - self.LARGEUR_ZONE_ELEVES - largeur_bureau) // 2
        y: int = self.MARGE

        pygame.draw.rect(self._screen, self.COULEUR_BUREAU, (x, y, largeur_bureau, hauteur_bureau))
        texte: pygame.Surface = self._font.render("Bureau", True, (0, 0, 0))
        self._screen.blit(texte, (x + 60, y + 20))

    def _dessiner_tables(self) -> None:
        """Dessine les tables avec les élèves placés et enregistre les zones cliquables."""
        self._zones_places.clear()

        for table in self._salle.get_tables():
            col, row = table.get_position()
            capacite: int = table.get_capacite()

            x_centre: int = self._centres_colonnes[col]
            x_base: int = x_centre - (capacite * self.LARGEUR_SIEGES) // 2
            y_base: int = self.MARGE + 100 + row * (
                        self.HAUTEUR_SIEGES + self.ECART_VERTICAL) - self._table_scroll_offset

            for i in range(capacite):
                x: int = x_base + i * self.LARGEUR_SIEGES
                y: int = y_base

                self._zones_places.append((x, y, x + self.LARGEUR_SIEGES, y + self.HAUTEUR_SIEGES, table, i))
                pygame.draw.rect(self._screen, (139, 69, 19), (x, y, self.LARGEUR_SIEGES, self.HAUTEUR_SIEGES))
                if self._siege_survole == (col, row, i):
                    eleve_sur_place: Optional[Eleve] = table.get_places()[i]
                    couleur_survol: Tuple[int, int, int] = (200, 80, 80) if eleve_sur_place else (100, 150, 255)
                    couleur_siege: Tuple[int, int, int]
                    if not table.est_valide(i):
                        couleur_siege = (80, 80, 80)  # gris foncé pour place désactivée
                    else:
                        couleur_siege = (139, 69, 19)  # couleur bois classique

                    pygame.draw.rect(self._screen, couleur_siege, (x, y, self.LARGEUR_SIEGES, self.HAUTEUR_SIEGES))

                    pygame.draw.rect(self._screen, couleur_survol, (x, y, self.LARGEUR_SIEGES, self.HAUTEUR_SIEGES))
                    pygame.draw.rect(self._screen, (255, 255, 255), (x, y, self.LARGEUR_SIEGES, self.HAUTEUR_SIEGES),
                                     width=2)

                if i > 0:
                    pygame.draw.line(self._screen, (255, 255, 255), (x, y), (x, y + self.HAUTEUR_SIEGES), 2)

                eleve: Optional[Eleve] = table.get_places()[i]
                if eleve:
                    texte: pygame.Surface = self._font.render(eleve.get_nom(), True, (255, 255, 255))
                    self._screen.blit(texte, (x + 5, y + 8))

    def _dessiner_zone_eleves(self) -> None:
        """Affiche la zone latérale contenant les élèves non placés (scrollable)."""
        self._surface_eleves.fill((200, 200, 200))
        nb_visible: int = self.HAUTEUR_FENETRE // self.HAUTEUR_RECT_ELEVE

        for i, eleve in enumerate(self._eleves[self._scroll_offset:]):
            if i >= nb_visible:
                break

            y: int = i * self.HAUTEUR_RECT_ELEVE
            rect: pygame.Rect = pygame.Rect(0, y, self.LARGEUR_ZONE_ELEVES, self.HAUTEUR_RECT_ELEVE)
            pygame.draw.rect(self._surface_eleves, (180, 180, 180), rect)
            pygame.draw.rect(self._surface_eleves, (100, 100, 100), rect, 1)
            texte: pygame.Surface = self._font.render(eleve.get_prenom(), True, (0, 0, 0))
            self._surface_eleves.blit(texte, (10, y + 8))

        x_zone: int = self.LARGEUR_FENETRE - self.LARGEUR_ZONE_ELEVES
        self._screen.blit(self._surface_eleves, (x_zone, 0))

    def defiler(self, direction: int, cible: str = "eleves") -> None:
        """
        Gère le défilement (molette) pour les élèves ou les tables.

        Args:
            direction: +1 ou -1 selon la direction de la molette.
            cible: "eleves" ou "tables"
        """
        if cible == "eleves":
            max_offset: int = max(0, len(self._eleves) - self.HAUTEUR_FENETRE // self.HAUTEUR_RECT_ELEVE)
            self._scroll_offset = min(max(0, self._scroll_offset + direction), max_offset)
        elif cible == "tables":
            self._table_scroll_offset = max(0, self._table_scroll_offset + direction * 30)

    def gerer_mouvement_souris(self, position: Tuple[int, int]) -> None:
        """Met à jour la position de la souris (utile pendant un drag)."""
        self._pos_souris = position

    def clic_sur_zone_eleves(self, position: Tuple[int, int]) -> None:
        """
        Sélectionne un élève dans la zone de droite pour débuter un glisser-déposer.

        Args:
            position: Position de la souris au clic.
        """
        x_souris, y_souris = position
        if x_souris < self.LARGEUR_FENETRE - self.LARGEUR_ZONE_ELEVES:
            return

        index: int = y_souris // self.HAUTEUR_RECT_ELEVE + self._scroll_offset
        if 0 <= index < len(self._eleves):
            self._eleve_selectionne = self._eleves.pop(index)
            self._dragging = True

    def relacher_souris(self) -> None:
        """
        Lors du relâchement de la souris :
        - si on vise une place libre : place l’élève
        - si on vise une place occupée : échange
        - sinon : remet l’élève dans la zone élève (avec tri)
        """
        if not self._eleve_selectionne:
            return

        for x1, y1, x2, y2, table, index in self._zones_places:
            if x1 <= self._pos_souris[0] <= x2 and y1 <= self._pos_souris[1] <= y2:
                ancien: Optional[Eleve] = table.get_places()[index]
                table.placer_eleve(self._eleve_selectionne, index)
                if ancien:
                    self.ajouter_eleve_et_trier(ancien)
                self._eleve_selectionne = None
                self._dragging = False
                return

        # Si aucune place visée, on remet l’élève dans la zone élève
        self.ajouter_eleve_et_trier(self._eleve_selectionne)
        self._eleve_selectionne = None
        self._dragging = False

    @staticmethod
    def desambiguiser(
            individus: List[Eleve],
            cle_principale: Callable[[Eleve], str],
            cle_secondaire: Callable[[Eleve], str],
            format_final: Callable[[str, str], str]
    ) -> Dict[Eleve, str]:
        """
        Désambiguïse des noms/prénoms selon une clé principale et une clé secondaire.

        Exemple : deux "Léo" deviennent "Léo D." et "Léo Dè." si besoin.

        Args:
            individus: Liste d'objets Eleve.
            cle_principale: Fonction donnant le nom/prénom de base.
            cle_secondaire: Fonction donnant la partie pour désambiguïser.
            format_final: Fonction pour formater la chaîne finale.

        Returns:
            Dictionnaire associant chaque élève à sa version désambiguïsée.
        """
        groupes: Dict[str, List[Eleve]] = defaultdict(list)
        result: Dict[Eleve, str] = {}

        for e in individus:
            groupes[cle_principale(e)].append(e)

        for valeur_principale, liste in groupes.items():
            if len(liste) == 1:
                result[liste[0]] = valeur_principale
            else:
                suffixes_utilises: Dict[Eleve, str] = {}
                for e in liste:
                    secondaire: str = cle_secondaire(e)
                    i: int = 1
                    while True:
                        extension: str = secondaire[:i]
                        candidat: str = format_final(valeur_principale, extension)
                        if candidat not in suffixes_utilises.values():
                            suffixes_utilises[e] = candidat
                            break
                        i += 1
                result.update(suffixes_utilises)

        return result

    def prenom_a_afficher(self) -> Dict[Eleve, str]:
        """
        Donne un affichage unique pour chaque élève basé sur le prénom.
        Ajoute une initiale du nom si nécessaire pour éviter les doublons.
        """
        return self.desambiguiser(
            self._eleves,
            cle_principale=lambda e: e.get_prenom(),
            cle_secondaire=lambda e: e.get_nom_famille(),
            format_final=lambda prenom, suffixe: f"{prenom} {suffixe}."
        )

    def nom_a_afficher(self) -> Dict[Eleve, str]:
        """
        Donne un affichage unique pour chaque élève basé sur le nom de famille.
        Ajoute une initiale du prénom si nécessaire pour éviter les doublons.
        """
        return self.desambiguiser(
            self._eleves,
            cle_principale=lambda e: e.get_nom_famille(),
            cle_secondaire=lambda e: e.get_prenom(),
            format_final=lambda nom, suffixe: f"{nom} {suffixe}."
        )

    def get_table_et_siege_depuis_coordonnees(self, x: int, y: int) -> Optional[Tuple[int, int, int]]:
        """
        Renvoie la position de table et le siège (numéro) sous les coordonnées données.

        Args:
            x: Abscisse de la souris (pixels)
            y: Ordonnée de la souris (pixels)

        Returns:
            - (colonne, rangée, numéro_du_siege) si la souris est bien sur un siège.
            - None sinon.
        """
        for table in self._salle.get_tables():
            col, row = table.get_position()
            capacite: int = table.get_capacite()

            x_centre: int = self._centres_colonnes[col]
            x_base: int = x_centre - (capacite * self.LARGEUR_SIEGES) // 2
            y_base: int = self.MARGE + 100 + row * (
                        self.HAUTEUR_SIEGES + self.ECART_VERTICAL) - self._table_scroll_offset

            for i in range(capacite):
                rect_siege: pygame.Rect = pygame.Rect(
                    x_base + i * self.LARGEUR_SIEGES,
                    y_base,
                    self.LARGEUR_SIEGES,
                    self.HAUTEUR_SIEGES
                )
                if rect_siege.collidepoint(x, y):
                    return col, row, i

        return None

    def survoler(self, x: int, y: int) -> None:
        """
        Met à jour le siège actuellement survolé (pour affichage).
        """
        self._siege_survole = self.get_table_et_siege_depuis_coordonnees(x, y)

    def ouvrir_menu_contextuel(self, x: int, y: int) -> None:
        """
        Active le menu contextuel si clic droit sur une place.
        """
        for x1, y1, x2, y2, table, index in self._zones_places:
            if x1 <= x <= x2 and y1 <= y <= y2:
                self._menu_contextuel_actif = True
                self._menu_position = (x, y)
                self._menu_table = table
                self._menu_index = index
                return
        self._menu_contextuel_actif = False

    def _dessiner_menu_contextuel(self) -> None:
        if not self._menu_contextuel_actif or self._menu_table is None:
            return

        x, y = self._menu_position
        options = ["Désactiver", "Réactiver", "Vider"]
        hauteur_option = 25
        largeur = 120
        hauteur_totale = hauteur_option * len(options)

        fond = pygame.Rect(x, y, largeur, hauteur_totale)
        pygame.draw.rect(self._screen, (240, 240, 240), fond)
        pygame.draw.rect(self._screen, (0, 0, 0), fond, 1)

        for i, texte in enumerate(options):
            surface = self._font.render(texte, True, (0, 0, 0))
            self._screen.blit(surface, (x + 5, y + i * hauteur_option + 5))

    def clic_menu_contextuel(self, x: int, y: int) -> None:
        if not self._menu_contextuel_actif or self._menu_table is None:
            return

        x0, y0 = self._menu_position
        hauteur_option = 25

        if not (x0 <= x <= x0 + 120 and y0 <= y <= y0 + hauteur_option * 3):
            self._menu_contextuel_actif = False
            return

        i = (y - y0) // hauteur_option

        if i == 0:  # Désactiver
            if self._menu_table.get_places()[self._menu_index]:
                self.ajouter_eleve_et_trier(self._menu_table.get_places()[self._menu_index])
                self._menu_table.placer_eleve(None, self._menu_index)
            self._menu_table.invalider(self._menu_index)

        elif i == 1:  # Réactiver
            self._menu_table.revalider(self._menu_index)

        elif i == 2:  # Vider
            if self._menu_table.get_places()[self._menu_index]:
                self.ajouter_eleve_et_trier(self._menu_table.get_places()[self._menu_index])
                self._menu_table.placer_eleve(None, self._menu_index)

        self._menu_contextuel_actif = False

    def ajouter_eleve_et_trier(self, eleve: Eleve) -> None:
        """
        Ajoute un élève dans la zone des élèves tout en maintenant l’ordre alphabétique.
        """
        self._eleves.append(eleve)
        self._eleves.sort()
