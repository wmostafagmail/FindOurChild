// Internal compile/link boundary, never registered with Python.
#pragma once
#include "model_types.h"
namespace foc {
void compiled_parse_cnn(cnn_type&,std::istream&);
void compiled_parse_predictor(shape_predictor&,std::istream&);
void compiled_parse_encoder(encoder_type&,std::istream&);
std::vector<mmod_rect> compiled_run_cnn(cnn_type&,const matrix<rgb_pixel>&);
full_object_detection compiled_run_predictor(const shape_predictor&,const matrix<rgb_pixel>&,const rectangle&);
matrix<float,0,1> compiled_run_encoder(encoder_type&,const matrix<rgb_pixel>&);
inline void parse_component(cnn_type& m,std::istream& s) { compiled_parse_cnn(m,s); }
inline void parse_component(shape_predictor& m,std::istream& s) { compiled_parse_predictor(m,s); }
inline void parse_component(encoder_type& m,std::istream& s) { compiled_parse_encoder(m,s); }
}
