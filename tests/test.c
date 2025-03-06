int add(int a, int b)
{
    return a + b;
}

int main(int argc, char **argv)
{
    int a = 1;
    int b = 2;
    int count = argc;
    while (a < 10) {
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
        count -= a;
        count += a;
    }
    int i = 1;
    b = add(a, b);
    for (int i = 0; i < count; i++) {
        a += i;
        break;
    }
    return 0;
}