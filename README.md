Passerelle connector with iA.Delib
==================================

Installation
------------

 - add to Passerelle installed apps settings:
   INSTALLED_APPS += ('passerelle_imio_ia_delib',)

 - enable module:
   PASSERELLE_APP_PASSERELLE_IMIO_IA_DELIB_ENABLED = True


Usage
-----

 - create and configure new connector
   - Title/description: whatever you want

 - test service by clicking on the available links
   - the /test/ endpoint to test the connection with iA.Delib
   - the /read-item/ endpoint to read a new point in iA.Delib
