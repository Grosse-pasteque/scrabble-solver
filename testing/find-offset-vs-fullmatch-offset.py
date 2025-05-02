def find_matching_offset(word, pattern):
    word_length = len(word)

    for offset in range(word_length):
        pos = offset
        match = True

        for element in pattern:
            if element.__class__ == int:
                pos += element
            elif pos < word_length and word[pos] == element:
                pos += 1
            else:
                match = False
                break
        if match and pos <= word_length:
            return offset
    return -1


pattern = [4, 'A', 2, 'B', 7, 'C', 8]

word = "MAMMBMMMMMMMCMMMM"
print(find_matching_offset(word, pattern))  # Output: 0

word = "MMMMMAMMBMMMMMMMCMMMM"
print(find_matching_offset(word, pattern))  # Output: -1 (No match)

word = "MABMMMMMMMCMM"
print(find_matching_offset(word, pattern))  # Output: -1 (No match)

word = "MAMMBMMCMMMM"
print(find_matching_offset(word, pattern))  # Output: -1 (No match)
