/**
 * 
 * This algorithm wasn't made by me !!!
 * 
 * I just optimized it a lot :)
 * 
**/
const fs = require('fs');

const randint = (a, b) => a + Math.floor((b - a) * Math.random());

const lettersFrequencies = {
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

const lettersTable = [];
for (const [letter, count] of Object.entries(lettersFrequencies))
    for (let i = 0; i < count; i++)
        lettersTable.push(letter);


function gridCopy(arr) {
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
    let hand = ""
    let tabCopie = copy(lettersTable);
    for (var i = 0; i < nb; i++)
        hand += tabCopie.splice(randint(0, tabCopie.length - 1), 1)[0];
    return hand;
}

function getSortedDict() {
    const dictionary = [];
    for (let i = 0; i < 26; i++)
        dictionary.push(new Set);
        // dictionary.push([]);
    const content = fs.readFileSync('ODS9.txt', 'utf8');
    for (const word of content.split('\n'))
        dictionary[word.length].add(word);
        // dictionary[word.length].push(word);
    return dictionary;
}

const dictionary = getSortedDict();
for (let i = 0; i < 26; i++)
    console.log(dictionary[i].size);

function isMultipleLettersOk(word, hand) {
    for (let letter of word) {
        const i = hand.indexOf(letter);
        if (i === -1)
            return false;
        hand.splice(i, 1); // TODO: use object with count instead of array
    }
    return true;
}

function isSubset(setA, setB) { // TODO: optimize
    /* TODO: cache words letters count
    
         dictionary = Map(word: Array(count, ...))

         [0, 0, 0, 0, ...]
          A  B  C  D  ...
    */
    for (let elem of setA)
        if (!setB.has(elem))
            return false;
    return true;
}

function* getSolutions(hand) {
    let size = hand.length;
    const handSet = new Set(hand);
    while (size > 0) {
        if (size < dictionary.length) {
            for (let word of dictionary[size]) // const [word, count]
                if (isSubset(word, handSet) && isMultipleLettersOk(word, copy(hand)))
                    // TODO: make 1 single check loop
                    yield word;
                // TODO: else delete from dictionnary
        }
        size--;
    }
}

const getLongestWord = hand => getSolutions(hand).next().value;

function* usableLetters(grid,hand) {
    const w = grid[0].length;
    const h = grid.length;
    for (var y = 0; y < h; y++)
    for (var x = 0; x < w; x++) {
        const v = grid[y][x];
        if (v && (!grid[y][x-1] && !grid[y][x+1] || !grid[y-1]?.[x] && !grid[y+1]?.[x]))
            yield v;
    }
}

function* getConnectedWord(hand) {
    for (let word of getSolutions(hand))
        if (word.includes(hand[0])) {
            yield word;
        }
}

function* getSlots(w, h, grid, letterGrille) {
    // yields [column, line, direction]
    for (let y = 0; y < h - 1; y++)
    for (let x = 0; x < w - 1; x++)
        if (grid[y][x] == letterGrille) {
            if (!grid[y][x-1] && !grid[y][x+1])
                yield [x, y, 0];
            else if (!grid[y-1]?.[x] && !grid[y+1]?.[x])
                yield [x, y, 1];
        }
}

function placeWord(word, grid, hand) {
    const wordLength = word.length;
    if (wordLength == 0)
        return;
    let w = grid[0].length,
        h = grid.length;
    const newGrid = gridCopy(grid),
          letterGrille = hand[0];

    let initLetterIndex = -1;
    for (let i = 0; i < wordLength; i++)
        if (word[i] == letterGrille)
            initLetterIndex = i;

    if (initLetterIndex == -1)
        return;

    let tempPosition = new Array(wordLength);
    for (let [columnInit, lineInit, direction] of getSlots(w, h, grid, letterGrille)) {
        for (let i = 0; i < wordLength; i++) {
            tempPosition[i] = [lineInit, columnInit];
            tempPosition[i][1 - direction] += i - initLetterIndex;
        }

        let k = 0;
        for (let [line, column] of tempPosition) {
            if (k == initLetterIndex) {
                k++;
                continue;
            }
            const up = grid[line - 1]?.[column],
                  down = grid[line + 1]?.[column],
                  left = grid[line]?.[column - 1],
                  right = grid[line]?.[column + 1];

            if (column + 1 == columnInit) {
                if (up || down || left) break;
            } else if (column - 1 == columnInit) {
                if (up || down || right) break;
            } else if (line - 1 == lineInit) {
                if (down || left || right) break;
            } else if (line + 1 == lineInit) {
                if (up || left || right) break;
            } else {
                if (up || down || left || right) break;
            }
            k++;
        }

        if (k == tempPosition.length) {
            for (let i = 0; i < wordLength; i++) {
                if (tempPosition[i][0] < 0) {
                    newGrid.unshift(new Array(w));
                    h++;
                } else if (
                    tempPosition[i][0] - tempPosition[0][0] >= h && tempPosition[0][0] < 0
                    || tempPosition[i][0] >= h
                ) {
                    newGrid.push(new Array(w));
                    h++;
                } else if (tempPosition[i][1] < 0) {
                    for (let line of newGrid)
                        line.unshift(undefined);
                    w++;
                } else if (
                    tempPosition[i][1] - tempPosition[0][1] >= w && tempPosition[0][1] < 0
                    || tempPosition[i][1] >= w
                ) {
                    for (let line of newGrid)
                        line.push(undefined);
                    w++;
                }
            }
            const inx = (1 - direction) * (initLetterIndex - tempPosition[initLetterIndex][1]),
                  iny = direction * (initLetterIndex - tempPosition[initLetterIndex][0]);
            for (let i = 0; i < wordLength; i++) {
                if (tempPosition[0][1-direction] < 0)
                    newGrid[tempPosition[i][0] + iny][tempPosition[i][1] + inx] = word[i];
                else
                    newGrid[tempPosition[i][0]][tempPosition[i][1]] = word[i];
            }
            return newGrid;
        }
    }
}

function bananaRec(grid, hand, depth=0) {
    if (hand.length <= 1)
        return grid;
    for (let word of getConnectedWord(hand)) {
        const newGrid = placeWord(word, gridCopy(grid), hand);
        // NOTE: there can be many placements so need something to fix it
        if (newGrid) {
            const newHand = copy(hand);
            for (let letter of word)
                newHand.splice(newHand.indexOf(letter), 1);
            for (let letter of usableLetters(newGrid, newHand)) {
                const recGrid = bananaRec(newGrid, [letter].concat(newHand), depth+1);
                if (recGrid)
                    return recGrid;
            }
        }
    }
}

function bananaSolver(hand) {
    for (let word of getSolutions(hand)) {
        const newGrid = [[], []];
        const newHand = copy(hand);
        for (let letter of word) {
            newHand.splice(newHand.indexOf(letter), 1);
            newGrid[0].push(letter);
            newGrid[1].push(undefined);
        }
        for (let letter of usableLetters(newGrid, newHand)) {
            const recGrid = bananaRec(newGrid, [letter].concat(newHand));
            if (recGrid)
                return recGrid;
        }
    }
}

function showGrid(grid) {
    for (let line of grid)
        console.log(line.map(x => x || ' ').join(''));
}


let tt = 0;
const hand = copy("AAAAAAAAAAAAAABBBCCCCDDDDEEEEEEEEEEEEEEEEEEEEEFFFGGHHIIIIIIIIIIIIJKLLLLLLLMMMMNNNNNNNNNOOOOOOOOOPPPQRRRRRRRRRSSSSSSSSSTTTTTTTTTUUUUUUUUUVVVWXYZZ");
// const hand = copy("GOOU");
const start = performance.now();
const grid = bananaSolver(hand);
const end = performance.now();

if (grid)
    showGrid(grid);
else
    console.log("Le main n'a pas de solution optimale");

console.log(end - start, "ms"); // 105 ms
console.log(tt, "ms wasted potentially");
// 0.6% for Hands
// 1.6% for Placing
// 2.5% for JSON.stringify
// 0.9% for Grid Copy
// 52.5% for Is Subset
// 0.2% for Multiple Letters Ok
