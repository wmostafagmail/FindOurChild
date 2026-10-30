// Selected graph declarations adapted from Davis E. King's pinned dlib v20.0
// tools/python/src/{cnn_face_detector,face_recognition}.cpp (BSL-1.0).
// No broad bindings or pretrained payload. All model operations remain review-locked.
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <dlib/dnn.h>
#include <dlib/image_processing/shape_predictor.h>
#include <dlib/image_transforms/interpolation.h>
#include <array>
#include <cstdint>
#include <string>

namespace py = pybind11;
using namespace dlib;

#include "fixed_interface.h"
using foc::cnn_type;
using foc::encoder_type;
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
    if (parts[0]==parts[1] || parts[2]==parts[3] || parts[0]==parts[4] || parts[2]==parts[4])
        throw py::value_error("Distinct five-point geometry required");
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
    module.doc() = "Source-only fixed-component interface; model execution is review-locked";
    module.attr("dlib_version") = FOC_DLIB_VERSION;
#ifdef DLIB_USE_CUDA
    module.attr("cuda_enabled") = true;
#else
    module.attr("cuda_enabled") = false;
#endif
#ifdef __AVX__
    module.attr("avx_enabled") = true;
#else
    module.attr("avx_enabled") = false;
#endif
    module.attr("interface_version") = "foc-dlib-closed-interface-v2";
    module.attr("model_execution_api_available") = false;
    foc::bind_closed_interface(module);
    module.attr("compiled_cnn_type_bytes") = sizeof(cnn_type);
    module.attr("compiled_encoder_type_bytes") = sizeof(encoder_type);
    module.attr("compiled_predictor_type_bytes") = sizeof(shape_predictor);
    module.def("align_chip", [](const RGB& rgb, const Points& p){return aligned_chip(rgb,p,false);},
        py::arg("rgb").noconvert(),py::arg("five_points"));
    module.def("align_chip_batch", [](const RGB& rgb, const Points& p){return aligned_chip(rgb,p,true);},
        py::arg("rgb").noconvert(),py::arg("five_points"));
}
