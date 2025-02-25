import json
import pytest

from django.urls import reverse


def test_hello_world():
    assert "hello_world" == "hello_world"
    assert "foo" != "bar"
    print("foo")


def test_ping(client):
    url = reverse("ping")
    response = client.get(url)
    content = json.loads(response.content)

    assert response.status_code == 200
    assert content["ping"] == "pong!"


# State     Explaination                                            Code
# -----     -------------------------------------------------       -----------------------------------
# Given     the state of the application before the test runs       setup code, fixtures, database state
# When      the behaviour or logic being tested                     code under test
# Then      the expected changes based on the behavior              asserts


# def test_ping(client):
# Given
# client

# When
# url = reverse("ping")
# response = client.get(url)
# content = json.loads(response.content)

# # Then
# assert response.status_code == 200
# assert content["ping"] == "pong!"
