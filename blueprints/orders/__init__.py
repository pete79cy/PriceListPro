from flask import Blueprint

orders = Blueprint('orders', __name__, url_prefix='/orders')

from . import routes, api