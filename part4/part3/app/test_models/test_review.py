from ..models.review import Review
import unittest

class TestUser(unittest.TestCase):
    def test_review_creation(self):
        review = Review(name="Wi-Fi")
        self.assertEqual(review.name, "Wi-Fi")

    '''def test_review_max_length(self):
        with self.assertRaises(ValueError) as context:
            review("abdcdefghijklmnopqrstuvwxyzabdcdefghijklmnopqrstuvwxyz")
        self.assertEqual(str(context.exception), "Name must be 50 characters max.")

    def test_review_missing_field(self):
        with self.assertRaises(TypeError):
            review()

    def test_review_update(self):
        review = review(name="Wi-Fi")
        new_data = {'name': "Wi-fi"}
        review.update(new_data)
        self.assertEqual(review.to_dict(), {'id': review.id, 'name': "Wi-fi"})

    def test_user_update_fail(self):
        review = review(name="Wi-Fi")
        with self.assertRaises(ValueError) as context:
            review.name = "abdcdefghijklmnopqrstuvwxyzabdcdefghijklmnopqrstuvwxyz"
        self.assertEqual(str(context.exception), "Name must be 50 characters max.")'''

if __name__ == "__main__":
    unittest.main()
