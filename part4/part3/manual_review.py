import unittest
import requests
import sqlite3
from flask_bcrypt import Bcrypt
import uuid
from datetime import datetime

conn = sqlite3.connect('./instance/development.db')
cursor = conn.cursor()
bcrypt = Bcrypt()

user_id = str(uuid.uuid4())
password = bcrypt.generate_password_hash('adminpassword').decode('utf-8')
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

user = (user_id, 'Julien', 'Monte', 'julien.monte@gmail.com', password, 1, now, now)

cursor.execute("DELETE FROM users")
cursor.execute("INSERT INTO users (id, first_name, last_name, email, password, is_admin, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", user)

conn.commit()
conn.close()

class TestAPI(unittest.TestCase):
	url = 'http://localhost:5000/api/v1/'
	headers = {'Content-Type': 'application/json'}
	user_id = None
	place_id = None
	review_id = None
	user1_token = None
	user2_token = None
	admin_token = None
	invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0MjIyNjEyNCwianRpIjoiYjVkYzk2ZTktMWIxNS00MjViLWI5ZjctYzYxOGI5Zjc0MzdiIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjU5ZDk5MGZiLTVjYmYtNGNjZC1iMWQ5LWMxNzQyMjhhZjE4YyIsIm5iZiI6MTc0MjIyNjEyNCwiY3NyZiI6ImQ0ZGYwNTU5LWQ4NWEtNDRhZi1iNDg3LTg1OTdhNDg1ZjAyZSIsImV4cCI6MTc0MjIyNzAyNCwiaXNfYWRtaW4iOmZhbHNlfQ._YmDIgOqEKZa_dvmJx0dvvM5cPjeaAvyA_A3NUQKvXM"
	amenity_id = None
	
	def test_01_create_user(self):
		user_data = {'first_name': 'John', 'last_name': 'Doe', 'email': 'john.doe@example.com', 'password': 'password'}
		response = requests.post(self.url + 'users/', json=user_data, headers=self.headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 201)
			self.assertIn('id', response_data)
			TestAPI.user_id = response_data['id']
			user_data = {'first_name': 'Jean', 'last_name': 'Dupon', 'email': 'jean.dupont@example.com', 'password': 'password'}
			requests.post(self.url + 'users/', json=user_data, headers=self.headers)
			print("✅ test_01_create_user passed")
		except:
			print("❌ test_01_create_user failed")

	def test_02_get_user(self):
		response = requests.get(self.url + 'users/' + str(TestAPI.user_id), headers=self.headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 200)
			self.assertEqual(response_data['id'], TestAPI.user_id)
			self.assertEqual(response_data['first_name'], 'John')
			self.assertEqual(response_data['last_name'], 'Doe')
			self.assertEqual(response_data['email'], 'john.doe@example.com')
			self.assertNotIn('password', response_data)
			print("✅ test_02_get_user passed")
		except:
			print("❌ test_02_get_user failed")
	
	def test_03_user_login(self):
		login_data = {'email': 'john.doe@example.com', 'password': 'password'}
		response = requests.post(self.url + 'auth/login', json=login_data, headers=self.headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 200)
			self.assertIn('access_token', response_data)
			TestAPI.user1_token = response_data['access_token']
			login_data = {'email': 'jean.dupont@example.com', 'password': 'password'}
			response = requests.post(self.url + 'auth/login', json=login_data, headers=self.headers)
			self.assertEqual(response.status_code, 200)
			response_data = response.json()
			TestAPI.user2_token = response_data['access_token']
			login_data = {'email': 'julien.monte@gmail.com', 'password': 'adminpassword'}
			response = requests.post(self.url + 'auth/login', json=login_data, headers=self.headers)
			self.assertEqual(response.status_code, 200)
			response_data = response.json()
			TestAPI.admin_token = response_data['access_token']
			print("✅ test_03_user_login passed")
		except:
			print("❌ test_03_user_login failed")

	def test_04_user_login_with_wrong_data(self):
		login_data = {'email': 'john.doe@example.com', 'password': 'passwor'}
		response = requests.post(self.url + 'auth/login', json=login_data, headers=self.headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 401)
			self.assertEqual(response_data['error'], 'Invalid credentials')
			print("✅ test_04_user_login_with_wrong_data passed")
		except:
			print("❌ test_04_user_login_with_wrong_data failed")
	
	def test_05_protected_route(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.user1_token}
		response = requests.get(self.url + 'protected', headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 200)
			self.assertEqual(response_data['message'], 'Hello, user ' + TestAPI.user_id)
			print("✅ test_05_protected_route passed")
		except:
			print("❌ test_05_protected_route failed")
	
	def test_06_protected_route_with_invalid_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.invalid_token}
		response = requests.get(self.url + 'protected', headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 401)
			print("✅ test_06_protected_route_with_invalid_token passed")
		except:
			print("❌ test_06_protected_route_with_invalid_token failed")
	
	def test_07_create_place_with_valid_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.user1_token}
		place_data = {'title': 'My Place', 'description': 'A place to stay', 'price': 100.0, 'latitude': 54.0, 'longitude': 19.0}
		response = requests.post(self.url + 'places/', json=place_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 201)
			self.assertIn('id', response_data)
			TestAPI.place_id = response_data['id']
			print("✅ test_07_create_place_with_valid_token passed")
		except:
			print("❌ test_07_create_place_with_valid_token failed")
	
	def test_08_create_place_with_invalid_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.invalid_token}
		place_data = {'title': 'My Place', 'description': 'A place to stay', 'price': 100.0, 'latitude': 54.0, 'longitude': 19.0}
		response = requests.post(self.url + 'places/', json=place_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 401)
			print("✅ test_08_create_place_with_invalid_token passed")
		except:
			print("❌ test_08_create_place_with_invalid_token failed")

	def test_09_update_place_with_valid_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.user1_token}
		place_data = {'title': 'My Place', 'description': 'A place to stay', 'price': 70.0, 'latitude': 54.0, 'longitude': 19.0}
		response = requests.put(self.url + 'places/' + str(TestAPI.place_id), json=place_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 200)
			print("✅ test_09_update_place_with_valid_token passed")
		except:
			print("❌ test_09_update_place_with_valid_token failed")

	def test_10_update_place_with_invalid_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.invalid_token}
		place_data = {'title': 'My Place', 'description': 'A place to stay', 'price': 1000.0, 'latitude': 54.0, 'longitude': 19.0}
		response = requests.put(self.url + 'places/' + str(TestAPI.place_id), json=place_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 401)
			print("✅ test_10_update_place_with_invalid_token passed")
		except:
			print("❌ test_10_update_place_with_invalid_token failed")

	def test_11_update_place_with_wrong_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.user2_token}
		place_data = {'title': 'My Place', 'description': 'A place to stay', 'price': 1000.0, 'latitude': 54.0, 'longitude': 19.0}
		response = requests.put(self.url + 'places/' + str(TestAPI.place_id), json=place_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 403)
			print("✅ test_11_update_place_with_wrong_token passed")
		except:
			print("❌ test_11_update_place_with_wrong_token failed")

	def test_12_create_review_with_valid_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.user2_token}
		review_data = {'place_id': TestAPI.place_id, 'rating': 4, 'text': 'Nice place'}
		response = requests.post(self.url + 'reviews/', json=review_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 201)
			review_data = {'place_id': TestAPI.place_id, 'rating': 4, 'text': 'Nice place'}
			response = requests.post(self.url + 'reviews/', json=review_data, headers=headers)
			TestAPI.review_id = response_data['id']
			response_data = response.json()
			self.assertEqual(response.status_code, 400)
			self.assertEqual(response_data['error'], 'You have already reviewed this place.')
			print("✅ test_12_create_review_with_valid_token passed")
		except Exception as e:
			print(e)
			print("❌ test_12_create_review_with_valid_token failed")

	def test_13_create_review_with_invalid_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.invalid_token}
		review_data = {'place_id': TestAPI.place_id, 'rating': 4, 'text': 'Nice place'}
		response = requests.post(self.url + 'reviews/', json=review_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 401)
			print("✅ test_13_create_review_with_invalid_token passed")
		except Exception as e:
			print(e)
			print("❌ test_13_create_review_with_invalid_token failed")

	def test_14_create_review_on_owned_place(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.user1_token}
		review_data = {'place_id': TestAPI.place_id, 'rating': 4, 'text': 'Nice place'}
		response = requests.post(self.url + 'reviews/', json=review_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 400)
			self.assertEqual(response_data['error'], 'You cannot review your own place.')
			print("✅ test_14_create_review_on_owned_place passed")
		except Exception as e:
			print(e)
			print("❌ test_14_create_review_on_owned_place failed")

	def test_15_update_review_with_wrong_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.user1_token}
		review_data = {'place_id': TestAPI.place_id, 'rating': 3, 'text': 'Nice place but it can be more clean'}
		response = requests.put(self.url + f"reviews/{TestAPI.review_id}", json=review_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 403)
			print("✅ test_15_update_review_with_wrong_token passed")
		except Exception as e:
			print(e)
			print("❌ test_15_update_review_with_wrong_token failed")

	def test_16_update_review_with_invalid_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.invalid_token}
		review_data = {'place_id': TestAPI.place_id, 'rating': 3, 'text': 'Nice place but it can be more clean'}
		response = requests.put(self.url + f"reviews/{TestAPI.review_id}", json=review_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 401)
			print("✅ test_16_update_review_with_invalid_token passed")
		except Exception as e:
			print(e)
			print("❌ test_15_update_review_with_invalid_token failed")

	def test_17_update_review_with_valid_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.user2_token}
		review_data = {'place_id': TestAPI.place_id, 'rating': 3, 'text': 'Nice place but it can be more clean'}
		response = requests.put(self.url + f"reviews/{TestAPI.review_id}", json=review_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 200)
			print("✅ test_17_update_review_with_valid_token passed")
		except Exception as e:
			print(e)
			print("❌ test_17_update_review_with_valid_token failed")

	def test_18_delete_review_with_wrong_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.user1_token}
		response = requests.delete(self.url + f"reviews/{TestAPI.review_id}", headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 403)
			print("✅ test_18_delete_review_with_wrong_token passed")
		except Exception as e:
			print(e)
			print("❌ test_18_delete_review_with_wrong_token failed")

	def test_19_delete_review_with_invalid_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.invalid_token}
		response = requests.delete(self.url + f"reviews/{TestAPI.review_id}", headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 401)
			print("✅ test_19_delete_review_with_invalid_token passed")
		except Exception as e:
			print(e)
			print("❌ test_19_delete_review_with_invalid_token failed")

	def test_20_delete_review_with_valid_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.user2_token}
		response = requests.delete(self.url + f"reviews/{TestAPI.review_id}", headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 200)
			response = requests.get(self.url + f"reviews/{TestAPI.review_id}", headers=headers)
			self.assertEqual(response.status_code, 404)
			print("✅ test_20_update_review_with_valid_token passed")
		except Exception as e:
			print(e)
			print("❌ test_20_update_review_with_valid_token failed")

	def test_21_update_user_with_wrong_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.user2_token}
		user_data = {'first_name': 'John', 'last_name': 'Doe', 'email': 'update@example.com'}
		response = requests.put(self.url + f"users/{TestAPI.user_id}", json=user_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 403)
			print("✅ test_21_update_user_with_wrong_token passed")
		except Exception as e:
			print(e)
			print("❌ test_21_update_user_with_wrong_token failed")

	def test_22_update_user_with_invalid_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.invalid_token}
		user_data = {'first_name': 'John', 'last_name': 'Doe', 'email': 'update@example.com'}
		response = requests.put(self.url + f"users/{TestAPI.user_id}", json=user_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 401)
			print("✅ test_22_update_user_with_invalid_token passed")
		except Exception as e:	
			print(e)
			print("❌ test_22_update_user_with_invalid_token failed")

	def test_23_update_user_with_valid_token_and_wrong_data(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.user1_token}
		user_data = {'first_name': 'John', 'last_name': 'Doe', 'email': 'update@example.com'}
		response = requests.put(self.url + f"users/{TestAPI.user_id}", json=user_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 400)
			self.assertEqual(response_data['error'], 'You cannot modify email or password.')
			user_data = {'first_name': 'John', 'last_name': 'Doe', 'password': 'update_password'}
			response = requests.put(self.url + f"users/{TestAPI.user_id}", json=user_data, headers=headers)
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 400)
			self.assertEqual(response_data['error'], 'You cannot modify email or password.')
			print("✅ test_23_update_user_with_valid_token_and_wrong_data passed")
		except Exception as e:
			print(e)
			print("❌ test_23_update_user_with_valid_token_and_wrong_data failed")

	def test_24_update_user_with_valid_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.user1_token}
		user_data = {'first_name': 'John', 'last_name': 'Dope'}
		response = requests.put(self.url + f"users/{TestAPI.user_id}", json=user_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 200)
			self.assertEqual(response_data['last_name'], 'Dope')
			print("✅ test_24_update_user_with_valid_token passed")
		except Exception as e:
			print(e)
			print("❌ test_24_update_user_with_valid_token failed")

	def test_25_create_admin_without_admin_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.user1_token}
		user_data = {'first_name': 'Fred', 'last_name': 'Pola', 'email': 'fred.pola@gmail.com', 'password': 'adminpassword', 'is_admin': True}
		response = requests.post(self.url + 'users/', json=user_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 403)
			headers = {'Content-Type': 'application/json'}
			response = requests.post(self.url + 'users/', json=user_data, headers=headers)
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 401)
			print("✅ test_25_create_admin_without_admin_token passed")
		except Exception as e:	
			print(e)
			print("❌ test_25_create_admin_without_admin_token failed")

	def test_26_create_admin_with_admin_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.admin_token}
		user_data = {'first_name': 'Fred', 'last_name': 'Pola', 'email': 'fred.pola@gmail.com', 'password': 'adminpassword', 'is_admin': True}
		response = requests.post(self.url + 'users/', json=user_data, headers=headers)
	
		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 201)
			print("✅ test_26_create_admin_with_admin_token passed")
		except Exception as e:
			print(e)
			print("❌ test_26_create_admin_with_admin_token failed")

	def test_27_upgrade_admin_privileges_without_admin_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.user1_token}
		user_data = {'first_name': 'John', 'last_name': 'Doe', 'is_admin': True}
		response = requests.put(self.url + f'users/{TestAPI.user_id}', json=user_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 403)
			print("✅ test_27_upgrade_admin_privileges_without_admin_token passed")
		except Exception as e:
			print(e)
			print("❌ test_27_upgrade_admin_privileges_without_admin_token failed")

	def test_28_upgrade_admin_privileges_with_admin_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.admin_token}
		user_data = {'first_name': 'John', 'last_name': 'Doe', 'is_admin': True}
		response = requests.put(self.url + f'users/{TestAPI.user_id}', json=user_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 200)
			user_data = {'first_name': 'John', 'last_name': 'Doe', 'is_admin': False}
			response = requests.put(self.url + f'users/{TestAPI.user_id}', json=user_data, headers=headers)
			print("✅ test_28_upgrade_admin_privileges_with_admin_token passed")
		except Exception as e:
			print(e)
			print("❌ test_28_upgrade_admin_privileges_with_admin_token failed")
	
	def test_29_update_mail_and_password_with_admin_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.admin_token}
		user_data = {'email': 'test@gmail.com', 'password': 'testpassword'}
		response = requests.put(self.url + f'users/{TestAPI.user_id}', json=user_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 200)
			login_data = {'email': 'test@gmail.com', 'password': 'testpassword'}
			response = requests.post(self.url + 'auth/login', json=login_data, headers=TestAPI.headers)
			self.assertEqual(response.status_code, 200)
			response_data = response.json()
			self.assertIn('access_token', response_data)
			TestAPI.user1_token = response_data['access_token']
			print("✅ test_29_update_mail_and_password_with_admin_token passed")
		except Exception as e:
			print(e)
			print("❌ test_29_update_mail_and_password_with_admin_token failed")
	
	def test_30_create_amenity_without_admin_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.user1_token}
		amenity_data = {'name': 'Pool'}
		response = requests.post(self.url + 'amenities/', json=amenity_data, headers=TestAPI.headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 401)
			response = requests.post(self.url + 'amenities/', json=amenity_data, headers=headers)
			self.assertEqual(response.status_code, 403)
			print("✅ test_30_create_amenity_without_admin_token passed")
		except Exception as e:
			print(e)
			print("❌ test_30_create_amenity_without_admin_token failed")

	def test_31_create_amenity_with_admin_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.admin_token}
		amenity_data = {'name': 'Pool'}
		response = requests.post(self.url + 'amenities/', json=amenity_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 201)
			TestAPI.amenity_id = response_data['id']
			print("✅ test_31_create_amenity_with_admin_token passed")
		except Exception as e:
			print(e)
			print("❌ test_31_create_amenity_with_admin_token failed")

	def test_32_update_review_with_admin_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.user2_token}
		review_data = {'place_id': TestAPI.place_id, 'rating': 4, 'text': 'Nice place but it can be more clean'}
		response = requests.post(self.url + "reviews/", json=review_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 201)
			TestAPI.review_id = response_data['id']
			headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.admin_token}
			review_data = {'place_id': TestAPI.place_id, 'rating': 3, 'text': 'Nice place but it can be more clean'}
			response = requests.put(self.url + f"reviews/{response_data['id']}", json=review_data, headers=headers)
			response_data = response.json()
			self.assertEqual(response_data['rating'], 3)
			print("✅ test_32_update_review_with_admin_token passed")
		except Exception as e:
			print(e)
			print("❌ test_32_update_review_with_admin_token failed")
	
	def test_33_delete_review_with_admin_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.admin_token}
		response = requests.delete(self.url + f"reviews/{TestAPI.review_id}", headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 200)
			response = requests.get(self.url + f"reviews/{TestAPI.review_id}", headers=headers)
			self.assertEqual(response.status_code, 404)
			print("✅ test_33_delete_review_with_admin_token passed")
		except Exception as e:
			print(e)
			print("❌ test_33_delete_review_with_admin_token failed")
	
	def test_34_update_amenity_without_admin_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.user1_token}
		amenity_data = {'name': 'Swimming Pool'}
		response = requests.put(self.url + f'amenities/{TestAPI.amenity_id}', json=amenity_data, headers=TestAPI.headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 401)
			response = requests.put(self.url + f'amenities/{TestAPI.amenity_id}', json=amenity_data, headers=headers)
			self.assertEqual(response.status_code, 403)
			print("✅ test_34_update_amenity_without_admin_token passed")
		except Exception as e:
			print(e)
			print("❌ test_34_update_amenity_without_admin_token failed")

	def test_35_update_amenity_with_admin_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.admin_token}
		amenity_data = {'name': 'Swimming Pool'}
		response = requests.put(self.url + f'amenities/{TestAPI.amenity_id}', json=amenity_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 200)
			self.assertEqual(response_data['name'], 'Swimming Pool')
			print("✅ test_35_update_amenity_with_admin_token passed")
		except Exception as e:
			print(e)
			print("❌ test_35_update_amenity_with_admin_token failed")

	def test_36_update_place_with_admin_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.admin_token}
		place_data = {'title': 'Villa in Town', 'description': 'A place to stay', 'price': 100.0, 'latitude': 54.0, 'longitude': 19.0}
		response = requests.put(self.url + 'places/' + str(TestAPI.place_id), json=place_data, headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 200)
			self.assertEqual(response_data['title'], 'Villa in Town')
			print("✅ test_36_update_place_with_admin_token passed")
		except Exception as e:
			print(e)
			print("❌ test_36_update_place_with_admin_token failed")
	
	def test_37_delete_place_with_admin_token(self):
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TestAPI.admin_token}
		response = requests.delete(self.url + 'places/' + str(TestAPI.place_id), headers=headers)

		try:
			response_data = response.json()
			print(response_data)
			self.assertEqual(response.status_code, 200)
			response = requests.get(self.url + 'places/' + str(TestAPI.place_id), headers=headers)
			self.assertEqual(response.status_code, 404)
			TestAPI.place_id = None
			print("✅ test_37_delete_place_with_admin_token passed")
		except Exception as e:
			print(e)
			print("❌ test_37_delete_place_with_admin_token failed")

unittest.main()
