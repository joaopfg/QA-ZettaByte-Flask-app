from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.db import get_db

bp = Blueprint('frontpage', __name__)

@bp.route('/')
def index():
    return render_template('frontpage/index.html')