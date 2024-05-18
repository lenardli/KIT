#include <getopt.h>
#include <regex.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define GNU_SOURCE

int pattern_file(char* filename, char* p_file, char* short_flag,
                 int file_count);
static char* substr(const char* str, unsigned start, unsigned end, char* stbuf);
int print_file(char* filename, char* pattern, const char* short_flag,
               int file_count);
int file_count(int optind, int argc, char* short_flag);

int file_count(int optind, int argc, char* short_flag) {
  int count = 0, flag = 2;
  for (; optind < argc; optind++) {
    if (strlen(short_flag) == 0) {
      if (optind > 1) count += 1;
    } else if (strchr(short_flag, 'e') != NULL) {
      count += 1;
    } else if (strchr(short_flag, 'f') != NULL) {
      if (optind > 2) count += 1;
    } else {
      if (optind > 2) count += 1;
    }
  }
  flag = count > 1 ? 1 : 0;
  return flag;
}

char* substr(const char* str, unsigned start, unsigned end, char* stbuf) {
  unsigned n = end - start;
  stbuf = strncpy(stbuf, str + start, n);
  stbuf[n] = 0;
  return stbuf;
}
int pattern_file(char* filename, char* p_file, char* short_flag,
                 int file_count) {
  FILE* file = fopen(p_file, "r");
  char* lbuf = NULL;
  char ebuf[1000] = {'\0'};
  size_t n = 256;
  int z = 0, err = 0;
  if (file != NULL) {
    while (getline(&lbuf, &n, file) != -1) {
      if ((z = strlen(lbuf)) > 0) {
        if (lbuf[z - 1] == '\n' && z != 1) lbuf[z - 1] = 0;
        if (strlen(lbuf) > 0 && strlen(ebuf) > 0) strcat(ebuf, "|");
        strcat(ebuf, lbuf);
      }
    }
    if (strlen(ebuf) > 0) print_file(filename, ebuf, short_flag, file_count);
    fclose(file);
    if (lbuf != NULL) free(lbuf);
  } else {
    fprintf(stderr, "No such file %s\n", p_file);
    err = 1;
  }
  return err;
}

int print_file(char* filename, char* pattern, const char* short_flag,
               int file_count) {
  char stbuf[500] = {'\0'};
  char* lbuf = NULL;
  int z = 0, lno = 0, cflags = 1, match_count = 0;
  size_t x = 0, n = 3;
  char ebuf[500] = {'\0'};
  regex_t reg = {0};
  regmatch_t pm[10] = {0};
  const size_t nmatch = 10;
  FILE* file = fopen(filename, "r");
  if (strchr(short_flag, 'i') != NULL) cflags = 2;
  z = regcomp(&reg, pattern, cflags);
  if (z != 0) {
    regerror(z, &reg, ebuf, sizeof(ebuf));
    fprintf(stderr, "%s: pattern '%s' \n", ebuf, pattern);
    return 1;
  }
  if (file != NULL) {
    while (getline(&lbuf, &n, file) != -1) {
      ++lno;
      while (1) {
        if (lbuf[strlen(lbuf) - 1] != '\n') strcat(lbuf, "\n");
        z = regexec(&reg, lbuf, nmatch, pm, 0);
        if (z == REG_NOMATCH) {
          if (strchr(short_flag, 'v') != NULL) {
            if (file_count) printf("%s:", filename);
            printf("%s", lbuf);
          }
          break;
        } else if (z != 0) {
          regerror(z, &reg, ebuf, sizeof(ebuf));
          fprintf(stderr, "%s: regcom('%s')", ebuf, lbuf);
          return 2;
        }
        if (strchr(short_flag, 'v') == NULL) {
          for (x = 0; x < nmatch; x++) {
            if ((strchr(short_flag, 'c') != NULL ||
                 strchr(short_flag, 'l') != NULL) &&
                !x)
              match_count += 1;
            else if (strchr(short_flag, 'o') != NULL && !x) {
              if (file_count) printf("%s:", filename);
              printf("%s\n", substr(lbuf, pm[x].rm_so, pm[x].rm_eo, stbuf));
            } else if (!x) {
              if (strchr(short_flag, 'n') != NULL) {
                if (file_count) printf("%s:", filename);
                printf("%d:%s", lno, lbuf);
              } else if ((strchr(short_flag, 'h') != NULL))
                printf("%s", lbuf);
              else {
                if (file_count) printf("%s:", filename);
                printf("%s", lbuf);
              }
            }
          }
        }
        strcpy(lbuf, substr(lbuf, pm[0].rm_eo, strlen(lbuf), stbuf));
        if (strchr(short_flag, 'o') == NULL) break;
      }
    }
    if (strchr(short_flag, 'c') != NULL) {
      if (file_count) printf("%s:", filename);
      printf("%d\n", match_count);
    }
    if (strchr(short_flag, 'l') != NULL && match_count != 0)
      printf("%s\n", filename);
    fclose(file);
    if (lbuf != NULL) free(lbuf);
  } else if (strchr(short_flag, 's') == NULL)
    fprintf(stderr, "No such file %s\n", filename);
  regfree(&reg);
  return 0;
}

int main(int argc, char** argv) {
  const char* short_options = "e:ivclnhsof:";
  int rez = 0, f_flag = 0, err = 0;
  char short_flag[20] = {'\0'};
  char* pattern = NULL;
  char temp = 0;
  char temp1[2] = {'\0'};
  while ((rez = getopt(argc, argv, short_options)) != -1) {
    switch (rez) {
      case ('?'):
        temp = rez;
        break;
      default:
        if (rez == 'e' || rez == 'f') {
          if (pattern != NULL) {
            strcat(pattern, "|");
            strcat(pattern, optarg);
          } else {
            pattern = (char*)calloc(strlen(optarg) + 1, sizeof(char));
            strcpy(pattern, optarg);
          }
        }
        temp1[0] = rez;
        strcat(short_flag, temp1);
        break;
    }
  }
  if (temp != '?') {
    f_flag = file_count(optind, argc, short_flag);  // um
    for (; optind < argc; optind++) {
      if (strlen(short_flag) == 0) {
        if (optind > 1) print_file(argv[optind], argv[1], short_flag, f_flag);
      } else if (strchr(short_flag, 'e') != NULL) {
        print_file(argv[optind], pattern, short_flag, f_flag);
      } else if (strchr(short_flag, 'f') != NULL) {
        if (optind > 2) {
          err = pattern_file(argv[optind], pattern, short_flag, f_flag) == 1;
          if (err) break;
        }
      } else {
        if (optind > 2) {
          print_file(argv[optind], argv[2], short_flag, f_flag);
        }
      }
    }
  }
  if (pattern != NULL) free(pattern);
}
