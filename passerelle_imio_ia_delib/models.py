from builtins import str

import requests
from django.db import models
from django.http import Http404
from django.http import HttpResponse
from django.urls import reverse
from passerelle.base.models import BaseResource
from passerelle.compat import json_loads
from passerelle.utils.api import endpoint
from passerelle.utils.jsonresponse import APIError
from requests.exceptions import ConnectionError


class IADelibConnector(BaseResource):
    """
    Connecteur iA.Delib
    """
    url = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="URL",
        help_text="URL de l'application iA.Delib",
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
    api_description = "Connecteur permettant d'intéragir avec une instance d'iA.Delib"
    category = "Connecteurs iMio"

    class Meta:
        verbose_name = "Connecteur iA.Delib"

    @property
    def session(self):
        session = requests.Session()
        session.auth = (self.username, self.password)
        session.headers.update({"Accept": "application/json"})
        return session

    @endpoint(
        perm="can_access",
        description="Valider la connexion entre iA.Delib et Publik",
    )
    def test(self, request):
        url = self.url  # Url et endpoint à contacter
        return self.session.get(url).json()

    @endpoint(
        methods=["get"],
        name="read-item",
        description="Tester un GET sur Delib",
        parameters={
            "uid": {
                "description": "Identifiant d'un Point",
                "example_value": "bce166cfb27946b58aff9ecfa27367fc",
            },
            "config_id": {
                "description": "Identifiant de la config de l'instance iA.Delib",
                "example_value": "meeting-config-college",
            },
        },
        perm="can_access",
    )
    def read_item(self, request, uid, config_id):
        url = f"{self.url}@item"  # Url et endpoint à contacter
        params = {
            "UID": uid,
            "config_id": config_id,
        }  # UID de mon point à récupérer et configuration de l'instance iA.Delib.
        try:
            response_json = self.session.get(url, params=params).json()
        except Exception as e:
            raise APIError(
                str(e),
                http_status=405,
            )
        return response_json

    @endpoint(
        methods=["post"],
        name="create-item",
        description="Tester un POST sur Delib local",
        perm="can_access",
    )
    def create_item(self, request, post_data):
        url = f"{self.url}@item"  # Url et endpoint à contacter
        try:
            response_json = self.session.post(
                url,
                headers={"Content-Type": "application/json"},
                json=post_data,
            ).json()
        except Exception as e:
            raise APIError(
                str(e),
                http_status=405,
            )
        return response_json
