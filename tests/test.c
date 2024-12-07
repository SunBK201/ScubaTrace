int ssh_packet_stop_discard(struct ssh* ssh)
{
    return 0;
}

int main(int argc, char const* argv[])
{
    ssh_packet_stop_discard(NULL);
    return 0;
}