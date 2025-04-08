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

    @property
    def session(self):
        session = requests.Session()
        session.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
        return session

    @endpoint(
        methods=["post"],
        name="get_bearer_token",
        perm="can_access",
        description="Récupérer le Bearer Token",
        long_description="Récupérer le Bearer Token.",
        display_order=0,
        display_category="Test",
    )
    def test(self, request):
        url = f"{self.url}realms/master/protocol/openid-connect/token"  # Url et endpoint à contacter
        payload = f'client_id={self.client_id}&password={self.password}&grant_type=password&username={self.username}'
        header = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = requests.post(url=url, header=header, data=payload)
        access_token = r.json()["access_token"]
        return {"access_token": access_token}