from classes import *
from sage.misc.prandom import randint, choice

def generation_aleatoire(width, height):
    # On initialise un PL rempli de murs
    L = PseudoMaze((width, height))
    for x, y in np.ndindex(L.size): (c := L.mazeMatrix[x, y]).h, c.g, c.d, c.b = 1, 1, 1, 1
    
    # On commence sur une cellule aléatoire
    currentCell = L.mazeMatrix[randint(0, width-1), randint(0, height-1)]
    currentCell.visited = True
    stack = [currentCell]

    # Tant que la pile n'est pas vide, ce qui équivaut à dire que l'on n'a pas tout visité
    while stack:
        # On prend la dernière cellule de la pile
        # et on détermine lesquels de ses voisins on n'a pas encore visité
        currentCell = stack[-1]
        non_visited_neighbors = [
            neighbor for neighbor in currentCell.neighbors if not neighbor.visited
        ]

        # Si la cellule a des voisins non visités, on continue de tracer un chemin avec celle-ci
        if non_visited_neighbors:
            # On choisit au hasard un voisin que l'on n'a pas encore vu
            nextCell = choice(non_visited_neighbors)
            nextCell.visited = True

            # Remove the wall between currentCell and nextCell
            (xc, yc), (xn, yn) = currentCell.xy, nextCell.xy
            if yc == yn:
                # On est sur la méme ligne, donc on enlève un mur vertical
                if xc < xn:
                    currentCell.d = 0
                    nextCell.g = 0
                else:
                    currentCell.g = 0
                    nextCell.d = 0
            else:
                # On est sur la mếme colonne, donc on enlève un mur horizontal
                if yc < yn:
                    currentCell.b = 0
                    nextCell.h = 0
                else:
                    currentCell.h = 0
                    nextCell.b = 0

            stack.append(nextCell)
        else:
            # Sinon, on revient en arrière, jusqu'à trouver une cellule ayant des voisins non visités
            # ou jusqu'à épuiser la pile, auquel cas le labyrinthe est terminé.
            stack.pop()
    
    L.update() # on met à jour l'attribut de construction par graphe

    return L


def nombre_labyrinthes(width, height):
    return PseudoMaze((width, height)).sage_graph.laplacian_matrix()[1:, 1:].determinant()


def resoudre_labyrinthe(L):
    return L.sage_graph.all_paths((0, 0), (L.width-1, L.height-1))[0]

def ferme_impasse(L, xy): # fonction auxiliaire
    if xy == (0, 0) or xy == (L.width-1, L.height-1): return False, None
    neighbors = L.adj[xy]
    if len(neighbors) == 1:
        other = neighbors[0]
        L.adj[xy] = []
        L.adj[other].remove(xy)
        return True, other
    else: return False, None

def resoudre_bride(L, verbose=False):
    G = PseudoMaze(adj=L.adj) # on copie le labyrinthe pour éviter les problèmes de modification en place
    modifie = True
    while modifie:
        modifie = False
        for xy in np.ndindex((G.width, G.height)):
            est_impasse, _ = ferme_impasse(G, xy)
            modifie = modifie or est_impasse
        G.update_from_adj()
        if verbose: G.plot_maze()
    return resoudre_labyrinthe(G)

def resoudre_bride_perf(L, verbose=False):
    G = PseudoMaze(adj=L.adj)
    modifie = True
    while modifie:
        modifie = False
        for xy in np.ndindex((G.width, G.height)):
            est_impasse, nxt = ferme_impasse(G, xy)
            modifie = modifie or est_impasse
            while est_impasse:
                est_impasse, nxt = ferme_impasse(G, nxt)
        G.update_from_adj()
        if verbose: G.plot_maze()
    return resoudre_labyrinthe(G)

def resolution_graphique(L, how=resoudre_labyrinthe, verbose=False):
    p = L.get_plot()
    path = how(L, verbose=verbose)
    for (xa, ya), (xb, yb) in zip(path[:-1], path[1:]):
        ya = L.height - ya
        yb = L.height - yb
        p += line2d([(xa+1/2, ya-1/2), (xb+1/2, yb-1/2)], color="blue", thickness=3)
    p.show()