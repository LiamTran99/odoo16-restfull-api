# odoo16-restfull-api
Custom module to expose CRUD APIs for all models, utilizing API key-based authentication for validation

## Getting Start
1. Add the following setting to your odoo.conf file
`server_wide_modules = web, base, rest_api_odoo`
2. Add rest_api_odoo folder to your custom-addons folder in your odoo codebase
3. Restart your odoo and install custom module rest_api_odoo
4. Create your api key 
-- Preferences (at the top right of mini navigation) -> Account Security => New Api Key
5. Go to Rest API and press new to create record and publish api for res.partner table
Model: res.partner (Contact)
Methods: publish GET, POST, PUT and DELETE 
6. Download [test-api.json](test-api.json) and add to postman
7. In environment create ACCESS_TOKEN variable with value equal to your New Api Key
8. In JSON Body of api, there are three property:
`fields` You can add some property to get from table
`values` where you can add new value (use for POST and UPDATE api)
`conditions` You can write some conditions for
9. Test api

