// Source-only synthetic supervisor. No dlib, parser, model or image dependency.
// Linux PID namespace init: its death kills every task in that namespace.
#include <sys/prctl.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <cstddef>
#include <sys/resource.h>
#include <sys/syscall.h>
#include <sys/timerfd.h>
#include <sys/wait.h>
#include <poll.h>
#include <fcntl.h>
#include <signal.h>
#include <unistd.h>
#include <time.h>
#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

static void worker_filter() {
    // Worker cannot stop/ptrace the watchdog or signal another process. Killing
    // namespace init still kills the entire namespace; no publication follows.
    sock_filter code[] = {
        BPF_STMT(BPF_LD|BPF_W|BPF_ABS, offsetof(seccomp_data, arch)),
        BPF_JUMP(BPF_JMP|BPF_JEQ|BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET|BPF_K, SECCOMP_RET_KILL_PROCESS),
        BPF_STMT(BPF_LD|BPF_W|BPF_ABS, offsetof(seccomp_data, nr)),
        BPF_JUMP(BPF_JMP|BPF_JGE|BPF_K, 0x40000000, 0, 1),
        BPF_STMT(BPF_RET|BPF_K, SECCOMP_RET_KILL_PROCESS),
#define DENY(n) BPF_JUMP(BPF_JMP|BPF_JEQ|BPF_K, n, 0, 1), BPF_STMT(BPF_RET|BPF_K, SECCOMP_RET_ERRNO|EPERM)
        DENY(SYS_kill), DENY(SYS_tkill), DENY(SYS_tgkill), DENY(SYS_pidfd_send_signal),
        DENY(SYS_rt_sigqueueinfo), DENY(SYS_rt_tgsigqueueinfo), DENY(SYS_ptrace), DENY(SYS_process_vm_writev), DENY(SYS_process_vm_readv),
        DENY(SYS_setns), DENY(SYS_unshare), DENY(SYS_pidfd_getfd),
#undef DENY
        BPF_STMT(BPF_RET|BPF_K, SECCOMP_RET_ALLOW)
    };
    sock_fprog program{static_cast<unsigned short>(sizeof(code)/sizeof(code[0])), code};
    if(prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &program)!=0) _exit(91);
}
static void limit(int resource, rlim_t soft, rlim_t hard) {
    rlimit value{soft, hard};
    if (setrlimit(resource, &value) != 0) _exit(91);
}
static void reap_all() {
    // Restricted to our verified PID namespace; never run this on the host.
    kill(-1, SIGKILL);
    while (waitpid(-1, nullptr, 0) > 0 || errno == EINTR) { errno = 0; }
}
int main(int argc, char** argv) {
    if (getpid() != 1 || geteuid() != 10001 || argc != 2) return 90;
    const std::string mode(argv[1]);
    if (mode != "ok" && mode != "sleep" && mode != "spin" && mode != "memory" &&
        mode != "descendant" && mode != "fds" && mode != "output" && mode != "attack" && mode != "pids" && mode != "network" && mode != "stdout") return 90;
    if (prctl(PR_SET_DUMPABLE, 0) != 0 || prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) return 91;
    // No control-plane/Docker-client calls below. timerfd stays outside worker.
    timespec started{};
    if (clock_gettime(CLOCK_MONOTONIC, &started) != 0) return 91;
    const int timer = timerfd_create(CLOCK_MONOTONIC, TFD_CLOEXEC);
    itimerspec deadline{}; deadline.it_value.tv_sec = 3;
    if (timer < 0 || timerfd_settime(timer, 0, &deadline, nullptr) != 0) return 91;
    const pid_t child = fork();
    if (child < 0) return 91;
    if (child == 0) {
        const pid_t expected = getppid();
        if (prctl(PR_SET_PDEATHSIG, SIGKILL) != 0 || expected != 1 || getppid() != expected) _exit(91);
        close(timer);
        // No untrusted worker stdout/stderr reaches the container log driver.
        // Only this supervisor emits the bounded fixed resource receipt.
        const int nullfd = open("/dev/null", O_RDWR | O_CLOEXEC);
        if (nullfd < 0 || dup2(nullfd, STDIN_FILENO) < 0 || dup2(nullfd, STDOUT_FILENO) < 0 ||
            dup2(nullfd, STDERR_FILENO) < 0) _exit(91);
        if (nullfd > STDERR_FILENO) close(nullfd);
        limit(RLIMIT_CPU, 1, 2); limit(RLIMIT_AS, 64*1024*1024, 64*1024*1024);
        limit(RLIMIT_CORE, 0, 0); limit(RLIMIT_FSIZE, 65536, 65536);
        limit(RLIMIT_NOFILE, 32, 32); limit(RLIMIT_NPROC, 16, 16);
        worker_filter();
        clearenv();
        execl("/opt/foc-demo/bin/foc-synthetic-probe", "foc-synthetic-probe", mode.c_str(), nullptr);
        _exit(91);
    }
    const int pidfd = static_cast<int>(syscall(SYS_pidfd_open, child, 0));
    if (pidfd < 0) { reap_all(); return 91; }
    pollfd events[2]{{timer, POLLIN, 0}, {pidfd, POLLIN, 0}};
    int result;
    do { result = poll(events, 2, -1); } while (result < 0 && errno == EINTR);
    int status = 0;
    const bool timed_out = result <= 0 || (events[0].revents & POLLIN);
    if (timed_out) { reap_all(); status = 124; }
    else {
        if (waitpid(child, &status, 0) != child) status = 125;
        else status = WIFEXITED(status) ? WEXITSTATUS(status) : 128 + WTERMSIG(status);
        reap_all();
    }
    close(pidfd); close(timer);
    // Fixed sanitized receipt, no worker-controlled text, inputs or vectors.
    rusage usage{}; timespec finished{};
    if (getrusage(RUSAGE_CHILDREN, &usage) != 0 || clock_gettime(CLOCK_MONOTONIC, &finished) != 0) return 91;
    const long long cpu_us = (static_cast<long long>(usage.ru_utime.tv_sec) + usage.ru_stime.tv_sec) * 1000000
                            + usage.ru_utime.tv_usec + usage.ru_stime.tv_usec;
    const long long wall_ms = (static_cast<long long>(finished.tv_sec) - started.tv_sec) * 1000
                             + (finished.tv_nsec - started.tv_nsec) / 1000000;
    // maxrss is max single reaped child RSS (Linux KiB), not aggregate cgroup peak.
    printf("{\"synthetic_only\":true,\"deadline_ms\":3000,\"status\":%d,\"inference\":false,"
           "\"max_child_rss_kib\":%ld,\"cpu_us\":%lld,\"wall_ms\":%lld}\n", status, usage.ru_maxrss, cpu_us, wall_ms);
    return status;
}
