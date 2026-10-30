#include "fixed_interface.h"
#include <stdexcept>
namespace foc {
unsigned long review_denials=0,model_open_attempts=0,deserialization_attempts=0,inference_attempts=0;
void require_execution_review() {
    ++review_denials;
    if (!kModelExecutionApproved) throw std::runtime_error("a1b_second_review_required");
    // Independent actual-manifest authority is NOT implemented/provisioned yet.
    // Flipping the capability constant alone can never authorize execution.
    throw std::runtime_error("actual_manifest_authority_unprovisioned");
}
}
