#include "model_backend.h"
#include "fixed_interface.h"
// Separate translation units and disabled LTO retain actual parser/forward bodies
// for ABI/link review. Every body denies BEFORE model parsing or execution.
namespace foc {
void compiled_parse_cnn(cnn_type& model,std::istream& input) {
    require_execution_review();deserialize(model,input);
}
void compiled_parse_predictor(shape_predictor& model,std::istream& input) {
    require_execution_review();deserialize(model,input);
}
void compiled_parse_encoder(encoder_type& model,std::istream& input) {
    require_execution_review();deserialize(model,input);
}
std::vector<mmod_rect> compiled_run_cnn(cnn_type& model,const matrix<rgb_pixel>& image) {
    require_execution_review();return model(image);
}
full_object_detection compiled_run_predictor(const shape_predictor& model,const matrix<rgb_pixel>& image,const rectangle& box) {
    require_execution_review();return model(image,box);
}
matrix<float,0,1> compiled_run_encoder(encoder_type& model,const matrix<rgb_pixel>& image) {
    require_execution_review();return model(image);
}
}
