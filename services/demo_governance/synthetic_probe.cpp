// Non-neural fault helpers. No model, asset, network authority or parser.
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <cerrno>
#include <cstdlib>
#include <cstring>
#include <new>
#include <string>
static void* volatile last_allocation = nullptr;
int main(int argc, char** argv) {
    if (argc != 2 || geteuid() != 10001) return 90;
    const std::string mode(argv[1]);
    if (mode == "attack") {
        return kill(1, SIGSTOP) == -1 && errno == EPERM ? 0 : 89;
    }
    if (mode == "pids") {
        for (int i = 0; i < 100; i++) {
            const pid_t p = fork();
            if (p < 0) return 74;
            if (p == 0) { sleep(30); return 0; }
        }
        return 89;
    }
    if (mode == "network") {
        const int s = socket(AF_INET, SOCK_STREAM, 0);
        sockaddr_in a{};
        a.sin_family = AF_INET;
        a.sin_port = htons(443);
        inet_pton(AF_INET, "192.0.2.1", &a.sin_addr);
        const int r = connect(s, reinterpret_cast<sockaddr*>(&a), sizeof(a));
        close(s);
        return r < 0 ? 0 : 89;
    }
    if (mode == "stdout") {
        char bytes[4096]{};
        constexpr char canary[] = "FOC-SYNTHETIC-PRIVATE-CANARY";
        memcpy(bytes, canary, sizeof(canary) - 1);
        for (int i = 0; i < 256; i++) {
            if (write(STDOUT_FILENO, bytes, sizeof(bytes)) != static_cast<ssize_t>(sizeof(bytes))) return 75;
            if (write(STDERR_FILENO, bytes, sizeof(bytes)) != static_cast<ssize_t>(sizeof(bytes))) return 75;
        }
        return 0;
    }
    if (mode == "ok") return 0;
    if (mode == "sleep") { sleep(30); return 0; }
    if (mode == "spin") {
        volatile unsigned long n = 0;
        for (;;) { n = n + 1; }
    }
    if (mode == "memory") {
        try {
            for (;;) {
                auto* p = new char[8*1024*1024];
                memset(p, 1, 8*1024*1024);
                last_allocation = p;
            }
        } catch (const std::bad_alloc&) { return 71; }
    }
    if (mode == "descendant") {
        if (fork() == 0) { setsid(); sleep(30); }
        sleep(30);
        return 0;
    }
    if (mode == "fds") {
        for (int i = 0; i < 100; i++) {
            if (open("/dev/null", O_RDONLY) < 0) return 72;
        }
        return 0;
    }
    if (mode == "output") {
        const int fd = open("/tmp/bounded", O_CREAT|O_WRONLY, 0600);
        char b[4096]{};
        for (int i = 0; i < 1000; i++) {
            if (write(fd, b, sizeof(b)) < 0) return 73;
        }
        close(fd);
        return 0;
    }
    return 90;
}
