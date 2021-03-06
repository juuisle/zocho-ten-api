# -------------------------------------------------------------------------------------------------
# Zocho-Ten Smart Ecosystem
#
# The MIT License (MIT)
# Copyright © 2020 Juuis Le
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
# and associated documentation files (the “Software”), to deal in the Software without restriction, 
# including without limitation the rights to use, copy, modify, merge, publish, distribute, 
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software 
# is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies 
# or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS 
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# -------------------------------------------------------------------------------------------------

from flask import Response, request
from flask_restful import Resource
from database.models import UserModel
from blacklist import BLACKLIST
from libs.strings import gettext

from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
)


class UserManagement(Resource):
  """ '/user' endpoint.
  The name of the function is the HTTP methods. 
  This application is for internal use. Therefore, all users will be
  created and managed my administrator
  """

  def get(self):
    pass

  def post(self):
    """ Create new user """

    user_data = request.get_json()

    if UserModel.find_by_username(user_data["user_name"]):
      return {"message": gettext("error_user_exists")}, 400
    
    if UserModel.find_by_email(user_data["email"]):
      return {"message": gettext("error_user_exists")}, 400
    
    user = UserModel(**user_data)
    try:
      user.save()
    except:
      return {"message": gettext("error_user_creating")}, 500
    
    return Response(user.to_json(), mimetype="application/json", status=200)

  def delete(self):
    """ Delete user """
    
    user_data = request.get_json()

    user = UserModel.find_by_username(user_data["user_name"])
    if user is None: 
      user = UserModel.find_by_email(user_data["email"])
      if user is None: 
        return {"message": gettext("error_user_not_found")}, 404
    
    try: 
      user.delete()
    except:
      return {"message": gettext("error_user_deleting")}, 500
  
    return {"message": gettext("user_deleted")}, 200


class UserLogin(Resource):
  """ '/login' endpoint.
  The name of the function is the HTTP methods. 
  """

  def post(self):
    user_data = request.get_json()
    print(user_data["user_name"])
    user = UserModel.find_by_username(user_data["user_name"])
    
    if user and safe_str_cmp(user.password, user_data["password"]):
      access_token = create_access_token(user.user_name, fresh=True)
      refresh_token = create_refresh_token(user.user_name)
      return (
          { "access_token": access_token, 
            "refresh_token": refresh_token
          }, 200,
      )
    return {"message": gettext("error_user_invalid_credentials")}, 401



class UserLogout(Resource):
  """ '/userlogin' endpoint.
  The name of the function is the HTTP methods. 
  """
  @jwt_required
  def post(self):
      jti = get_raw_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
      user_name = get_jwt_identity()
      BLACKLIST.add(jti)
      return {"message": gettext("user_logged_out").format(user_name)}, 200


class TokenRefresh(Resource):
  @jwt_refresh_token_required
  def post(self):
    user_name = get_jwt_identity()
    return {
      'access_token': create_access_token(identity=user_name)
    }