from django.test import SimpleTestCase, TestCase
from django.urls import reverse

# from products.models import Product, User


class TestProfilePage(TestCase):
    def test_profile_view_redirects_for_anonymous_users(self):
        """Test that anonymous users are redirected to the login page when trying to access the profile view."""
        response = self.client.get(reverse("profile"))

        # Check if the user was redirected to the login page
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile')}")

    def test_profile_view_accessible_for_authenticated_users(self):
        """Test that authenticated users can access the profile view and see their username."""
        # Create a test user
        User.objects.create_user(username="testuser", password="password123")

        # Log the user in
        self.client.login(username="testuser", password="password123")

        # Access the profile page
        response = self.client.get(reverse("profile"))

        # Check that the response status code is 200 (successful access)
        self.assertEqual(response.status_code, 200)

        # Check if the user's username is in the response content
        self.assertContains(response, "testuser")


class TestHomePage(SimpleTestCase):

    def test_homepage_uses_correct_template(self):
        """Test that the homepage view uses the correct template."""
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "index.html")

    def test_homepage_contains_welcome_message(self):
        """Test that the homepage contains the welcome message in the content."""
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Welcome to our Store!", status_code=200)


class TestProductsPage(TestCase):
    def setUp(self):
        """Create some products for testing."""
        Product.objects.create(name="Laptop", price=1000)
        Product.objects.create(name="Phone", price=800)

    def test_products_uses_correct_template(self):
        """Test that the products view uses the correct template."""
        response = self.client.get(reverse("products"))
        self.assertTemplateUsed(response, "products.html")

    def test_products_context(self):
        """Test that the products context contains the correct products."""
        response = self.client.get(reverse("products"))
        self.assertEqual(len(response.context["products"]), 2)
        self.assertContains(response, "Laptop")
        self.assertContains(response, "Phone")
        self.assertNotContains(response, "No products available")

    def test_products_view_no_products(self):
        """Test that the view behaves correctly when no products are available."""
        Product.objects.all().delete()  # Clear all products
        response = self.client.get(reverse("products"))
        self.assertEqual(len(response.context["products"]), 0)
        self.assertContains(response, "No products available")
