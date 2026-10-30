// Fixed-file integrity primitive. No dlib parser or Python callbacks here.
#pragma once
#include <array>
#include <cstdint>
#include <istream>
#include <streambuf>
#include <string>

namespace foc {
struct Identity {
    std::uint64_t bytes;
    std::array<unsigned char, 32> sha256;
};
constexpr std::uint64_t kArtifactCeiling = 64ULL * 1024 * 1024;

class VerifiedStream final : public std::streambuf {
public:
    // Only internal fixed-component code calls this in the extension.
    VerifiedStream(const char* path, const Identity& expected);
    ~VerifiedStream() override;
    VerifiedStream(const VerifiedStream&) = delete;
    VerifiedStream& operator=(const VerifiedStream&) = delete;
    void verify_unchanged();
protected:
    int_type underflow() override;
private:
    int fd_ = -1;
    Identity expected_;
    std::uint64_t position_ = 0;
    std::array<char, 65536> buffer_{};
    std::string snapshot_;
};
}
