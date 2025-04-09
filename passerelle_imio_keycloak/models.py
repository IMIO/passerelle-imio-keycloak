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
        methods=["get"],
        name="delete-user-credential",
        perm='can_access',
        description="Supprimer un type de connexion d'un utilisateur",
        long_description="Supprimer un type de connexion d'un utilisateur",
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
            },
            "credential_id": {
                "description": "GUID du credential",
                "example_value": "98e95a9c-236d-4d1b-af70-e90a95248ecc",
            }
        }
    )
    def delete_user_credential(self, request, realm, user_id, credential_id):
        url = f"{self.url}admin/realms/{realm}/users/{user_id}/credentials/{credential_id}"  # Url et endpoint à contacter
        token = self.access_token(request)["access_token"]
        headers = {"Authorization": "Bearer " + token}
        r = requests.delete(url=url, headers=headers)
        r.raise_for_status()

    @endpoint(
        methods=["post"],
        name="update-user",
        perm='can_access',
        description="Mettre à jour un utilisateur",
        long_description="Mettre à jour un utilisateur",
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
        display_order=6,
        display_category="User",
        parameters={
            "realm": {
                "description": "Tenant Keycloak/Collectivité",
                "example_value": "imio",
            }
        }
    )
    def create_user(self, request, realm):
        """
            "username": "drstranger@marvel.com",
            "enabled": True,
            "emailVerified": True,
            "firstName": "Stephen",
            "lastName": "Strange",
            "email": "drstranger@marvel.com"
        """
        url = f"{self.url}admin/realms/{realm}/users"  # Url et endpoint à contacter
        token = self.access_token(request)["access_token"]
        headers = {"Authorization": "Bearer " + token}
        r = requests.post(url=url, headers=headers, data=request.body)
        r.raise_for_status()

    def get_user_groups(self, request, realm, user_id):
        url = f"{self.url}admin/realms/{realm}/users/{user_id}/groups"  # Url et endpoint à contacter
        token = self.access_token(request)["access_token"]
        headers = {"Authorization": "Bearer " + token}
        r = requests.get(url=url, headers=headers)
        return {"data": r.json()}

    @endpoint(
        methods=["get"],
        name="read-user-by-mail",
        perm='can_access',
        description="Récupérer un utilisateur via son adresse mail",
        long_description="Récupérer un utilisateur via son adresse mail",
        display_order=7,
        display_category="User",
        parameters={
            "realm": {
                "description": "Tenant Keycloak/Collectivité",
                "example_value": "imio",
            },
            "email": {
                "description": "mail de l'utilisateur",
                "example_value": "jordano.modesto@imio.be",
            }
        }
    )
    def get_user_by_mail(self, request, realm, email):
        url = f"{self.url}admin/realms/{realm}/users?email={email}"  # Url et endpoint à contacter
        token = self.access_token(request)["access_token"]
        headers = {"Authorization": "Bearer " + token}
        r = requests.get(url=url, headers=headers)
        return {"data": r.json()}

    @endpoint(
        methods=["get"],
        name="read-groups",
        perm='can_access',
        description="Récupérer la liste des groupes d'un realm",
        long_description="Récupérer la liste des groupes pour un realm donné",
        display_order=0,
        display_category="Group",
        example_pattern="group/",
        pattern="^group/$",
        parameters={
            "realm": {
                "description": "Tenant Keycloak/Collectivité",
                "example_value": "imio",
            }
        }
    )
    def get_groups(self, request, realm):
        url = f"{self.url}admin/realms/{realm}/groups"  # Url et endpoint à contacter
        token = self.access_token(request)["access_token"]
        headers = {"Authorization": "Bearer " + token}
        r = requests.get(url=url, headers=headers)
        return {"data": r.json()}

    @endpoint( #Méthode à revoir, ticket EO envoyé
        methods=["delete"],
        name="delete-user",
        perm='can_access',
        description="Supprimer un utilisateur d'un realm",
        long_description="Supprimer un utilisateur d'un realm",
        display_order=8,
        display_category="User",
        parameters={
            "realm": {
                "description": "Tenant Keycloak/Collectivité",
                "example_value": "imio",
            },
            "user_id": {
                "description": "GUID de l'utilisateur",
                "example_value": "c034662e-56a4-4dec-8ebd-ecf2bb75d3e7",
            }
        }
    )
    def delete_user(self, request, realm, user_id):
        url = f"{self.url}admin/realms/{realm}/users/{user_id}"  # Url et endpoint à contacter
        token = self.access_token(request)["access_token"]
        headers = {
            "Authorization": "Bearer " + token        
            }
        r = requests.delete(url=url, headers=headers)
        r.raise_for_status()


    @endpoint(
        methods=["post"],
        name="create-idp-link",
        perm='can_access',
        description="Créer un lien d'identité pour un utilisateur",
        long_description="Créer un lien d'identité pour un utilisateur",
        display_order=1,
        display_category="IDP",
        parameters={
            "realm": {
                "description": "Tenant Keycloak/Collectivité",
                "example_value": "central",
            },
            "user_id": {
                "description": "GUID de l'utilisateur",
                "example_value": "4d49f2eb-890d-47e9-8cb4-3910fc17b66b",
            },
            "provider_id": {
                "description": "ID du fournisseur",
                "example_value": "imio",
            }
        }
    )

    def create_idp_link(self, request, realm, user_id, provider_id):
        """
            "identityProvider": "imio",
            "userId": "4d49f2eb-890d-47e9-8cb4-3910fc17b66b",
            "userName": "drstranger@marvel.com"
        """
        url = f"{self.url}admin/realms/{realm}/users/{user_id}/federated-identity/{provider_id}"
        token = self.access_token(request)["access_token"]
        headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
            }
        r = requests.post(url=url, headers=headers, data=request.body)

    @endpoint(
        methods=["get"],
        name="get-idp-link",
        perm='can_access',
        description="Récupérer la liste de liens d'identités pour un utilisateur",
        long_description="Récupérer la liste de liens d'identités pour un utilisateur",
        display_order=1,
        display_category="IDP",
        parameters={
            "realm": {
                "description": "Tenant Keycloak/Collectivité",
                "example_value": "central",
            },
            "user_id": {
                "description": "GUID de l'utilisateur",
                "example_value": "97cf8f01-fa69-4143-9836-b69765d8d5d3",
            }
        }
    )

    def read_idp_links(self, request, realm, user_id):
        url = f"{self.url}admin/realms/{realm}/users/{user_id}/federated-identity"
        token = self.access_token(request)["access_token"]
        headers = {"Authorization": "Bearer " + token}
        r = requests.get(url=url, headers=headers)
        return {"data": r.json()}

    @endpoint(
        methods=["get"],
        name="delete-idp-link",
        perm='can_access',
        description="Supprime un lien d'identité pour un utilisateur",
        long_description="Supprime un lien d'identité pour un utilisateur",
        display_order=2,
        display_category="IDP",
        parameters={
            "realm": {
                "description": "Tenant Keycloak/Collectivité",
                "example_value": "central",
            },
            "user_id": {
                "description": "GUID de l'utilisateur",
                "example_value": "dfe2571a-0d55-4e86-85a4-a708a356e1c8",
            },
            "provider_id": {
                "description": "ID du fournisseur",
                "example_value": "pltest1",
            }
        }
    )

    def delete_idp_link(self, request, realm, user_id, provider_id):
        url = f"{self.url}admin/realms/{realm}/users/{user_id}/federated-identity/{provider_id}"
        token = self.access_token(request)["access_token"]
        headers = {"Authorization": "Bearer " + token}
        r = requests.delete(url=url, headers=headers)
        r.raise_for_status()

    @endpoint(
        methods=["post"], # Fonctionne avec get (IT) mais on test ça côté TS avec un post
        name="add-user-group",
        perm='can_access',
        description="Ajouter un utilisateur dans un groupe",
        long_description="Ajouter un utilisateur dans un groupe",
        display_order=9,
        display_category="User",
        parameters={
            "realm": {
                "description": "Tenant Keycloak/Collectivité",
                "example_value": "imio",
            },
            "user_id": {
                "description": "GUID de l'utilisateur",
                "example_value": "8c733129-bdbb-4268-a54e-6de65512cede",
            },
            "group_id": {
                "description": "GUID du groupe",
                "example_value": "ab220bdb-a4b7-4090-b631-0c6abea09293",
            }
        }
    )
    def add_user_group(self, request, realm, user_id, group_id):
        url = f"{self.url}admin/realms/{realm}/users/{user_id}/groups/{group_id}"  # Url et endpoint à contacter
        token = self.access_token(request)["access_token"]
        headers = {"Authorization": "Bearer " + token}
        r = requests.put(url=url, headers=headers)
        r.raise_for_status()

    @endpoint(
        methods=["get"], 
        name="delete-user-group",
        perm='can_access',
        description="Supprimer l'utilisateur d'un groupe",
        long_description="Supprimer l'utilisateur d'un groupe",
        display_order=10,
        display_category="User",
        parameters={
            "realm": {
                "description": "Tenant Keycloak/Collectivité",
                "example_value": "imio",
            },
            "user_id": {
                "description": "GUID de l'utilisateur",
                "example_value": "8c733129-bdbb-4268-a54e-6de65512cede",
            },
            "group_id": {
                "description": "GUID du groupe",
                "example_value": "ab220bdb-a4b7-4090-b631-0c6abea09293",
            }
        }
    )
    def delete_user_group(self, request, realm, user_id, group_id):
        url = f"{self.url}admin/realms/{realm}/users/{user_id}/groups/{group_id}"  # Url et endpoint à contacter
        token = self.access_token(request)["access_token"]
        headers = {"Authorization": "Bearer " + token}
        r = requests.delete(url=url, headers=headers)
        r.raise_for_status()
