int add(int a, int b)
{
    return a + b;
}

int main()
{
    int count = 10;
    int a = 1;
    int b = 2;
    while (a < 10) {
        a += 1;
        if (b > 5) {
            b -= 1;
        } else {
            a += 2;
        }
        if (a == 5) {
            break;
        }
        a -= 1;
    }
    b = add(a, b);
    for (int i = 0; i < count; i++) {
        a += 1;
        break;
    }
    return 0;
}