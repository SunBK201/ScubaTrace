#include <include/sub.h>
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
        if (b > 5) {
            a -= 1;
        } else {
            a += 2;
        }
        if (a == 5) {
            break;
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
    return 0;
}

int mul(int a, int b)
{
    a = MAX(a, 1);
    return a * add(a, b);
}