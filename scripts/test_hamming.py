import unittest

from hamming import decode_12_7, encode_11_7, encode_12_7, exhaustive_verification, inject


class HammingTests(unittest.TestCase):
    def test_known_zero_word(self):
        self.assertEqual(encode_11_7(0), (0,) * 11)
        self.assertEqual(encode_12_7(0), (0,) * 12)

    def test_single_error_correction(self):
        data = (1, 0, 1, 1, 0, 1, 0)
        codeword = encode_12_7(data)
        for position in range(1, 13):
            self.assertEqual(decode_12_7(inject(codeword, [position])).data, data)

    def test_exhaustive_counts(self):
        self.assertEqual(exhaustive_verification(), {
            "data_words": 128, "single_errors": 1536, "double_errors": 8448
        })


if __name__ == "__main__":
    unittest.main()
