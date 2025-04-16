#include <other.c>
#include <stdio.h>
#include <stdlib.h>

int addwapper(int a, int b) {
  add(a, b);
  return add(a, b);
}

int main() {
  int a = 1;
  int c, d = 2;
  int codelen = malloc(d);
  int b = 2;
  addwapper(a, d);
  int c = a + b;
  add(a, b);
}