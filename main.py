import pygame

from plan_classe.model.eleve import Eleve
from plan_classe.model.salle import Salle
from plan_classe.ui.planvisuel import PlanVisuel


def lancer_pygame(salle: Salle, eleves: list[Eleve]) -> None:
    visuel = PlanVisuel(salle, eleves)
    visuel.afficher()

    clock = pygame.time.Clock()
    running: bool = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # molette haut
                    visuel.defiler(-1)
                elif event.button == 5:  # molette bas
                    visuel.defiler(1)
                elif event.button == 1:  # clic gauche
                    if visuel._menu_contextuel_actif:
                        visuel.clic_menu_contextuel(*event.pos)
                    else:
                        visuel.clic_sur_zone_eleves(event.pos)
                elif event.button == 3:  # clic droit
                    visuel.ouvrir_menu_contextuel(*event.pos)

                visuel.afficher()

            elif event.type == pygame.MOUSEMOTION:
                visuel.gerer_mouvement_souris(event.pos)
                visuel.survoler(*event.pos)
                visuel.afficher()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # relâchement du clic gauche
                    visuel.relacher_souris()
                    visuel.afficher()

        clock.tick(60)

    pygame.quit()


def main():
    salle = Salle.depuis_mode_compact(nb_lignes=9, capacites_par_table=[3, 4, 4])
    eleves = [Eleve(f"Élève{i + 1}", "F" if i % 2 == 0 else "M") for i in range(20)]
    lancer_pygame(salle, eleves)
