
from odoo.osv import fields, osv
from odoo.addons.metapack_integration.api import API
from suds.client import Client
import os
import time
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import base64
import logging
import urlparse
import httplib
logger = logging.getLogger(__name__)

from odoo.http import request
from requests_oauthlib import OAuth1Session

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def generate_quick_data(self, cr, uid, ids, context):
        clientkey = "qyprdbiuOkMz30peomhD3NhBl6Sq9e"
        clientsecret = "Dywf4nBFj5h1iDhjn7wSokgQEGvojp2RQ5NhKPhH"

        # OAuth end points for Intuit
        request_token_url = "https://oauth.intuit.com/oauth/v1/get_request_token"
        access_token_url = "https://oauth.intuit.com/oauth/v1/get_access_token"
        authorization_base_url = "https://appcenter.intuit.com/connect/begin"

        # 2. Fetch a request token
        # callback_uri is a callback endpoint on your web server
        from requests_oauthlib import OAuth1Session

        oauth = OAuth1Session(clientkey, clientsecret, callback_uri='http://localhost:8444/web?db=helpdesk_ext#id=3&view_type=form&model=stock.picking&action=349&active_id=2')
        oauth.fetch_request_token(request_token_url)

        # 3. Redirect user to your provider implementation for authorization
        # Cut and paste the authorization_url and run it in a browser
        authorization_url = oauth.authorization_url(authorization_base_url)
        print 'Please go here and authorize : ', authorization_url
        print"=======================",urlparse.urlparse(authorization_url,allow_fragments=True)
        return {
                            'type': 'ir.actions.act_url',
                            'url': authorization_url,
                            'target': 'new'
        }
        print 'Please go here and authorize : ', authorization_url
        kkkk

        # 4. Get the authorization verifier code from the callback url
        # redirect response is the complete callback_uri after you have authorized access to a company
#        redirect_response = raw_input('Paste the full redirect URL here : ')
        redirect_response = 'http://localhost:8444/?oauth_token=qyprdyT5RrH4QvBQgDKqUkjr4gb7YRLrbFyeTRREwpJKW87J&oauth_verifier=yyqa7tz&realmId=193514292321532&dataSource=QBO'
        oauth.parse_authorization_response(redirect_response)

        # 5. Fetch the access token
        # At this point, oauth session object already has the request token and request token secret
        oauth.fetch_access_token(access_token_url) 

        # Define the get and post endpoints for QuickBooks Online API v3
        getresource = 'https://sandbox-quickbooks.api.intuit.com/v3/company/193514292321532/query?query=select%20%2A%20from%20customer'

        # 6. Read a customer from a company
        r = oauth.get(getresource)

        print r.status_code

        if r.status_code==200:
            print r.content
        else:
            print "Error occured."