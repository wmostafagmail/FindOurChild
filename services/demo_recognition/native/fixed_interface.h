#pragma once
#include "model_types.h"
#include <pybind11/pybind11.h>
namespace foc {
// No runtime configuration, environment variable, Python attribute or flag changes this.
inline constexpr bool kModelExecutionApproved = false;
void require_execution_review();
extern unsigned long review_denials;
extern unsigned long model_open_attempts;
extern unsigned long deserialization_attempts;
extern unsigned long inference_attempts;
void bind_closed_interface(pybind11::module_& module);
}
