/*
 * wordcount.c
 *
 * A small text statistics utility. Given a path to a text file, prints
 * the number of lines, words, and characters, the length of the longest
 * line, and the average word length.
 *
 * Build:  gcc -Wall -Wextra -o wordcount wordcount.c
 * Usage:  ./wordcount <path-to-text-file>
 *
 * Exit codes:
 *   0  success
 *   1  usage error
 *   2  file could not be opened
 *   3  out of memory
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define INITIAL_LINE_CAPACITY 128

/*
 * Aggregated statistics for one input file. All counts are non-negative.
 * average_word_length is 0.0 when word_count is 0.
 */
typedef struct {
    long line_count;
    long word_count;
    long char_count;
    long longest_line;
    double average_word_length;
} FileStats;

/*
 * Read one line from `stream` into a dynamically-allocated buffer.
 * The buffer grows as needed and is returned through *line_out.
 * The caller owns the returned buffer and must free() it.
 *
 * Returns the number of characters read (excluding the terminating
 * newline, if any), or -1 on end of file with no characters read,
 * or -2 on allocation failure.
 */
static long read_line(FILE *stream, char **line_out) {
    size_t capacity = INITIAL_LINE_CAPACITY;
    size_t length = 0;
    char *buffer = malloc(capacity);
    int c;

    if (buffer == NULL) {
        return -2;
    }

    while ((c = fgetc(stream)) != EOF && c != '\n') {
        if (length + 1 >= capacity) {
            capacity *= 2;
            char *resized = realloc(buffer, capacity);
            if (resized == NULL) {
                free(buffer);
                return -2;
            }
            buffer = resized;
        }
        buffer[length++] = (char)c;
    }

    if (c == EOF && length == 0) {
        free(buffer);
        *line_out = NULL;
        return -1;
    }

    buffer[length] = '\0';
    *line_out = buffer;
    return (long)length;
}

/*
 * Count the words in a null-terminated string. A "word" is a maximal
 * run of non-whitespace characters. Also adds the total length of all
 * word characters to *total_word_chars so the caller can compute the
 * average word length across an entire file.
 */
static long count_words(const char *line, long *total_word_chars) {
    long words = 0;
    int in_word = 0;
    long word_len = 0;

    for (const char *p = line; *p != '\0'; p++) {
        if (isspace((unsigned char)*p)) {
            if (in_word) {
                words++;
                *total_word_chars += word_len;
                word_len = 0;
                in_word = 0;
            }
        } else {
            in_word = 1;
            word_len++;
        }
    }
    if (in_word) {
        words++;
        *total_word_chars += word_len;
    }
    return words;
}

/*
 * Walk the input file, accumulating statistics into *stats.
 * Returns 0 on success, non-zero on error (see exit codes at top).
 */
static int analyze_file(FILE *input, FileStats *stats) {
    char *line = NULL;
    long line_length;
    long total_word_chars = 0;

    stats->line_count = 0;
    stats->word_count = 0;
    stats->char_count = 0;
    stats->longest_line = 0;
    stats->average_word_length = 0.0;

    while ((line_length = read_line(input, &line)) >= 0) {
        stats->line_count++;
        stats->char_count += line_length;
        if (line_length > stats->longest_line) {
            stats->longest_line = line_length;
        }
        stats->word_count += count_words(line, &total_word_chars);
        free(line);
        line = NULL;
    }

    if (line_length == -2) {
        return 3;
    }

    if (stats->word_count > 0) {
        stats->average_word_length =
        (double)total_word_chars / (double)stats->word_count;
    }

    return 0;
}

/*
 * Print a FileStats to stdout in a fixed, human-readable layout.
 */
static void print_stats(const char *path, const FileStats *stats) {
    printf("File:                %s\n", path);
    printf("Lines:               %ld\n", stats->line_count);
    printf("Words:               %ld\n", stats->word_count);
    printf("Characters:          %ld\n", stats->char_count);
    printf("Longest line:        %ld\n", stats->longest_line);
    printf("Average word length: %.2f\n", stats->average_word_length);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <path-to-text-file>\n", argv[0]);
        return 1;
    }

    const char *path = argv[1];
    FILE *input = fopen(path, "r");
    if (input == NULL) {
        fprintf(stderr, "Error: could not open '%s'\n", path);
        return 2;
    }

    FileStats stats;
    int result = analyze_file(input, &stats);
    fclose(input);

    if (result != 0) {
        fprintf(stderr, "Error: out of memory while reading file\n");
        return result;
    }

    print_stats(path, &stats);
    return 0;
}
