from flask import render_template, request, redirect, url_for, session, flash, Blueprint
from werkzeug.security import check_password_hash
from models import get_conect_bd