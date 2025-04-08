Passerelle connector with Keycloak
==================================

Installation
------------

 - add to Passerelle installed apps settings:
   INSTALLED_APPS += ('passerelle_imio_keycloak,)

 - enable module:
   PASSERELLE_APP_PASSERELLE_IMIO_KEYCLAOK_ENABLED = True


Usage
-----

 - create and configure new connector
   - Title/description: whatever you want

 - test service by clicking on the available links
   - the /test/ endpoint to test the connection with Keycloak
   - the /read-item/ endpoint to read a new point in Keycloak
