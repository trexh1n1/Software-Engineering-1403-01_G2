import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.shortcuts import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from database.query import create_db_connection, save_user
from database.secret import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

# Create your views here.


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def suggest_api(request):
    data = json.loads(request.body)

    past_word = data.get("past_word")
    suggestions = []

    if past_word:
        mydb = create_db_connection(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)
        cursor = mydb.cursor()

        try:
            cursor.execute(
                """
                SELECT current_word, probability
                FROM G10_word_probabilities
                WHERE past_word = %s
                ORDER BY probability DESC
                LIMIT 5;
                """,
                (past_word,),
            )
            suggestions = cursor.fetchall()
        except Exception:
            return HttpResponse("Error fetching suggestions.", status=500)
        finally:
            cursor.close()
            mydb.close()

    suggestions_data = [
        {"current_word": word, "probability": prob} for word, prob in suggestions
    ]

    return Response({"suggestions": suggestions_data})


@api_view(["GET"])
def csrf_api(request):
    csrf_token = get_token(request)
    return Response({"csrf": csrf_token})


@api_view(["POST"])
def signup_api(request):
    data = json.loads(request.body)

    uname = data.get("username")
    email = data.get("email")
    pass1 = data.get("password1")
    pass2 = data.get("password2")
    name = data.get("name")
    age = data.get("age")

    if pass1 != pass2:
        return HttpResponse("Passwords do not match", status=400)
    else:
        if User.objects.filter(username=uname).exists():
            return HttpResponse("Duplicate username.", status=400)

        try:
            mydb = create_db_connection(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)

            my_user = User.objects.create_user(uname, email, pass1)
            my_user.save()
            save_user(mydb, name, uname, pass1, email, age)
        except Exception:
            return HttpResponse("Registeration failed.", status=403)
        finally:
            mydb.close()

    return HttpResponse()


@api_view(["POST"])
def login_api(request):
    data = json.loads(request.body)

    username = data.get("username")
    pass1 = data.get("pass")

    user = authenticate(request, username=username, password=pass1)

    if user is None:
        return HttpResponse("Username or Password is incorrect.", status=403)

    login(request, user)

    return HttpResponse()


@api_view(["POST"])
def logout_api(request):
    logout(request)
