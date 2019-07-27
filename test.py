from client import *


def test_bgr2gray():
    src = np.array([[[91, 2, 79], [179, 52, 205], [236, 8, 181]],
                    [[239, 26, 248], [207, 218, 45], [183, 158, 101]]], dtype=np.uint8)
    ref = np.array([[35, 112, 86], [117, 165, 144]], dtype=np.uint8)
    out = bgr2gray(src)
    assert(np.all(out == ref)), 'test_bgr2gray FAILED'
    print('test_bgr2gray PASSED')


def test_gray2bin():
    src = np.random.uniform(low=0, high=256, size=[14, 15]).astype(np.uint8)
    out = gray2bin(src)
    numOutWhite = np.sum(out > 0)
    numRefWhite = np.sum(src > 127)
    assert(numOutWhite == numRefWhite), 'test_gray2bin FAILED'
    print('test_gray2bin PASSED')


def test_countPixels_1():
    src = np.array([255, 255, 0, 255, 0, 0, 255, 255, 255, 0, 0], dtype=np.uint8)
    xs, counts = countPixels(src)

    target_counts = np.array([2, 1, 1, 2, 3, 2], dtype=np.uint8)
    target_xs = np.array([0, 2, 3, 4, 6, 9], dtype=np.uint8)

    assert(np.all(counts == target_counts)), 'test_countPixels_1 (counts) FAILED'
    assert(np.all(xs == target_xs)), 'test_countPixels_1 (xs) FAILED'
    print('test_countPixels_1 PASSED')


def test_countPixels_2():
    src = np.array([0, 0, 255, 255, 0, 255, 0, 0, 255, 255, 255, 0, 0], dtype=np.uint8)
    xs, counts = countPixels(src)

    target_counts = np.array([2, 2, 1, 1, 2, 3, 2], dtype=np.uint8)
    target_xs = np.array([0, 2, 4, 5, 6, 8, 11], dtype=np.uint8)

    assert(np.all(counts == target_counts)), 'test_countPixels_2 (counts) FAILED'
    assert(np.all(xs == target_xs)), 'test_countPixels_2 (xs) FAILED'
    print('test_countPixels_2 PASSED')


def test_checkRatios_1():
    counts = np.array([1, 1, 3, 1, 1], dtype=np.uint8)
    assert(checkRatios(counts)), 'checkRatios_1 FAILED'
    print('checkRatios_1 PASSED')


def test_checkRatios_2():
    counts = np.array([2, 2, 6, 2, 2], dtype=np.uint8)
    assert(checkRatios(counts)), 'checkRatios_1 FAILED'
    print('checkRatios_1 PASSED')


def test_checkRatios_3():
    counts = np.array([3, 3, 10, 2, 3], dtype=np.uint8)
    assert(checkRatios(counts)), 'checkRatios_1 FAILED'
    print('checkRatios_1 PASSED')


def test_checkRatios_4():
    counts = np.array([3, 1, 9, 3, 3], dtype=np.uint8)
    assert(not checkRatios(counts)), 'checkRatios_1 FAILED'
    print('checkRatios_1 PASSED')


try:
    test_bgr2gray()
    test_gray2bin()
    test_countPixels_1()
    test_countPixels_2()
    test_checkRatios_1()
    test_checkRatios_2()
    test_checkRatios_3()
    test_checkRatios_4()
except Exception as e:
    print(str(e))
    exit(1)
