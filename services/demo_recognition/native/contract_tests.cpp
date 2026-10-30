// Benign byte-stream integrity tests ONLY. No dlib/model parser is linked.
#include "verified_stream.h"
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <vector>
using namespace foc;
constexpr const char* root="/opt/qualification/stream-fixtures/";
Identity identity() { return {29,{73,54,70,142,151,229,85,12,95,57,33,238,239,146,28,205,102,56,172,62,183,178,231,191,154,178,132,51,138,216,2,71}}; }
std::string path(const char* name) { return std::string(root)+name; }
void check(bool condition) { if (!condition) throw std::runtime_error("native_contract_assertion"); }
void denied(const char* name,Identity value) {
    bool rejected=false;
    try { VerifiedStream stream(name,value); }
    catch (const std::runtime_error&) { rejected=true; }
    check(rejected);
}
int main() {
    const auto good=identity();
    std::vector<std::function<void()>> cases={
        [&]{VerifiedStream b(path("valid").c_str(),good);std::istream in(&b);std::string s((std::istreambuf_iterator<char>(in)),{});check(s=="fictional source-only stream\n");b.verify_unchanged();},
        [&]{VerifiedStream b(path("valid").c_str(),good);std::istream in(&b);check(in.get()=='f');b.verify_unchanged();},
        [&]{auto x=good;x.bytes=0;denied(path("valid").c_str(),x);},
        [&]{auto x=good;x.bytes=kArtifactCeiling+1;denied(path("valid").c_str(),x);},
        [&]{auto x=good;x.sha256.fill(0);denied(path("valid").c_str(),x);},
        [&]{auto x=good;x.sha256[0]^=1;denied(path("valid").c_str(),x);},
        [&]{auto x=good;++x.bytes;denied(path("valid").c_str(),x);},
        [&]{denied(path("symlink").c_str(),good);},
        [&]{denied(path("directory-link/valid").c_str(),good);},
        [&]{denied(path("hardlink").c_str(),good);},
        [&]{denied(path("fifo").c_str(),good);},
        [&]{denied(path("directory").c_str(),good);},
        [&]{denied(path("writable").c_str(),good);},
        [&]{denied(path("unowned").c_str(),good);},
        [&]{denied(path("missing").c_str(),good);},
        [&]{denied("relative",good);},
        [&]{denied(path("../stream-fixtures/valid").c_str(),good);},
        [&]{denied(("/"+std::string(300,'x')).c_str(),good);},
        [&]{for (unsigned i=0;i<16;++i){VerifiedStream b(path("valid").c_str(),good);b.verify_unchanged();}},
        [&]{VerifiedStream b(path("valid").c_str(),good);std::istream in(&b);for (unsigned i=0;i<29;++i)check(in.get()!=EOF);check(in.get()==EOF);b.verify_unchanged();}
    };
    std::cout<<"{\"scope\":\"synthetic_byte_stream_only_no_model_parser\",\"tests\":[";
    for (unsigned i=0;i<cases.size();++i) {
        try { cases[i](); } catch (...) {std::cerr<<"native stream contract case failed: "<<i+1<<'\n';return 1;}
        if (i) std::cout<<',';
        std::cout<<"{\"id\":\"STREAM-"<<i+1<<"\",\"status\":\"passed\"}";
    }
    std::cout<<"],\"model_deserializations\":0}\n";
}
