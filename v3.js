/**
 * 
 * This algorithm wasn't made by me !!!
 * 
 * I just optimized it a lot :)
 * 
**/
const fs = require('fs');

const randint = (a, b) => a + Math.floor((b - a) * Math.random());

const dicoLettres = {
    'A': 14,
    'B': 3,
    'C': 4,
    'D': 4,
    'E': 21,
    'F': 3,
    'G': 2,
    'H': 2,
    'I': 12,
    'J': 1,
    'K': 1,
    'L': 7,
    'M': 4,
    'N': 9,
    'O': 9,
    'P': 3,
    'Q': 1,
    'R': 9,
    'S': 9,
    'T': 9,
    'U': 9,
    'V': 3,
    'W': 1,
    'X': 1,
    'Y': 1,
    'Z': 2,
};
let longueur_max = 0;
let longueur_min = Infinity;

const tableauLettres = []
for (const [lettre, count] of Object.entries(dicoLettres)) {
    for (let i = 0; i < count; i++) {
        tableauLettres.push(lettre)
    }
}

function copyGrille(arr) {
    let newArr = new Array(arr.length);
    for (let i = 0; i < arr.length; i++) {
        let row = arr[i];
        let newRow = new Array(row.length);
        for (let j = 0; j < row.length; j++)
            newRow[j] = row[j];
        newArr[i] = newRow;
    }
    return newArr;
}
function copy(arr) {
    let newArr = new Array(arr.length);
    for (let i = 0; i < arr.length; i++)
        newArr[i] = arr[i];
    return newArr;
}

function bananaTirage(nb) {
    let tirage = ""
    let tabCopie = copy(tableauLettres);
    for (var i = 0; i < nb; i++)
        tirage += tabCopie.splice(randint(0, tabCopie.length - 1), 1)[0];
    return tirage;
}

function dictionnaire_ordonne() {
    const dictionnaire = [];
    for (let i = 0; i < 26; i++)
        dictionnaire.push([])
    const content = fs.readFileSync('ODS9.txt', 'utf8');
    for (const mot of content.split('\n'))
        dictionnaire[mot.length].push(mot);
    return dictionnaire;
}

const dictionnaire = dictionnaire_ordonne();

function lettres_multiples_ok(mot, tirage) {
    for (let lettre of mot) {
        const i = tirage.indexOf(lettre);
        if (i === -1)
            return false;
        tirage.splice(i, 1); // TODO: use object with count instead of array
    }
    return true;
}

function isSubset(setA, setB) { // TODO: optimize
    for (let elem of setA) {
        if (!setB.has(elem))
            return false;
    }
    return true;
}

function* get_ensemble_solutions(tirage) {
    let longueur_mot = tirage.length;
    const set_tirage = new Set(tirage);
    while (longueur_mot > 0) {
        if (longueur_mot < dictionnaire.length) {
            for (let mot of dictionnaire[longueur_mot]) {
                if (isSubset(mot, set_tirage) && lettres_multiples_ok(mot, copy(tirage)))
                    yield mot
            }
        }
        longueur_mot--;
    }
}

const get_plus_long_mot = tirage => get_ensemble_solutions(tirage).next().value;

function* lettres_utilisables(grille,tirage) {
    const w = grille[0].length;
    const h = grille.length;
    for (var i = 0; i < h; i++) {
        for (var j = 0; j < w; j++) {
            const v = grille[i][j];
            if (v != '.') {
                if (i == 0) {
                    if (j == 0) {
                        if (grille[0][1] == '.' || grille[1][0] == '.')
                            yield v;
                    } else if (j == w-1) {
                        if (grille[0][w-2] == '.' || grille[1][w-1] == '.')
                            yield v;
                    } else if (j > 0 && j < w-1) {
                        if (grille[0][j-1] == '.' && grille[0][j+1] == '.' || grille[1][j] == '.')
                            yield v;
                    }
                } else if (i == h-1) {
                    if (j == 0) {
                        if (grille[h-1][1] == '.' || grille[h-2][0] == '.')
                            yield v;
                    } else if (j == w-1) {
                        if (grille[h-1][w-2] == '.' || grille[h-2][w-1] == '.')
                            yield v;
                    } else if (j > 0 && j < w-1) {
                        if (grille[h-1][j-1] == '.' && grille[h-1][j+1] == '.' || grille[h-2][j] == '.')
                            yield v;
                    }
                } else if (i > 0 && i < h-1) {
                    if (j == 0) {
                        if (grille[i-1][0] == '.' && grille[i+1][0] == '.' || grille[i][1] == '.')
                            yield v;
                    } else if (j == w-1) {
                        if (grille[i-1][w-1] == '.' && grille[i+1][w-1] == '.' || grille[i][w-2] == '.')
                            yield v;
                    } else if (j > 0 && j < w-1) {
                        if (grille[i][j-1] == '.' && grille[i][j+1] == '.' || grille[i-1][j] == '.' && grille[i+1][j] == '.')
                            yield v;
                    }
                }
            }
        }
    }
}

function* get_mot_connexe(tirage) {
    for (let mot of get_ensemble_solutions(tirage))
        if (mot.includes(tirage[0]))
            yield mot;
}

function ajout_mot_grille(mot, grille, tirage) {
    const taille_mot = mot.length;
    if (taille_mot == 0)
        return grille;
    let w = grille[0].length,
        h = grille.length;
    const new_grille = copyGrille(grille),
          lettre_grille = tirage[0],
          ligne_lettre = [],
          colonne_lettre = [],
          sens = [];

    const slots = []; // colone, ligne, sens
    for (let y = 0; y < h - 1; y++) {
        for (let x = 0; x < w - 1; x++) {
            if (grille[y][x] == lettre_grille) {
                if (y == 0) {
                    if (x == 0) {
                        if (grille[0][1] == '.')                                 slots.push([x, y, 0]);
                        else if (grille[1][0] == '.')                            slots.push([x, y, 1]);
                    } else if (x == h-1) {
                        if (grille[0][h-2] == '.')                               slots.push([x, y, 0]);
                        else if (grille[1][h-1] == '.')                          slots.push([x, y, 1]);
                    } else {
                        if (grille[0][x-1] == '.' && grille[0][x+1] == '.')      slots.push([x, y, 0]);
                        else if (grille[1][x] == '.')                            slots.push([x, y, 1]);
                    }
                } else if (y == h-1) {
                    if (x == 0) {
                        if (grille[h-1][1] == '.')                               slots.push([x, y, 0]);
                        else if (grille[h-2][0] == '.')                          slots.push([x, y, 1]);
                    } else if (x == h-1) {
                        if (grille[h-1][h-2] == '.')                             slots.push([x, y, 0]);
                        else if (grille[h-2][h-1] == '.')                        slots.push([x, y, 1]);
                    } else {
                        if (grille[h-1][x-1] == '.' && grille[h-1][x+1] == '.')  slots.push([x, y, 0]);
                        else if (grille[h-2][x] == '.')                          slots.push([x, y, 1]);
                    }
                } else {
                    if (x == 0) {
                        if (grille[y-1][0] == '.' && grille[y+1][0] == '.')      slots.push([x, y, 1]);
                        else if (grille[y][1] == '.')                            slots.push([x, y, 0]);
                    } else if (x == h-1) {
                        if (grille[y-1][h-1] == '.' && grille[y+1][h-1] == '.')  slots.push([x, y, 1]);
                        else if (grille[y][h-2] == '.')                          slots.push([x, y, 0]);
                    } else {
                        if (grille[y][x-1] == '.' && grille[y][x+1] == '.')      slots.push([x, y, 0]);
                        else if (grille[y-1][x] == '.' && grille[y+1][x] == '.') slots.push([x, y, 1]);
                    }
                }
            }
        }
    }

    let emplacement_lettre_initiale = -1;
    for (let i = 0; i < taille_mot; i++)
        if (mot[i] == lettre_grille)
            emplacement_lettre_initiale = i;

    if (emplacement_lettre_initiale == -1)
        return grille;

    for (let [x, y, sens] of slots) {
        let emp_let_temp = [];
        for (let i = 0; i < taille_mot; i++) {
            if (sens)
                emp_let_temp.push([y + i - emplacement_lettre_initiale, x]);
            else
                emp_let_temp.push([y, x + i - emplacement_lettre_initiale]);
        }

        let k = 0;
        for (let [ligne, colone] of emp_let_temp) {
            if (k == emplacement_lettre_initiale) {
                k++;
                continue;
            }
            if (ligne == 0) {
                if (colone == 0) {
                    if (ligne+1 == y) {
                        if (grille[ligne][colone+1] != '.')
                            break;
                    } else if (colone+1 == x) {
                        if (grille[ligne+1][colone] != '.')
                            break;
                    } else {
                        if (grille[ligne+1][colone] != '.' || grille[ligne][colone+1] != '.')
                            break;
                    }
                } else if (colone == w-1) {
                    if (ligne+1 == y) {
                        if (grille[ligne][colone-1] != '.')
                            break;
                    } else if (colone-1 == x) {
                        if (grille[ligne+1][colone] != '.')
                            break;
                    } else {
                        if (grille[ligne][colone-1] != '.' || grille[ligne+1][colone] != '.')
                            break;
                    }
                } else if (0 < colone && colone < w-1) {
                    if (colone-1 == x) {
                        if (grille[ligne+1][colone] != '.' || grille[ligne][colone+1] != '.')
                            break;
                    } else if (colone+1 == x) {
                        if (grille[ligne+1][colone] != '.' || grille[ligne][colone-1] != '.')
                            break;
                    } else if (ligne+1 == y) {
                        if (grille[ligne][colone-1] != '.' || grille[ligne][colone+1] != '.')
                            break;
                    } else {
                        if (grille[ligne+1][colone] != '.' || grille[ligne][colone-1] != '.' || grille[ligne][colone+1] != '.')
                            break;
                    }
                }
            } else if (ligne == h-1) {
                if (colone == 0) {
                    if (ligne-1 == y) {
                        if (grille[ligne][colone+1] != '.')
                            break;
                    } else if (colone+1 == x) {
                        if (grille[ligne-1][colone] != '.')
                            break;
                    } else {
                        if (grille[ligne][colone+1] != '.' || grille[ligne-1][colone] != '.')
                            break;
                    }
                } else if (colone == w-1) {
                    if (colone-1 == y) { // TODO: misstake?
                        if (grille[ligne-1][colone] != '.')
                            break;
                    } else if (ligne-1 == y) {
                        if (grille[ligne][colone-1] != '.')
                            break;
                    } else {
                        if (grille[ligne-1][colone] != '.' || grille[ligne][colone-1] != '.')
                            break;
                    }
                } else if (0 < colone && colone < w-1) {
                    if (colone-1 == x) {
                        if (grille[ligne-1][colone] != '.' || grille[ligne][colone+1] != '.')
                            break;
                    } else if (colone+1 == x) {
                        if (grille[ligne-1][colone] != '.' || grille[ligne][colone-1] != '.')
                            break;
                    } else if (ligne-1 == y) {
                        if (grille[ligne][colone-1] != '.' || grille[ligne][colone+1] != '.')
                            break;
                    } else {
                        if (grille[ligne-1][colone] != '.' || grille[ligne][colone-1] != '.' || grille[ligne][colone+1] != '.')
                            break;
                    }
                }
            } else if (0 < ligne && ligne < h-1) {
                if (colone == 0) {
                    if (ligne-1 == y) {
                        if (grille[ligne+1][colone] != '.' || grille[ligne][colone+1] != '.')
                            break;
                    } else if (ligne+1 == y) {
                        if (grille[ligne-1][colone] != '.' || grille[ligne][colone+1] != '.')
                            break;
                    } else if (colone+1 == y) {
                        if (grille[ligne-1][colone] != '.' || grille[ligne+1][colone] != '.')
                            break;
                    } else {
                        if (grille[ligne-1][colone] != '.' || grille[ligne+1][colone] != '.' || grille[ligne][colone+1] != '.')
                            break;
                    }
                } else if (colone == w-1) {
                    if (ligne-1 == y) {
                        if (grille[ligne+1][colone] != '.' || grille[ligne][colone-1] != '.')
                            break;
                    } else if (ligne+1 == y) {
                        if (grille[ligne-1][colone] != '.' || grille[ligne][colone-1] != '.')
                            break;
                    } else if (colone-1 == y) {
                        if (grille[ligne-1][colone] != '.' || grille[ligne+1][colone] != '.')
                            break;
                    } else {
                        if (grille[ligne-1][colone] != '.' || grille[ligne+1][colone] != '.' || grille[ligne][colone-1] != '.')
                            break;
                    }
                } else if (0 < colone && colone < w-1) {
                    if (colone+1 == x) {
                        if (grille[ligne-1][colone] != '.' || grille[ligne+1][colone] != '.' || grille[ligne][colone-1] != '.')
                            break;
                    } else if (colone-1 == x) {
                        if (grille[ligne-1][colone] != '.' || grille[ligne+1][colone] != '.' || grille[ligne][colone+1] != '.')
                            break;
                    } else if (ligne-1 == y) {
                        if (grille[ligne+1][colone] != '.' || grille[ligne][colone-1] != '.' || grille[ligne][colone+1] != '.')
                            break;
                    } else if (ligne+1 == y) {
                        if (grille[ligne-1][colone] != '.' || grille[ligne][colone-1] != '.' || grille[ligne][colone+1] != '.')
                            break;
                    } else {
                        if (grille[ligne-1][colone] != '.' || grille[ligne+1][colone] != '.' || grille[ligne][colone-1] != '.' || grille[ligne][colone+1] != '.')
                            break;
                    }
                }
            }
            k++;
        }

        if (k == emp_let_temp.length) {
            for (let i = 0; i < taille_mot; i++) {
                if (emp_let_temp[i][0] < 0) {
                    new_grille.unshift(copy('.'.repeat(w))); // new_grille.splice(i, 0, copy('.'.repeat(w)));
                    h++;
                } else if (
                    emp_let_temp[i][0] - emp_let_temp[0][0] >= h && emp_let_temp[0][0] < 0
                    || emp_let_temp[i][0] >= h
                ) {
                    new_grille.push(copy('.'.repeat(w)));
                    h++;
                } else if (emp_let_temp[i][1] < 0) {
                    for (let line of new_grille)
                        line.unshift('.'); // line.splice(i, 0, '.');
                    w++;
                } else if (
                    emp_let_temp[i][1] - emp_let_temp[0][1] >= w && emp_let_temp[0][1] < 0
                    || emp_let_temp[i][1] >= w
                ) {
                    for (let line of new_grille)
                        line.push('.');
                    w++;
                }
            }
            for (let i = 0; i < taille_mot; i++) {
                if (sens) {
                    if (emp_let_temp[0][0] < 0)
                        new_grille[emp_let_temp[i][0] + emplacement_lettre_initiale - emp_let_temp[emplacement_lettre_initiale][0]][emp_let_temp[i][1]] = mot[i];
                    else
                        new_grille[emp_let_temp[i][0]][emp_let_temp[i][1]] = mot[i];
                } else {
                    if (emp_let_temp[0][1] < 0)
                        new_grille[emp_let_temp[i][0]][emp_let_temp[i][1] + emplacement_lettre_initiale - emp_let_temp[emplacement_lettre_initiale][1]] = mot[i];
                    else
                        new_grille[emp_let_temp[i][0]][emp_let_temp[i][1]] = mot[i];
                }
            }
            return new_grille;
        }
    }
    return grille;
}

function banana_rec(grille, tirage, depth=0) {
    if (tirage.length <= 1)
        return grille;
    for (let mot of get_mot_connexe(tirage)) {
        let new_grille = copyGrille(grille);
        new_grille = ajout_mot_grille(mot, new_grille, tirage);
        if (JSON.stringify(new_grille) != JSON.stringify(grille)) {
            let new_tirage = copy(tirage);
            for (let lettre of mot)
                new_tirage.splice(new_tirage.indexOf(lettre), 1);
            for (let lettre of lettres_utilisables(new_grille, new_tirage)) {
                let grille_banana_connexe = banana_rec(new_grille, [lettre].concat(new_tirage), depth+1);
                if (grille_banana_connexe)
                    return grille_banana_connexe;
            }
        }
    }
}

function bananaSolver(listeTirage) {
    let tirage = copy(listeTirage);
    let grille = [[],[]];
    for (let mot of get_ensemble_solutions(tirage)) {
        // console.log("-", mot);
        let new_grille = copyGrille(grille);
        let new_tirage = copy(tirage);
        for (let lettre of mot) {
            new_tirage.splice(new_tirage.indexOf(lettre), 1);
            new_grille[0].push(lettre);
            new_grille[1].push('.');
        }
        for (let lettre of lettres_utilisables(new_grille, new_tirage)) {
            let grille_banana_connexe = banana_rec(new_grille, [lettre].concat(new_tirage));
            if (grille_banana_connexe)
                return grille_banana_connexe;
        }
    }
}

function afficherGrille(grille) {
    for (let ligne of grille)
        console.log(ligne.join('').replaceAll('.', ' '));
}


const tirage = copy("AAAAAAAAAAAAAABBBCCCCDDDDEEEEEEEEEEEEEEEEEEEEEFFFGGHHIIIIIIIIIIIIJKLLLLLLLMMMMNNNNNNNNNOOOOOOOOOPPPQRRRRRRRRRSSSSSSSSSTTTTTTTTTUUUUUUUUUVVVWXYZZ");
// const tirage = copy("GOOU");

const start = performance.now();
const grille = bananaSolver(tirage);
const end = performance.now();

if (grille)
    afficherGrille(grille);
else
    console.log("Le tirage n'a pas de solution optimale");
console.log(end - start, "ms"); // 110 ms
