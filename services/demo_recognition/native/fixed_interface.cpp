#include "fixed_interface.h"
#include "verified_stream.h"
#include "model_backend.h"
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <dlib/image_transforms/interpolation.h>
#include <array>
#include <cmath>
#include <memory>
#include <optional>

namespace foc {
namespace py=pybind11;
using RGB=py::array_t<std::uint8_t,py::array::c_style>;
using Box=std::array<long,4>;
using Landmarks=std::array<std::array<long,2>,5>;

namespace {
// Immutable paths are internal and never parameters of an exported interface.
constexpr std::array<const char*,3> paths={
    "/opt/foc-demo/models/mmod_human_face_detector.dat",
    "/opt/foc-demo/models/shape_predictor_5_face_landmarks.dat",
    "/opt/foc-demo/models/dlib_face_recognition_resnet_model_v1.dat"};
// Actual A3/A4 decompressed identities DO NOT EXIST yet. No placeholder is trusted.
const std::array<std::optional<Identity>,3> identities={std::nullopt,std::nullopt,std::nullopt};

void validate_rgb(const RGB& rgb, bool chip=false) {
    auto b=rgb.request();
    if (b.ndim!=3 || b.shape[2]!=3 || b.shape[0]<1 || b.shape[1]<1 ||
        b.shape[0]>512 || b.shape[1]>512 || (chip && (b.shape[0]!=150 || b.shape[1]!=150)))
        throw py::value_error("bounded_rgb_required");
}
void validate_box(const RGB& rgb, const Box& box) {
    if (box[0]<0 || box[1]<0 || box[2]<box[0] || box[3]<box[1] ||
        box[2]>=rgb.shape(1) || box[3]>=rgb.shape(0)) throw py::value_error("bounded_rectangle_required");
}
matrix<rgb_pixel> image_copy(const RGB& rgb) {
    auto b=rgb.request();matrix<rgb_pixel> image(b.shape[0],b.shape[1]);
    const auto* bytes=static_cast<const std::uint8_t*>(b.ptr);
    for (long y=0;y<image.nr();++y) for (long x=0;x<image.nc();++x) {
        auto i=(y*image.nc()+x)*3;image(y,x)=rgb_pixel(bytes[i],bytes[i+1],bytes[i+2]);
    }
    return image;
}

// These definitions instantiate and compile/link the REAL dlib parser and forward
// APIs, not sizeof() or a fake descriptor. They are never executed in this phase.
class FixedComponents final {
    cnn_type cnn_; shape_predictor predictor_; encoder_type encoder_;
    template<class Model> void load(unsigned component,Model& model) {
        require_execution_review();
        if (!identities[component]) throw std::runtime_error("actual_identity_unapproved");
        ++model_open_attempts;
        VerifiedStream buffer(paths[component],*identities[component]);
        std::istream input(&buffer);input.exceptions(std::ios::badbit);
        ++deserialization_attempts;
        parse_component(model,input);
        if (input.peek()!=std::char_traits<char>::eof()) throw std::runtime_error("trailing_artifact_denied");
        buffer.verify_unchanged();
    }
public:
    FixedComponents() {
        require_execution_review();load(0,cnn_);load(1,predictor_);load(2,encoder_);
        if (predictor_.num_parts()!=5 || predictor_.num_features()>1000000)
            throw std::runtime_error("component_schema_denied");
    }
    std::vector<Box> detect(const RGB& rgb) {
        require_execution_review();++inference_attempts;auto image=image_copy(rgb);
        // No upsample, resize, batching, GPU or detector substitution.
        auto detections=compiled_run_cnn(cnn_,image);
        if (detections.size()>32) throw std::runtime_error("detection_capacity_denied");
        std::vector<Box> boxes;
        for (const auto& d:detections) {
            Box b={d.rect.left(),d.rect.top(),d.rect.right(),d.rect.bottom()};
            validate_box(rgb,b);if (!std::isfinite(d.detection_confidence)) throw std::runtime_error("invalid_detection");
            boxes.push_back(b);
        }
        return boxes;
    }
    Landmarks predict(const RGB& rgb,const Box& box) {
        require_execution_review();++inference_attempts;auto image=image_copy(rgb);
        auto shape=compiled_run_predictor(predictor_,image,rectangle(box[0],box[1],box[2],box[3]));
        if (shape.num_parts()!=5) throw std::runtime_error("invalid_landmarks");
        Landmarks points{};
        for (unsigned i=0;i<5;++i) {
            const auto p=shape.part(i);
            if (p.x()<0 || p.y()<0 || p.x()>=image.nc() || p.y()>=image.nr()) throw std::runtime_error("invalid_landmarks");
            points[i]={p.x(),p.y()};
        }
        return points;
    }
    std::array<double,128> encode(const RGB& rgb) {
        require_execution_review();++inference_attempts;auto image=image_copy(rgb);
        const matrix<float,0,1> descriptor=compiled_run_encoder(encoder_,image);
        if (descriptor.size()!=128) throw std::runtime_error("invalid_descriptor");
        std::array<double,128> result{};double norm=0;
        for (unsigned i=0;i<128;++i) {
            result[i]=descriptor(i);if (!std::isfinite(result[i])) throw std::runtime_error("invalid_descriptor");
            norm+=result[i]*result[i];
        }
        if (!std::isfinite(norm) || norm<=0 || norm>1000000) throw std::runtime_error("invalid_descriptor");
        return result; // native float -> double, NO normalization/jitter/score conversion.
    }
};
FixedComponents& session() { require_execution_review();static FixedComponents models;return models; }
bool provider_faulted=false;
template<class Operation> auto guarded_operation(Operation operation) -> decltype(operation()) {
    require_execution_review();
    if (provider_faulted) throw std::runtime_error("component_unavailable");
    try { return operation(); }
    catch (...) {
        provider_faulted=true;
        // Never expose dlib/OpenSSL/OS exception text, artifact paths or contents.
        throw std::runtime_error("component_execution_failed");
    }
}
}

void bind_closed_interface(py::module_& module) {
    module.def("boundary_counters",[](){py::dict result;result["review_denials"]=review_denials;
        result["model_open_attempts"]=model_open_attempts;result["deserialization_attempts"]=deserialization_attempts;
        result["inference_attempts"]=inference_attempts;return result;});
    module.def("prepare_components",[](){guarded_operation([](){(void)session();});}); // deliberately zero arguments
    module.def("detect",[](const RGB& rgb){validate_rgb(rgb);return guarded_operation([&](){return session().detect(rgb);});},py::arg("rgb").noconvert());
    module.def("predict_five",[](const RGB& rgb,const Box& box){validate_rgb(rgb);validate_box(rgb,box);return guarded_operation([&](){return session().predict(rgb,box);});},
        py::arg("rgb").noconvert(),py::arg("rectangle"));
    module.def("encode_128",[](const RGB& chip){validate_rgb(chip,true);return guarded_operation([&](){return session().encode(chip);});},py::arg("chip").noconvert());
    module.def("validate_detection_input",[](const RGB& rgb){validate_rgb(rgb);},py::arg("rgb").noconvert());
    module.def("validate_landmark_input",[](const RGB& rgb,const Box& box){validate_rgb(rgb);validate_box(rgb,box);},
        py::arg("rgb").noconvert(),py::arg("rectangle"));
    module.def("validate_encoder_input",[](const RGB& chip){validate_rgb(chip,true);},py::arg("chip").noconvert());
}
}
