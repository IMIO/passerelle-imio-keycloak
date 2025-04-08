from builtins import str

import json
import requests
from django.db import models
from django.http import Http404
from django.http import HttpResponse
from django.urls import reverse
from passerelle.base.models import BaseResource
from passerelle.utils.api import endpoint
from passerelle.utils.jsonresponse import APIError
from requests.exceptions import ConnectionError
from requests import RequestException


class KeycloakConnector(BaseResource):
    """
    Connecteur Keycloak
    """

    url = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="URL",
        help_text="URL de l'application Keycloak",
    )
    username = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Utilisateur",
    )
    password = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Mot de passe",
    )
    client_id = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="id client",
    )
    api_description = "Connecteur permettant d'intéragir avec Keycloak"
    category = "Connecteurs iMio"

    class Meta:
        verbose_name = "Connecteur Keycloak"

    @endpoint(
        methods=["get"],
        name="get-bearer-token",
        perm="can_access",
        description="Récupérer le Bearer Token",
        long_description="Récupérer le Bearer Token.",
        display_order=1,
        display_category="Access",
    )
    def access_token(self, request):
        url = f"{self.url}realms/master/protocol/openid-connect/token"  # Url et endpoint à contacter
        payload = f'client_id={self.client_id}&password={self.password}&grant_type=password&username={self.username}'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = requests.post(url=url, headers=headers, data=payload)
        access_token = r.json()["access_token"]
        return {"access_token": access_token}
    
    @endpoint(
        methods=["get"],
        name="read-users",
        perm='can_access',
        description="Récupérer la liste des users d'un realm",
        long_description="Récupérer la liste des users pour un realm donné",
        display_order=1,
        display_category="User",
        example_pattern="users/",
        pattern="^users/$",
        parameters={
            "realm": {
                "description": "Tenant Keycloak/Collectivité",
                "example_value": "imio",
            }
        }
    )
    def get_users(self, request, realm):
        url = f"{self.url}admin/realms/{realm}/users"  # Url et endpoint à contacter
        token = self.access_token(request)["access_token"]
        headers = {"Authorization": "Bearer " + token}
        r = requests.get(url=url, headers=headers)
        return {"data": r.json()}

    @endpoint(
        methods=["get"],
        name="read-user-groups",
        perm='can_access',
        description="Récupérer la liste de groupe d'un user",
        long_description="Récupérer la liste de groupe d'un user",
        display_order=2,
        display_category="User",
        parameters={
            "realm": {
                "description": "Tenant Keycloak/Collectivité",
                "example_value": "imio",
            },
            "user_id": {
                "description": "GUID de l'utilisateur",
                "example_value": "4d49f2eb-890d-47e9-8cb4-3910fc17b66b",
            }
        }
    )
    def get_user_groups(self, request, realm, user_id):
        url = f"{self.url}admin/realms/{realm}/users/{user_id}/groups"  # Url et endpoint à contacter
        token = self.access_token(request)["access_token"]
        headers = {"Authorization": "Bearer " + token}
        r = requests.get(url=url, headers=headers)
        return {"data": r.json()}

    @endpoint(
        methods=["get"],
        name="read-user-credentials",
        perm='can_access',
        description="Récupérer les types de connection d'un utilisateur",
        long_description="Récupérer les types de connection d'un utilisateur",
        display_order=3,
        display_category="User",
        parameters={
            "realm": {
                "description": "Tenant Keycloak/Collectivité",
                "example_value": "imio",
            },
            "user_id": {
                "description": "GUID de l'utilisateur",
                "example_value": "4d49f2eb-890d-47e9-8cb4-3910fc17b66b",
            }
        }
    )
    def get_user_credentials(self, request, realm, user_id):
        url = f"{self.url}admin/realms/{realm}/users/{user_id}/credentials"  # Url et endpoint à contacter
        token = self.access_token(request)["access_token"]
        headers = {"Authorization": "Bearer " + token}
        r = requests.get(url=url, headers=headers)
        return {"data": r.json()}

    @endpoint(
        methods=["post"],
        name="update-user",
        perm='can_access',
        description="Mettre à jour un utilisateur",
        long_description="Mettre à jour un utilisateur",
        display_order=4,
        display_category="User",
        parameters={
            "realm": {
                "description": "Tenant Keycloak/Collectivité",
                "example_value": "imio",
            },
            "user_id": {
                "description": "GUID de l'utilisateur",
                "example_value": "4d49f2eb-890d-47e9-8cb4-3910fc17b66b",
            }
        }
    )
    def update_user(self, request, realm, user_id):
        url = f"{self.url}admin/realms/{realm}/users/{user_id}"  # Url et endpoint à contacter
        token = self.access_token(request)["access_token"]
        headers = {
            "Authorization": "Bearer " + token,
            "Content-type": "application/json"
        }
        data = json.loads(request.body)
        data = {key: value for key, value in data.items() if value}
        r = requests.put(url=url, headers=headers, data=json.dumps(data))
        return r # status 204 ok

    @endpoint(
        methods=["post"],
        name="create-user",
        perm='can_access',
        description="Créer un utilisateur",
        long_description="Créer un utilisateur",
        display_order=5,
        display_category="User",
        parameters={
            "realm": {
                "description": "Tenant Keycloak/Collectivité",
                "example_value": "imio",
            },
            "user_id": {
                "description": "GUID de l'utilisateur",
                "example_value": "4d49f2eb-890d-47e9-8cb4-3910fc17b66b",
            },
            "central_realm": {
                "description": "Realm 'Central'",
                "example_value": "central",
            }
        }
    )
    def create_user(self, request, realm, user_id, central_realm=None):
        """
            "username": "drstranger@marvel.com",
            "enabled": True,
            "emailVerified": True,
            "firstName": "Stephen",
            "lastName": "Strange",
            "email": "drstranger@marvel.com"
        """
        url = f"{self.url}admin/realms/{realm}/users/{user_id}"  # Url et endpoint à contacter
        token = self.access_token(request)["access_token"]
        headers = {
            "Authorization": "Bearer " + token,
            "Content-type": "application/json"
        }
        r = requests.post(url=url, headers=headers, data=request.body)
        global_response = {"original realm": r}
        if central_realm:
            url = f"{self.url}admin/realms/{central_realm}/users/{user_id}"
            r = requests.post(url=url, headers=headers, data=request.body)
            global_response["central realm"] = r
        return global_response #status 201 ok

    def get_user_groups(self, request, realm, user_id):
        url = f"{self.url}admin/realms/{realm}/users/{user_id}/groups"  # Url et endpoint à contacter
        token = self.access_token(request)["access_token"]
        headers = {"Authorization": "Bearer " + token}
        r = requests.get(url=url, headers=headers)
        return {"data": r.json()}

    @endpoint(
        methods=["get"],
        name="read-user-id",
        perm='can_access',
        description="Récupérer les types de connection d'un utilisateur",
        long_description="Récupérer les types de connection d'un utilisateur",
        display_order=3,
        display_category="User",
        parameters={
            "realm": {
                "description": "Tenant Keycloak/Collectivité",
                "example_value": "imio",
            },
            "user_id": {
                "description": "GUID de l'utilisateur",
                "example_value": "4d49f2eb-890d-47e9-8cb4-3910fc17b66b",
            }
        }
    )
    def get_user_credentials(self, request, realm, user_id):
        url = f"{self.url}admin/realms/{realm}/users/{user_id}/credentials"  # Url et endpoint à contacter
        token = self.access_token(request)["access_token"]
        headers = {"Authorization": "Bearer " + token}
        r = requests.get(url=url, headers=headers)
        return {"data": r.json()}