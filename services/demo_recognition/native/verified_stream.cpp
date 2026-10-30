#include "verified_stream.h"
#include <algorithm>
#include <openssl/evp.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <memory>
#include <stdexcept>

namespace foc {
namespace {
[[noreturn]] void reject() { throw std::runtime_error("artifact_integrity_denied"); }
void trusted_directory(int fd) {
    struct stat st{};
    if (fstat(fd,&st) || !S_ISDIR(st.st_mode) || st.st_uid!=0 || (st.st_mode&0022)) reject();
}
std::string stamp(int fd, std::uint64_t expected) {
    struct stat st{};
    if (fstat(fd, &st) || !S_ISREG(st.st_mode) || st.st_nlink != 1 ||
        st.st_size <= 0 || static_cast<std::uint64_t>(st.st_size) != expected ||
        (st.st_mode & 0222) || st.st_uid != 0) reject();
    return std::to_string(st.st_dev)+":"+std::to_string(st.st_ino)+":"+
        std::to_string(st.st_size)+":"+std::to_string(st.st_mtim.tv_sec)+":"+
        std::to_string(st.st_mtim.tv_nsec)+":"+std::to_string(st.st_ctim.tv_sec)+":"+
        std::to_string(st.st_ctim.tv_nsec);
}
std::array<unsigned char, 32> hash_fd(int fd, std::uint64_t size) {
    std::unique_ptr<EVP_MD_CTX, decltype(&EVP_MD_CTX_free)> ctx(EVP_MD_CTX_new(), EVP_MD_CTX_free);
    if (!ctx || EVP_DigestInit_ex(ctx.get(), EVP_sha256(), nullptr) != 1) reject();
    std::array<char, 65536> data{};
    std::uint64_t offset=0;
    while (offset < size) {
        auto count=pread(fd, data.data(), std::min<std::uint64_t>(data.size(),size-offset), offset);
        if (count <= 0 || EVP_DigestUpdate(ctx.get(),data.data(),count) != 1) reject();
        offset += count;
    }
    char extra;
    if (pread(fd,&extra,1,size) != 0) reject();
    std::array<unsigned char, 32> result{}; unsigned int length=0;
    if (EVP_DigestFinal_ex(ctx.get(),result.data(),&length) != 1 || length != result.size()) reject();
    return result;
}
}

VerifiedStream::VerifiedStream(const char* path, const Identity& expected): expected_(expected) {
    if (!expected.bytes || expected.bytes > kArtifactCeiling ||
        std::all_of(expected.sha256.begin(),expected.sha256.end(),[](auto x){return x==0;})) reject();
    // Absolute trusted parent directories must separately be immutable/read-only.
    // openat() prevents symlinks at EVERY path component, not just the final file.
    if (!path || path[0]!='/' || std::string(path).size()>256) reject();
    int dir=open("/",O_RDONLY|O_DIRECTORY|O_CLOEXEC);
    if (dir<0) reject();
    try {
        trusted_directory(dir);
        const std::string text(path); std::size_t start=1;
        while (true) {
            auto end=text.find('/',start);auto part=text.substr(start,end-start);
            if (part.empty() || part=="." || part=="..") reject();
            if (end==std::string::npos) {
                fd_=openat(dir,part.c_str(),O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK);
                break;
            }
            int next=openat(dir,part.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
            if (next<0) reject();
            close(dir);dir=next;trusted_directory(dir);start=end+1;
        }
        close(dir);dir=-1;
        if (fd_<0) reject();
        snapshot_=stamp(fd_,expected.bytes);
        if (hash_fd(fd_,expected.bytes)!=expected.sha256 || stamp(fd_,expected.bytes)!=snapshot_) reject();
        setg(buffer_.data(),buffer_.data(),buffer_.data());
    } catch (...) { if (dir>=0) close(dir);if (fd_>=0) close(fd_);fd_=-1;throw; }
}
VerifiedStream::~VerifiedStream() { if (fd_>=0) close(fd_); }
void VerifiedStream::verify_unchanged() {
    if (stamp(fd_,expected_.bytes)!=snapshot_ || hash_fd(fd_,expected_.bytes)!=expected_.sha256 ||
        stamp(fd_,expected_.bytes)!=snapshot_) reject();
}
VerifiedStream::int_type VerifiedStream::underflow() {
    if (gptr()<egptr()) return traits_type::to_int_type(*gptr());
    if (position_==expected_.bytes) return traits_type::eof();
    const auto n=pread(fd_,buffer_.data(),std::min<std::uint64_t>(buffer_.size(),expected_.bytes-position_),position_);
    if (n<=0) reject();
    position_+=n;setg(buffer_.data(),buffer_.data(),buffer_.data()+n);
    return traits_type::to_int_type(*gptr());
}
}
