/* hello world */

#include <stdio.h>
#include "test.h"

int uct_pagesize = 1;
int uct_pagesize_shift;
int uct_cacheline_size;

int add(int a, int b);

struct test_struct {
    int a;
    int b;
};

int add(int a, int b)
{
    add(1, 2);
    return a + b;
}

int main()
{
    printf("Hello, world!\n");
    return 0;
}
