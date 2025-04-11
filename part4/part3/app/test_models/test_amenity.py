from app.models.amenity import Amenity
import unittest

class TestUser(unittest.TestCase):
    def test_amenity_creation(self):
        amenity = Amenity(name="Wi-Fi")
        self.assertEqual(amenity.name, "Wi-Fi")

    def test_amenity_max_length(self):
        with self.assertRaises(ValueError) as context:
            Amenity("abdcdefghijklmnopqrstuvwxyzabdcdefghijklmnopqrstuvwxyz")
        self.assertEqual(str(context.exception), "Name must be 50 characters max.")

    def test_amenity_missing_field(self):
        with self.assertRaises(TypeError):
            Amenity()

    def test_amenity_update(self):
        amenity = Amenity(name="Wi-Fi")
        new_data = {'name': "Wi-fi"}
        amenity.update(new_data)
        self.assertEqual(amenity.to_dict(), {'id': amenity.id, 'name': "Wi-fi"})

    def test_user_update_fail(self):
        amenity = Amenity(name="Wi-Fi")
        with self.assertRaises(ValueError) as context:
            amenity.name = "abdcdefghijklmnopqrstuvwxyzabdcdefghijklmnopqrstuvwxyz"
        self.assertEqual(str(context.exception), "Name must be 50 characters max.")

if __name__ == "__main__":
    unittest.main()
