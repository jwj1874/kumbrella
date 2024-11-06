from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from db import get_db_connection
import pymysql
return_bp = Blueprint('return', __name__)


@return_bp.route('/return')
def return_process():
    