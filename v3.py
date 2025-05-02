from random import randint

dicoLettres = {
    'A':14,
    'B':3,
    'C':4,
    'D':4,
    'E':21,
    'F':3,
    'G':2,
    'H':2,
    'I':12,
    'J':1,
    'K':1,
    'L':7,
    'M':4,
    'N':9,
    'O':9,
    'P':3,
    'Q':1,
    'R':9,
    'S':9,
    'T':9,
    'U':9,
    'V':3,
    'W':1,
    'X':1,
    'Y':1,
    'Z':2,
}

tableauLettres = []
for lettre in dicoLettres:
    for i in range(dicoLettres[lettre]):
        tableauLettres.append(lettre)

def bananaTirage(nb):
    tirage = ""
    tabCopie = tableauLettres[:]
    for i in range(nb):
        tirage += tabCopie.pop(randint(0,len(tabCopie)-1))
    return tirage

def dictionnaire_ordonne():
    dictionnaire = { i + 1: [] for i in range(26) }
    with open("ODS9.txt", "r") as fichier:
        for mot in fichier.read().split('\n'):
            dictionnaire[len(mot)].append(mot)
    return dictionnaire

dictionnaire = dictionnaire_ordonne()

def lettres_multiples_ok(mot: str, tirage: list[str]) -> bool:
    for lettre in mot:
        try:
            tirage.remove(lettre)
        except:
            return False
    return True

def get_ensemble_solutions(tirage: list[str]) -> list[str]:
    longueur_mot = len(tirage)
    set_tirage = set(tirage)
    while longueur_mot > 0:
        if longueur_mot < len(dictionnaire):
            for mot in dictionnaire[longueur_mot]:
                # issubset
                if set(mot) <= set_tirage and lettres_multiples_ok(mot, tirage[:]):
                    yield mot
        longueur_mot -= 1

def get_plus_long_mot(tirage: list[str]) -> str:
    return next(get_ensemble_solutions(tirage), None)

def lettres_utilisables(grille,tirage):
    w = len(grille[0])
    h = len(grille)
    for i in range(h):
        for j in range(w):
            if grille[i][j] != '.':
                if i == 0:
                    if j == 0:
                        if grille[0][1] == '.' or grille[1][0] == '.':
                            yield [grille[i][j]] + tirage
                    elif j == w-1:
                        if grille[0][w-2] == '.' or grille[1][w-1] == '.':
                            yield [grille[i][j]] + tirage
                    elif j > 0 and j < w-1:
                        if grille[0][j-1] == '.' and grille[0][j+1] == '.' or grille[1][j] == '.':
                            yield [grille[i][j]] + tirage
                elif i == h-1:
                    if j == 0:
                        if grille[h-1][1] == '.' or grille[h-2][0] == '.':
                            yield [grille[i][j]] + tirage
                    elif j == w-1:
                        if grille[h-1][w-2] == '.' or grille[h-2][w-1] == '.':
                            yield [grille[i][j]] + tirage
                    elif j > 0 and j < w-1:
                        if grille[h-1][j-1] == '.' and grille[h-1][j+1] == '.' or grille[h-2][j] == '.':
                            yield [grille[i][j]] + tirage
                elif i > 0 and i < h-1:
                    if j == 0:
                        if grille[i-1][0] == '.' and grille[i+1][0] == '.' or grille[i][1] == '.':
                            yield [grille[i][j]] + tirage
                    elif j == w-1:
                        if grille[i-1][w-1] == '.' and grille[i+1][w-1] == '.' or grille[i][w-2] == '.':
                            yield [grille[i][j]] + tirage
                    elif j > 0 and j < w-1:
                        if grille[i][j-1] == '.' and grille[i][j+1] == '.' or grille[i-1][j] == '.' and grille[i+1][j] == '.':
                            yield [grille[i][j]] + tirage

def get_mot_connexe(tirage):
    for mot in get_ensemble_solutions(tirage):
        if tirage[0] in mot:
            yield mot

def ajout_mot_grille(mot,grille,tirage):
    taille_mot = len(mot)
    if taille_mot == 0:
        return grille
    w = len(grille[0])
    h = len(grille)
    new_grille = [line[:] for line in grille]
    lettre_grille = tirage[0]
    ligne_lettre = []
    colonne_lettre = []
    sens = []
    for i in range(h-1):
        for j in range(w-1):
            if grille[i][j] == lettre_grille:
                if i == 0:
                    if j == 0:
                        if (grille[0][1] == '.'):
                            ligne_lettre.append(i)
                            colonne_lettre.append(j)
                            sens.append(0)
                        elif (grille[1][0] == '.'):
                            ligne_lettre.append(i)
                            colonne_lettre.append(j)
                            sens.append(1)
                    elif j == h-1:
                        if (grille[0][h-2] == '.'):
                            ligne_lettre.append(i)
                            colonne_lettre.append(j)
                            sens.append(0)
                        elif (grille[1][h-1] == '.'):
                            ligne_lettre.append(i)
                            colonne_lettre.append(j)
                            sens.append(1)
                    else:
                        if (grille[0][j-1] == '.' and grille[0][j+1] == '.'):
                            ligne_lettre.append(i)
                            colonne_lettre.append(j)
                            sens.append(0)
                        elif (grille[1][j] == '.'):
                            ligne_lettre.append(i)
                            colonne_lettre.append(j)
                            sens.append(1)
                elif i == h-1:
                    if j == 0:
                        if (grille[h-1][1] == '.'):
                            ligne_lettre.append(i)
                            colonne_lettre.append(j)
                            sens.append(0)
                        elif (grille[h-2][0] == '.'):
                            ligne_lettre.append(i)
                            colonne_lettre.append(j)
                            sens.append(1)
                    elif j == h-1:
                        if (grille[h-1][h-2] == '.'):
                            ligne_lettre.append(i)
                            colonne_lettre.append(j)
                            sens.append(0)
                        elif (grille[h-2][h-1] == '.'):
                            ligne_lettre.append(i)
                            colonne_lettre.append(j)
                            sens.append(1)
                    else:
                        if (grille[h-1][j-1] == '.' and grille[h-1][j+1] == '.'):
                            ligne_lettre.append(i)
                            colonne_lettre.append(j)
                            sens.append(0)
                        elif (grille[h-2][j] == '.'):
                            ligne_lettre.append(i)
                            colonne_lettre.append(j)
                            sens.append(1)
                else:
                    if j == 0:
                        if (grille[i-1][0] == '.' and grille[i+1][0] == '.'):
                            ligne_lettre.append(i)
                            colonne_lettre.append(j)
                            sens.append(1)
                        elif (grille[i][1] == '.'):
                            ligne_lettre.append(i)
                            colonne_lettre.append(j)
                            sens.append(0)
                    elif j == h-1:
                        if (grille[i-1][h-1] == '.' and grille[i+1][h-1] == '.'):
                            ligne_lettre.append(i)
                            colonne_lettre.append(j)
                            sens.append(1)
                        elif (grille[i][h-2] == '.'):
                            ligne_lettre.append(i)
                            colonne_lettre.append(j)
                            sens.append(0)
                    else:
                        if (grille[i][j-1] == '.' and grille[i][j+1] == '.'):
                            ligne_lettre.append(i)
                            colonne_lettre.append(j)
                            sens.append(0)
                        elif (grille[i-1][j] == '.' and grille[i+1][j] == '.'):
                            ligne_lettre.append(i)
                            colonne_lettre.append(j)
                            sens.append(1)

    emplacement_lettre_initiale = -1
    for i in range(taille_mot):
        if mot[i] == lettre_grille:
            emplacement_lettre_initiale = i
    if emplacement_lettre_initiale == -1:
        return grille
    for j in range(len(ligne_lettre)):
        emp_let_temp = []
        for i in range(taille_mot):
            if sens[j] == 0:
                emp_let_temp.append((
                    ligne_lettre[j],
                    colonne_lettre[j] + i - emplacement_lettre_initiale
                ))
            else:
                emp_let_temp.append((
                    ligne_lettre[j] + i - emplacement_lettre_initiale,
                    colonne_lettre[j]
                ))

        for k, (ligne, colone) in enumerate(emp_let_temp):
            if k == emplacement_lettre_initiale:
                continue
            if ligne == 0:
                if colone == 0:
                    if ligne+1 == ligne_lettre[j]:
                        if grille[ligne][colone+1] != '.':
                            break
                    elif colone+1 == colonne_lettre[j]:
                        if grille[ligne+1][colone] != '.':
                            break
                    else:
                        if grille[ligne+1][colone] != '.' or grille[ligne][colone+1] != '.':
                            break
                elif colone == w-1:
                    if ligne+1 == ligne_lettre[j]:
                        if grille[ligne][colone-1] != '.':
                            break
                    elif colone-1 == colonne_lettre[j]:
                        if grille[ligne+1][colone] != '.':
                            break
                    else:
                        if grille[ligne][colone-1] != '.' or grille[ligne+1][colone] != '.':
                            break
                elif 0 < colone < w-1:
                    if colone-1 == colonne_lettre[j]:
                        if grille[ligne+1][colone] != '.' or grille[ligne][colone+1] != '.':
                            break
                    elif colone+1 == colonne_lettre[j]:
                        if grille[ligne+1][colone] != '.' or grille[ligne][colone-1] != '.':
                            break
                    elif ligne+1 == ligne_lettre[j]:
                        if grille[ligne][colone-1] != '.' or grille[ligne][colone+1] != '.':
                            break
                    else:
                        if grille[ligne+1][colone] != '.' or grille[ligne][colone-1] != '.' or grille[ligne][colone+1] != '.':
                            break
            elif ligne == h-1:
                if colone == 0:
                    if ligne-1 == ligne_lettre[j]:
                        if grille[ligne][colone+1] != '.':
                            break
                    elif colone+1 == colonne_lettre[j]:
                        if grille[ligne-1][colone] != '.':
                            break
                    else:
                        if grille[ligne][colone+1] != '.' or grille[ligne-1][colone] != '.':
                            break
                elif colone == w-1:
                    if colone-1 == ligne_lettre[j]: # NOTE: !!!!!!!! MISSTAKE
                        if grille[ligne-1][colone] != '.':
                            break
                    elif ligne-1 == ligne_lettre[j]:
                        if grille[ligne][colone-1] != '.':
                            break
                    else:
                        if grille[ligne-1][colone] != '.' or grille[ligne][colone-1] != '.':
                            break
                elif 0 < colone < w-1:
                    if colone-1 == colonne_lettre[j]:
                        if grille[ligne-1][colone] != '.' or grille[ligne][colone+1] != '.':
                            break
                    elif colone+1 == colonne_lettre[j]:
                        if grille[ligne-1][colone] != '.' or grille[ligne][colone-1] != '.':
                            break
                    elif ligne-1 == ligne_lettre[j]:
                        if grille[ligne][colone-1] != '.' or grille[ligne][colone+1] != '.':
                            break
                    else:
                        if grille[ligne-1][colone] != '.' or grille[ligne][colone-1] != '.' or grille[ligne][colone+1] != '.':
                            break
            elif 0 < ligne < h-1:
                if colone == 0:
                    if ligne-1 == ligne_lettre[j]:
                        if grille[ligne+1][colone] != '.' or grille[ligne][colone+1] != '.':
                            break
                    elif ligne+1 == ligne_lettre[j]:
                        if grille[ligne-1][colone] != '.' or grille[ligne][colone+1] != '.':
                            break
                    elif colone+1 == ligne_lettre[j]:
                        if grille[ligne-1][colone] != '.' or grille[ligne+1][colone] != '.':
                            break
                    else:
                        if grille[ligne-1][colone] != '.' or grille[ligne+1][colone] != '.' or grille[ligne][colone+1] != '.':
                            break
                elif colone == w-1:
                    if ligne-1 == ligne_lettre[j]:
                        if grille[ligne+1][colone] != '.' or grille[ligne][colone-1] != '.':
                            break
                    elif ligne+1 == ligne_lettre[j]:
                        if grille[ligne-1][colone] != '.' or grille[ligne][colone-1] != '.':
                            break
                    elif colone-1 == ligne_lettre[j]:
                        if grille[ligne-1][colone] != '.' or grille[ligne+1][colone] != '.':
                            break
                    else:
                        if grille[ligne-1][colone] != '.' or grille[ligne+1][colone] != '.' or grille[ligne][colone-1] != '.':
                            break
                elif 0 < colone < w-1:
                    if colone+1 == colonne_lettre[j]:
                        if grille[ligne-1][colone] != '.' or grille[ligne+1][colone] != '.' or grille[ligne][colone-1] != '.':
                            break
                    elif colone-1 == colonne_lettre[j]:
                        if grille[ligne-1][colone] != '.' or grille[ligne+1][colone] != '.' or grille[ligne][colone+1] != '.':
                            break
                    elif ligne-1 == ligne_lettre[j]:
                        if grille[ligne+1][colone] != '.' or grille[ligne][colone-1] != '.' or grille[ligne][colone+1] != '.':
                            break
                    elif ligne+1 == ligne_lettre[j]:
                        if grille[ligne-1][colone] != '.' or grille[ligne][colone-1] != '.' or grille[ligne][colone+1] != '.':
                            break
                    else:
                        if grille[ligne-1][colone] != '.' or grille[ligne+1][colone] != '.' or grille[ligne][colone-1] != '.' or grille[ligne][colone+1] != '.':
                            break

        else:
            for i in range(taille_mot):
                if emp_let_temp[i][0] < 0:
                    new_grille.insert(i, ['.'] * w)
                    h += 1
                elif (
                    emp_let_temp[i][0] - emp_let_temp[0][0] > h-1 and emp_let_temp[0][0] < 0
                    or emp_let_temp[i][0] > h-1
                ):
                    new_grille.append(['.'] * w)
                    h += 1
                elif emp_let_temp[i][1] < 0:
                    for line in new_grille:
                        line.insert(i, '.')
                    w += 1
                elif (
                    emp_let_temp[i][1] - emp_let_temp[0][1] > w-1 and emp_let_temp[0][1] < 0
                    or emp_let_temp[i][1] > w-1
                ):
                    for line in new_grille:
                        line.append('.')
                    w += 1

            for i in range(taille_mot):
                if sens[j]==0:
                    if emp_let_temp[0][1] < 0:
                        new_grille[emp_let_temp[i][0]][emp_let_temp[i][1] + emplacement_lettre_initiale - emp_let_temp[emplacement_lettre_initiale][1]] = mot[i]
                    else:
                        new_grille[emp_let_temp[i][0]][emp_let_temp[i][1]] = mot[i]
                elif sens[j]==1:
                    if emp_let_temp[0][0] < 0:
                        new_grille[emp_let_temp[i][0] + emplacement_lettre_initiale - emp_let_temp[emplacement_lettre_initiale][0]][emp_let_temp[i][1]] = mot[i]
                    else:
                        new_grille[emp_let_temp[i][0]][emp_let_temp[i][1]] = mot[i]
            return new_grille
    return grille

def banana_rec(grille,tirage,depth=0):
    if len(tirage) <= 1:
        return grille
    for mot in get_mot_connexe(tirage):
        new_grille = [line[:] for line in grille]
        new_grille = ajout_mot_grille(mot,new_grille,tirage)
        if new_grille != grille:
            new_tirage = tirage[:]
            for lettre in mot:
                new_tirage.remove(lettre)
            for tirage_connexe in lettres_utilisables(new_grille,new_tirage):
                grille_banana_connexe = banana_rec(new_grille,tirage_connexe,depth+1)
                if grille_banana_connexe:
                    return grille_banana_connexe

def bananaSolver(listeTirage):
    tirage = list(listeTirage)
    grille = [[],[]]
    for mot in get_ensemble_solutions(tirage):
        new_grille = [line[:] for line in grille]
        new_tirage = tirage[:]
        for lettre in mot:
            new_tirage.remove(lettre)
            new_grille[0].append(lettre)
            new_grille[1].append('.')
        for tirage_connexe in lettres_utilisables(new_grille,new_tirage):
            grille_banana_connexe = banana_rec(new_grille,tirage_connexe)
            if grille_banana_connexe:
                return grille_banana_connexe
    return ["Le tirage n'a pas de solution optimale"]

def afficherGrille(grille):
    for ligne in grille:
        print(''.join(ligne).replace('.', ' '))

if __name__ == '__main__':
    # tirage = "AAAAAAAAAAAAAABBBCCCCDDDDEEEEEEEEEEEEEEEEEEEEEFFFGGHHIIIIIIIIIIIIJKLLLLLLLMMMMNNNNNNNNNOOOOOOOOOPPPQRRRRRRRRRSSSSSSSSSTTTTTTTTTUUUUUUUUUVVVWXYZZ"
    tirage = "AAEPEE"
    import cProfile
    with cProfile.Profile() as pr:
        grille = bananaSolver(tirage)
        pr.dump_stats('stats.prof') # snakeviz stats.prof
    afficherGrille(grille)
