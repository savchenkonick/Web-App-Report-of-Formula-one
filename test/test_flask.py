import flask
import pytest
import json
from flaskr import app, api


@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client


def test_request():
    with app.app.test_request_context('report/pilots?pilot_id=BHS'):
        assert flask.request.path == '/report/pilots'
        assert flask.request.args['pilot_id'] == 'BHS'


def test_client():
    with app.app.test_client() as tc:
        response = tc.get('/')
        assert response.status_code == 200


def test_json():
    with api.app.test_client() as tc:
        resp = tc.get('api/v1/report/?format=json')
        json_data = json.loads(resp.data)
        assert 'Monaco Q1 Results' in json_data
