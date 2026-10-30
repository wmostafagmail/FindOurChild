"""Execute only validators/closed-boundary negatives, NEVER a dlib model parser."""

import os
import resource
import time

import _foc_dlib_native as native
import numpy as np


def checks(image, chip):
    box = [0, 0, 200, 200]
    outcomes = []

    def case(number, operation, error=None):
        try:
            operation()
        except (TypeError, ValueError, RuntimeError, AssertionError) as exc:
            if error is None or not isinstance(exc, error):
                raise AssertionError(f'INTERFACE-{number} unexpected rejection') from None
            if isinstance(exc, RuntimeError):
                assert str(exc) == 'a1b_second_review_required'
        else:
            assert error is None, f'INTERFACE-{number} failed to deny'
        outcomes.append({'id': f'INTERFACE-{number}', 'status': 'passed'})

    case(1, native.prepare_components, RuntimeError)
    case(2, lambda: native.detect(image), RuntimeError)
    case(3, lambda: native.predict_five(image, box), RuntimeError)
    case(4, lambda: native.encode_128(chip), RuntimeError)
    case(5, lambda: native.detect({}), TypeError)
    case(6, lambda: native.detect(image.astype(np.float32)), TypeError)
    case(7, lambda: native.detect(image[::-1]), TypeError)
    case(8, lambda: native.detect(np.zeros((513, 1, 3), np.uint8)), ValueError)
    case(9, lambda: native.detect(np.zeros((0, 1, 3), np.uint8)), ValueError)
    case(10, lambda: native.detect(np.zeros((10, 10, 4), np.uint8)), ValueError)
    case(11, lambda: native.detect(np.zeros((10, 10), np.uint8)), ValueError)
    case(12, lambda: native.predict_five(image, [0, 1]), TypeError)
    case(13, lambda: native.predict_five(image, [10, 10, 0, 0]), ValueError)
    case(14, lambda: native.predict_five(image, [0, 0, 256, 256]), ValueError)
    case(15, lambda: native.predict_five(image, [-1, 0, 20, 20]), ValueError)
    case(16, lambda: native.predict_five(image, [0, 0, float('nan'), 20]), TypeError)
    case(17, lambda: native.encode_128(np.zeros((149, 150, 3), np.uint8)), ValueError)
    case(18, lambda: native.encode_128(np.full((150, 150, 3), np.nan)), TypeError)
    case(19, lambda: native.prepare_components('/tmp/model.dat'), TypeError)
    case(20, lambda: native.prepare_components('https://unapproved.invalid/model'), TypeError)
    case(21, lambda: native.prepare_components({'approved': True}), TypeError)
    case(22, lambda: native.prepare_components('shape_predictor_68_face_landmarks'), TypeError)
    native.model_execution_api_available = True
    try:
        case(23, native.prepare_components, RuntimeError)
    finally:
        native.model_execution_api_available = False
    os.environ['FOC_ALLOW_MODELS'] = '1'
    try:
        case(24, native.prepare_components, RuntimeError)
    finally:
        del os.environ['FOC_ALLOW_MODELS']

    def no_extra_loaders():
        for name in ['deserialize', 'load_image', 'get_frontal_face_detector', 'load_model', 'from_file']:
            assert not hasattr(native, name)
    case(25, no_extra_loaders)
    case(26, lambda: native.validate_detection_input(np.zeros((512, 512, 3), np.uint8)))
    case(27, lambda: native.validate_landmark_input(image, box))
    case(28, lambda: native.validate_encoder_input(chip))
    started = time.monotonic()

    def repeated():
        for _ in range(1000):
            try:
                native.prepare_components()
            except RuntimeError as exc:
                assert str(exc) == 'a1b_second_review_required'
            else:
                raise AssertionError('Repeated denial bypassed')
    case(29, repeated)
    case(30, lambda: native.align_chip(image, [[1, 1]] * 5), ValueError)
    case(31, lambda: native.predict_five(image, [0, 0, 2**100, 20]), TypeError)

    def untouched():
        counters = native.boundary_counters()
        assert counters['review_denials'] >= 1000
        assert counters['model_open_attempts'] == counters['deserialization_attempts'] == counters['inference_attempts'] == 0
    case(32, untouched)
    assert time.monotonic() - started < 5
    assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss < 262144
    return {'tests': outcomes, 'boundary_counters': native.boundary_counters(),
            'repeat_denial_wall_ms': (time.monotonic() - started) * 1000,
            'model_execution_api_available': False, 'model_inference_executed': False}
