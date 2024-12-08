int main()
{
    if (a == 1) {
        ssh->log = NULL;
    } else if (a==2){
        func1();
        if (a == 1)
            return 2;
    } else if (a==3){
        return 1;
    }
    return 0;
}
