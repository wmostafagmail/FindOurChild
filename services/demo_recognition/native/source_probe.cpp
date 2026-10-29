// Selected graph declarations adapted from Davis E. King's pinned dlib v20.0
// tools/python/src/{cnn_face_detector,face_recognition}.cpp (BSL-1.0).
// No upstream broad Python bindings, pretrained payload or model loader.
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <dlib/dnn.h>
#include <dlib/image_processing/shape_predictor.h>
#include <dlib/image_transforms/interpolation.h>
#include <dlib/revision.h>
#include <array>
#include <cstdint>
#include <string>

namespace py = pybind11;
using namespace dlib;

template <long N, typename S> using con5d = con<N,5,5,2,2,S>;
template <long N, typename S> using con5 = con<N,5,5,1,1,S>;
template <typename S> using downsampler = relu<affine<con5d<32,relu<affine<con5d<32,relu<affine<con5d<16,S>>>>>>>>>;
template <typename S> using rcon5 = relu<affine<con5<45,S>>>;
using cnn_type = loss_mmod<con<1,9,9,1,1,rcon5<rcon5<rcon5<downsampler<input_rgb_image_pyramid<pyramid_down<6>>>>>>>>;

template <template <int,template<typename>class,int,typename> class B, int N, template<typename>class BN, typename S>
using residual = add_prev1<B<N,BN,1,tag1<S>>>;
template <template <int,template<typename>class,int,typename> class B, int N, template<typename>class BN, typename S>
using residual_down = add_prev2<avg_pool<2,2,2,2,skip1<tag2<B<N,BN,2,tag1<S>>>>>>;
template <int N, template<typename>class BN, int stride, typename S>
using block = BN<con<N,3,3,1,1,relu<BN<con<N,3,3,stride,stride,S>>>>>;
template <int N, typename S> using ares = relu<residual<block,N,affine,S>>;
template <int N, typename S> using ares_down = relu<residual_down<block,N,affine,S>>;
template <typename S> using alevel0 = ares_down<256,S>;
template <typename S> using alevel1 = ares<256,ares<256,ares_down<256,S>>>;
template <typename S> using alevel2 = ares<128,ares<128,ares_down<128,S>>>;
template <typename S> using alevel3 = ares<64,ares<64,ares<64,ares_down<64,S>>>>;
template <typename S> using alevel4 = ares<32,ares<32,ares<32,S>>>;
using encoder_type = loss_metric<fc_no_bias<128,avg_pool_everything<alevel0<alevel1<alevel2<alevel3<alevel4<
    max_pool<3,3,2,2,relu<affine<con<32,7,7,2,2,input_rgb_image_sized<150>>>>>>>>>>>>>;

using RGB = py::array_t<std::uint8_t, py::array::c_style>;
using Points = std::array<std::array<long,2>,5>;

RGB aligned_chip(const RGB& rgb, const Points& coordinates, bool batch) {
    const auto source = rgb.request();
    if (source.ndim != 3 || source.shape[2] != 3 || source.shape[0] < 1 || source.shape[1] < 1 ||
        source.shape[0] > 1600 || source.shape[1] > 1600)
        throw py::value_error("Bounded contiguous RGB uint8 array required");
    const long height = source.shape[0], width = source.shape[1];
    array2d<rgb_pixel> image(height, width);
    const auto* bytes = static_cast<const std::uint8_t*>(source.ptr);
    for (long y = 0; y < height; ++y) for (long x = 0; x < width; ++x) {
        const auto offset = (y*width+x)*3;
        image[y][x] = rgb_pixel(bytes[offset],bytes[offset+1],bytes[offset+2]);
    }
    std::vector<point> parts;
    for (const auto& p : coordinates) {
        if (p[0] < 0 || p[0] >= width || p[1] < 0 || p[1] >= height)
            throw py::value_error("Five bounded fictional points required");
        parts.emplace_back(p[0],p[1]);
    }
    full_object_detection shape(rectangle(0,0,width-1,height-1), parts);
    const auto details = get_face_chip_details(shape,150,0.25);
    array2d<rgb_pixel> chip;
    if (batch) {
        dlib::array<array2d<rgb_pixel>> chips;
        extract_image_chips(image,std::vector<chip_details>{details},chips);
        chip.swap(chips[0]);
    } else {
        extract_image_chip(image,details,chip);
    }
    RGB output({150,150,3});
    auto destination = output.mutable_unchecked<3>();
    for (long y=0; y<150; ++y) for (long x=0; x<150; ++x) {
        destination(y,x,0)=chip[y][x].red;
        destination(y,x,1)=chip[y][x].green;
        destination(y,x,2)=chip[y][x].blue;
    }
    return output;
}

PYBIND11_MODULE(_foc_dlib_native, module) {
    module.doc() = "Data-free source probe only; no model loading/inference API";
    module.attr("dlib_version") = std::to_string(DLIB_MAJOR_VERSION)+"."+
        std::to_string(DLIB_MINOR_VERSION)+"."+std::to_string(DLIB_PATCH_VERSION);
    module.attr("interface_version") = "foc-dlib-source-probe-v1";
    module.attr("model_execution_api_available") = false;
    module.attr("compiled_cnn_type_bytes") = sizeof(cnn_type);
    module.attr("compiled_encoder_type_bytes") = sizeof(encoder_type);
    module.attr("compiled_predictor_type_bytes") = sizeof(shape_predictor);
    module.def("align_chip", [](const RGB& rgb, const Points& p){return aligned_chip(rgb,p,false);},
        py::arg("rgb").noconvert(),py::arg("five_points"));
    module.def("align_chip_batch", [](const RGB& rgb, const Points& p){return aligned_chip(rgb,p,true);},
        py::arg("rgb").noconvert(),py::arg("five_points"));
}
