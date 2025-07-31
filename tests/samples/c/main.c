#include "include/sub.h"
#include <stdio.h>

int add(int a, int b)
{
    return a + sub(a, b);
}

int main(int argc, char** argv)
{
    int a = 1;
    int b = 2;
    int count = 10;
    int c = count + argc;
    while (a < 10 && add(c, c)) {
        a += 1;
        if (b > 5) 
            a -= 1;
        else if (b < 3) {
            a += 2;
        } else {
            a += 3;
        }
        if (a == 5) {
            break;
        } else {
            a += 4;
        }

        if (b > 10) {
            a += 5;
        }
        a -= 1;
        count -= c;
        count += a;
        b = sub(a, c);
    }
    count -= c;
    int i = 1;
    b = add(a, b);
    for (int i = 0; i < count; i++) {
        a += i;
        break;
    }
    printf("a: %d, b: %d, count: %d\n", a, b, count);
    return 0;
}

int mul(int a, int b)
{
    a = MAX(a, 1);
    return a * add(a, b);
}

int cp(int *x, int *y)
{
    *x = *y;
    return 0;
}

int test_switch(int a)
{
    switch (a) {
        case 1:
            return 1;
        case 2:
            return 2;
        default:
            a = 0;
        }
    return a;
}

int test_goto(int a)
{
    if (a < 0) {
        goto label_negative;
    } else if (a > 0) {
        goto label_positive;
    } else {
        return 0;
    }
label_negative:
    return -1;
label_positive:
    return 1;
}

void test_continue(int a)
{
    for (int i = 0; i < 10; i++) {
        if (i == a) {
            continue;
        }
        printf("i: %d\n", i);
    }
}

int test_break(int a)
{
    for (int i = 0; i < 10; i++) {
        if (i == a) {
            break;
        }
        printf("i: %d\n", i);
    }
    return 0;
}
