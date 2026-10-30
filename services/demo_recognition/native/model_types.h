// Selected dlib v20.0 graph definitions, BSL-1.0; no pretrained data.
#pragma once
#include <dlib/dnn.h>
#include <dlib/image_processing/shape_predictor.h>
namespace foc {
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

}
