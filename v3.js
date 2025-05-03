/**
 * 
 * This algorithm wasn't made by me !!!
 * 
 * I just optimized it a lot :)
 * 
**/
const fs = require('fs');

const dictionary = getSortedDict();
const squaresHand = ['OARR', 'CXEE', 'GCOO', 'DXEE', 'JXEE', 'LXEE', 'MXEE', 'GMOO', 'GROO', 'GUOO'];

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

function getSortedDict() {
    const dictionary = [];
    for (let i = 0; i < 26; i++)
        dictionary.push([]);
    const content = fs.readFileSync('ODS9.txt', 'utf8');
    for (const word of content.split('\n'))
        dictionary[word.length].push(word);
    return dictionary;
}

function isMultipleLettersOk(word, hand) {
    for (let letter of word) {
        const i = hand.indexOf(letter);
        if (i == -1)
            return false;
        hand.splice(i, 1);
    }
    return true;
}

function isSubset(setA, setB) {
    for (let elem of setA)
        if (!setB.has(elem))
            return false;
    return true;
}

function* getSolutions(hand) {
    let size = hand.length;
    const handSet = new Set(hand);
    while (size > 0) {
        if (size < dictionary.length)
            for (let word of dictionary[size])
                if (isSubset(word, handSet) && isMultipleLettersOk(word, copy(hand)))
                    yield word;
        size--;
    }
}

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
        if (word.includes(hand[0]))
            yield word;
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

function bananaSolver(handString) {
    if (handString.length == 4)
        main: for (const squareHand of squaresHand) {
            const count = new Uint8Array(26);
            for (let i = 0; i < 4; i++) {
                count[squareHand.charCodeAt(i) - 65]++;
                count[handString.charCodeAt(i) - 65]--;
            }
            for (let i = 0; i < 26; i++)
                if (count[i])
                    continue main;
            return [
                [squareHand[0], squareHand[2]],
                [squareHand[2], squareHand[1]]
            ];
        }

    for (let word of getSolutions(copy(handString))) {
        const s = word.length + 2;
        const newGrid = [
            new Array(s),
            new Array(s),
            new Array(s)
        ];
        const newHand = copy(handString);
        let i = 1;
        for (let letter of word)
            newHand.splice(newHand.indexOf(newGrid[1][i++] = letter), 1);
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


const handString = "AAAAAAAAAAAAAABBBCCCCDDDDEEEEEEEEEEEEEEEEEEEEEFFFGGHHIIIIIIIIIIIIJKLLLLLLLMMMMNNNNNNNNNOOOOOOOOOPPPQRRRRRRRRRSSSSSSSSSTTTTTTTTTUUUUUUUUUVVVWXYZZ";
const start = performance.now();
const grid = bananaSolver(handString);
const end = performance.now();

if (grid)
    showGrid(grid);
else
    console.log("No grid found...");

console.log(end - start, "ms");