##############################################################################
#
#    TeckZilla Software Solutions and Services
#    Copyright (C) 2012-2013 TeckZilla-OpenERP Experts(<http://www.teckzilla.net>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import werkzeug
import random
from odoo import SUPERUSER_ID

from odoo.addons.website.models.website import slug
#from openerp.addons.web.controllers.main import login_redirect
import json
import binascii
from odoo import http, tools, _
from odoo.http import request
from odoo import SUPERUSER_ID
import os
from datetime import datetime
# from requests_oauthlib import OAuth2Session
from xml.dom.minidom import parse, parseString
import pytz
from dateutil.parser import parse
import logging
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
logger = logging.getLogger('quickbook')
from quickbooks import Oauth2SessionManager
from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer
from quickbooks.objects.vendor import Vendor
from quickbooks.objects.item import Item
from quickbooks.objects.account import Account
from quickbooks.objects.invoice import Invoice
from quickbooks.objects.term import Term
from quickbooks.objects.taxrate import TaxRate
global session_manager
import requests
from quickbooks.cdc import change_data_capture
import urllib2
import base64
import json

oauth = ''
test = ''
class customer_sign_up(http.Controller):

    def connect(self):
        clientkey = ''
        clientsecret = ''
        reconfig_idsquest_token_url = ''
        access_token_url = ''
        authorization_base_url = ''
        callbck_url = request.env['ir.config_parameter'].get_param('web.base.url')
        logger.error('callbck_url==============////////////%s',callbck_url)
        url = callbck_url+'/page/quick_book'
        quick_config_obj = request.env['quick.configuration']
        config_ids = quick_config_obj.search([])
        clientkey = config_ids.clientkey
        clientsecret = config_ids.clientsecret
        session_manager = Oauth2SessionManager(
            client_id=clientkey,
            client_secret=clientsecret,
            base_url=url,
        )
        logger.error('session_manager==============////////////%s', session_manager)
        callback_url = url
        authorize_url = session_manager.get_authorize_url(callback_url)
        logger.error('authorize_url==============////////////%s', authorize_url)
        return [authorize_url,session_manager]




    @http.route('/page/quick_book', auth='public', type='http', website=True)
    def quick_book_page(self, **kwargs):
        global cust_date_n
        logger.error('inside the quickbook ==============////////////%s')
        quick_config_obj = request.env['quick.configuration']
        config_ids = quick_config_obj.search([])
        quick_obj = request.env['quick.quick']
        quick_ids = quick_obj.search([])
        url = request.httprequest.url

        if url.find('code') >= 0:
            url_new = request.httprequest.args
            url_new_2 = request.httprequest.args.getlist('state')
            data = base64.b64decode(url_new_2[0])
            new_data=json.loads(data)
            if new_data.get('date'):
                date=new_data.get('date')
            if new_data.get('date1'):
                date1 = new_data.get('date1')

            status=new_data.get('status')
            logger.error('inside the import customer ==============////////////%s')
            code = kwargs.get('code')
            logger.error('code==============////////////%s', code)
            realmid=kwargs.get('realmId')
            logger.error('realmid==============////////////%s', realmid)
            session_man=self.connect()
            session_manager=session_man[1]
            token=session_manager.get_access_tokens(code)
            logger.error('token==============////////////%s', token)
            acess_token=session_manager.access_token
            logger.error('acess_token==============////////////%s', acess_token)
            session_manager_new = Oauth2SessionManager(
                client_id=realmid,
                client_secret=config_ids.clientsecret,
                access_token=acess_token,
            )
            if not config_ids.production:
                client = QuickBooks(
                    sandbox=True,
                    session_manager=session_manager_new,
                    company_id=realmid
                )
            else:
                client = QuickBooks(

                    session_manager=session_manager_new,
                    company_id=realmid
                )
            logger.error('client==============////////////%s', client)
            print ("client................",client)
            logger.error('test==============////////////%s', test)
            if status=='Customer':
                print ("customer.............................")
                logger.error('cust==============////////////%s')
                payment_term = self.get_payment_term(client)
                logger.error('cust==============////////////%s')
                date_cust = date
                logger.error('date_cust==============////////////%s', date_cust)
                query="SELECT * FROM customer WHERE MetaData.CreateTime >='"+date_cust+"' ""STARTPOSITION 1 MAXRESULTS 1000"
                print ("query.,.................",query)
                customers = Customer.query(query,qb=client)
                print ("customers....................",customers)
                logger.error('customers==============////////////%s', customers)
                customer = self.get_customer_record(customers)

            if status=='Vendor':
                print ("vendor./............")
                date_sup = date
                query = "SELECT * FROM vendor WHERE MetaData.CreateTime >='" + date_sup + "'STARTPOSITION 1 MAXRESULTS 1000"
                vendors = Vendor.query(query, qb=client)
                print ("Vendors....................",vendors)
                self.vendor_record(vendors)
            if status=='Accounts':
                print ("accounts,,,,,,,,,,,,,,,,,,,,,,,")
                logger.error('accounts...............==============////////////%s')
                query = "SELECT * FROM account STARTPOSITION 1 MAXRESULTS 1000"
                accounts = Account.query(query, qb=client)
                chart_account=self.chart_of_account(accounts)

            if status == 'Item':
                date_item = date
                print ("date_item.................",date_item)
                query = "SELECT * FROM item WHERE MetaData.CreateTime>='" + date_item + "' STARTPOSITION 1 MAXRESULTS 1000"
                print ("query..............//////////",query)
                items = Item.query(query, qb=client)
                self.product_product(items)

            if status=='Invoice':
                from_dt_new = date
                to_dt_new=date1
                account_obj= request.env['account.account']
                invoice_obj=request.env['account.invoice']
                # print"from_dt_new======>",from_dt_new,to_dt_new
                # payment_term = self.get_payment_term(client)
                # tax_rate=self.tax(client)
                query="SELECT * FROM Invoice WHERE MetaData.CreateTime >= '" + from_dt_new + "' AND MetaData.CreateTime <= '" + to_dt_new + "' STARTPOSITION 1 MAXRESULTS 1000"
                print ("query....................",query)
                invoices=Invoice.query(query, qb=client)
                self.customer_invoice(invoices)

            if test == 'purchase':
                print"from_dt",from_dt
                print"to_dt",to_dt
                from_dt_po = from_dt.replace(':','%3A')
                to_dt_po = to_dt.replace(':','%3A')
                getresource = config_ids.url +config_ids.company+'/query?query=select%20%2A%20from%20purchaseorder%20where%20MetaData.CreateTime%20%3E%3D%20%27'+from_dt_po+'%27%20and%20%20MetaData.CreateTime%20%3C%3D%20%27'+to_dt_po+'%27%20%20MAXRESULTS%201000'
                r = oauth.get(getresource)
                if r.status_code==200:
                    data = r.content
                    responseDOM = parseString(data)
                    tag = responseDOM.getElementsByTagName('PurchaseOrder')
                    self.get_purchase(tag)
                else:
                    print "Error occurred."

            if test == 'sale':
                from_dt_so = from_dt.replace(':','%3A')
                to_dt_so = to_dt.replace(':','%3A')
                getresource = config_ids.url +config_ids.company+'/query?query=select%20%2A%20from%20salesreceipt%20where%20MetaData.CreateTime%20%3E%3D%20%27'+from_dt_so+'%27%20and%20%20MetaData.CreateTime%20%3C%3D%20%27'+to_dt_so+'%27%20%20MAXRESULTS%201000'
                r = oauth.get(getresource)
                if r.status_code==200:
                    data = r.content
                    responseDOM = parseString(data)
                    tag = responseDOM.getElementsByTagName('SalesReceipt')
                    self.get_sale(tag)
                else:
                    print "Error occured."
            if test == 'export_cust':
                self.export_customer(realmid=realmid,acess_token=acess_token)

            if test == 'export_vendor':
                self.export_vendor(realmid=realmid,access_token=acess_token)
            if test == 'export_items':
                query = "SELECT * FROM account STARTPOSITION 1 MAXRESULTS 1000"
                accounts = Account.query(query, qb=client)
                self.export_items(realmid=realmid,access_token=acess_token,accounts=accounts)

            if test == 'export_invoice':
                self.export_invoice(from_dt,to_dt,realmid=realmid,access_token=acess_token)

            if test == 'export_purchase':
                self.export_purchase(from_dt_pr,to_dt_pr)

            if test == 'export_sale':
                self.export_sale(from_dt_sr,to_dt_sr)


        values = {
            'quick':quick_ids,
        }
        return request.render("quickbooks_connector_v10.quick_book_page", values)



    @http.route('/page/add_quick_b_data', auth='public', type='http', website=True, csrf = False)
    def add_quick_b_data(self, **post):

        last_date = parse(post['last_dt_co'])
        tz = pytz.timezone("America/Toronto")
        aware_dt = tz.localize(last_date)
        cust_date = aware_dt.isoformat()
        logger.error('++++cust_date+++++++++++++ %s',cust_date)
        global oauth 
        quick_config_obj = request.env['quick.configuration']
        config_ids = quick_config_obj.search([])
        print "=============config_ids======================",config_ids
        quick_obj = request.env['quick.quick']
        cquick_ids = quick_obj.search([])
        date_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if cquick_ids:
            cquick_id = cquick_ids.write({'lastupdate_cust' : date_time})
        else:
            uid = quick_obj.create({'lastupdate_cust' : date_time})
        # quick = Quickbook()
        url = self.connect()

        logger.error('++++url++++++url+++++++ %s',url)
        authorize_url=url[0]

        # state_param = '?state=' + 'customer'
        # print ("state_param................0",state_param)
        # authorize_url += state_param
        logger.error('++++authorize_url++++++authorize_url+++++++ %s', authorize_url)
        print("authorize_url...............", authorize_url)
        state_dict = {
            'date':cust_date ,
            'status': "Customer",
        }
        state_json = json.dumps(state_dict)
        encoded_params = base64.urlsafe_b64encode(state_json)
        state_param = str(encoded_params)
        authorize_url = authorize_url.replace('None', state_param)

        if authorize_url:
            global test
            global cust_date_n
            test = 'cust'
            cust_date_n = cust_date
            return json.dumps({'url': authorize_url})
        else:
            return request.render("quickbooks_connector_v10.quick_book_page")

    def get_customer_record(self,customers):
        logger.error('++++get_customer_record++++++get_customer_record+++++++ %s')

        partner_obj=request.env['res.partner']
        country_obj = request.env['res.country']
        cd_list=[]
        logger.error('++++customers++++++customers+++++++ %s', len(customers))
        for customer in customers:
            name = customer.DisplayName or ''
            logger.error('++++name++++++name+++++++ %s', name)
            print("name................", name)
            activity_cutomer = customer.Active or False
            email = customer.PrimaryEmailAddr or ''
            phone = customer.PrimaryPhone or ''
            fax = customer.Fax if customer.Fax else ''
            mobile = customer.Mobile if customer.Mobile else ''
            notes = customer.Notes if all(customer.Notes) else ''
            if customer.MetaData:
                metadata=customer.MetaData
                create_time=metadata.get('CreateTime')
                last_update_time=metadata.get('LastUpdatedTime')
            else:
                create_time=''
                last_update_time=''

            account_rece_id = request.env['account.account'].search([('user_type_id', '=', 'Receivable')])
            account_pay_id = request.env['account.account'].search([('user_type_id', '=', 'Payable')])
            if customer.WebAddr:
                web_add = customer.WebAddr
                web_url = web_add.URI
            else:
                web_url = ''

            if customer.Title:
                cust_title = request.env['res.partner.title'].search([('shortcut', '=', customer.Title)])
                if cust_title:
                    title = cust_title.id
                else:
                    title_id = request.env['res.partner.title'].create(
                        {'name': customer.Title, 'shortcut': customer.Title})
                    title = title_id.id
            else:
                title = ''
            if customer.SalesTermRef:
                term_ref = customer.SalesTermRef
                payment_term_val = {'name': term_ref.name, 'quickbook_id': term_ref.value}
                term_id = request.env['account.payment.term'].search([('quickbook_id', '=', term_ref.value)])
                pay_term = term_id.id
            else:
                pay_term = False
            bll_address = customer.BillAddr
            global bll_address
            if customer.BillAddr:
                bill_address = customer.BillAddr
                b_city = bill_address.City
                # b_country=bill_address.Country
                b_country_code = bill_address.CountrySubDivisionCode
                b_address1 = bill_address.Line1
                b_address2 = bill_address.Line2
                b_address3 = bill_address.Line3
                b_zip = bill_address.PostalCode
                b_id = bill_address.Id
                b_notes = bill_address.Note
                b_type = 'invoice'
                x = 1
                global b_id
            else:
                fault_reason = 'There Is No Billing Address'
                b_address1 = ''
                b_address2 = ''
                b_city = ''
                b_zip = ''
                b_type = ''
                b_id = ''
                b_country_code = ''
                b_notes = ''
                x = 2
            sll_address = customer.ShipAddr
            global sll_address
            if customer.ShipAddr:
                ship_address = customer.ShipAddr
                s_city = ship_address.City
                # s_country = ship_address.Country
                s_country_code = ship_address.CountrySubDivisionCode
                s_address1 = ship_address.Line1
                s_address2 = ship_address.Line2
                s_address3 = ship_address.Line3
                s_zip = ship_address.PostalCode
                s_id = ship_address.Id
                s_type = 'delivery'
                s_notes = ship_address.Note
                global s_id
                y = 1
            else:
                s_address1 = ''
                s_address2 = ''
                s_city = ''
                s_zip = ''
                s_type = ''
                s_country_code = ''
                s_id = ''
                s_notes = ''
                fault_reason = 'There Is No Shipping Address'
                y = 2
            if x == 1:
                country_ids_b = country_obj.search([('code', '=', b_country_code)])
                if country_ids_b:
                    country_id_b = country_ids_b.id
                else:
                    country_id_b = False
            if y == 1:
                country_ids_s = country_obj.search([('code', '=', s_country_code)])
                if country_ids_s:
                    country_id_s = country_ids_s.id
                else:
                    country_id_s = False
            else:
                pass
            quick_id = customer.Id
            bill_add_val = {
                'street': b_address1,
                'street2': b_address2,
                'city': b_city,
                'zip': b_zip,
                'type': b_type,
                'name': b_id,
                # 'country_id':country_id_b,
                'comment': b_notes

            }
            global bill_add_val
            shipp_add_val = {
                'street': s_address1,
                'street2': s_address2,
                'city': s_city,
                'zip': s_zip,
                'type': s_type,
                'name': s_id,
                # 'country_id':country_id_s,
                'comment': s_notes
            }
            global shipp_add_val

            customer_val = {
                'name': name,
                'company_type': 'person',
                # 'street':b_address1,
                # 'street2':b_address2,
                'property_account_receivable_id': account_rece_id.id,
                'property_account_payable_id': account_pay_id.id,
                # 'city':b_city,
                # 'zip':b_zip,
                'email': email,
                'quick_id': quick_id,
                'title': title,
                'mobile': mobile,
                'phone': phone,
                'customer': True,
                # 'country_id':country_id_b,
                'fax': fax,
                'comment': notes,
                'create_time':create_time,
                'last_update_time':last_update_time,
                'property_payment_term_id': pay_term,
                'website': web_url,

            }
            print("customer_val.,............", customer_val)
            # partner_ids = partner_obj.search([('email','=',email),('name','=',name),('customer','=',True)])
            partner_ids = partner_obj.search([('quick_id', '=', quick_id), ('customer', '=', True)])
            if not partner_ids:
                if customer.ParentRef:
                    parent = customer.ParentRef
                    parent_partner_id = request.env['res.partner'].search([('quick_id', '=', parent.value)])
                    if not parent_partner_id:
                        fault_reason = 'please import customer properly'
                        # p_p_id = request.env['res.partner'].create(
                        #     {'name', '=', parent.name, 'quick_id', '=', parent.value})
                        # p_p_id=p_p_id.id
                        customer_val.update({'faulty_reason': fault_reason})
                        pass
                    else:
                        p_p_id = parent_partner_id.id
                        customer_val.update({'parent_id': p_p_id})
                if (x == 1 and y == 1):
                    customer_val.update({'child_ids': [(0, 0, bill_add_val), (0, 0, shipp_add_val)]})
                if (x == 1 and y == 2):
                    customer_val.update({'child_ids': [(0, 0, bill_add_val)]})
                if (y == 1 and x == 2):
                    customer_val.update({'child_ids': [(0, 0, shipp_add_val)]})
                if (x == 2 and y == 2):
                    pass
                partner_id = partner_obj.create(customer_val)
                logger.error('++++partner_id++++++partner_id+++++++ %s', partner_id)
            else:
                print("customer_val,,,vvvvvvvvvvvv,,,,,,,,,,,,,,,", customer_val)
                partner_ids.update(customer_val)
                if b_id:
                    billing_id = partner_obj.search([('name', '=', b_id)])
                    if billing_id:
                        billing_id.update(bill_add_val)
                    else:
                        customer_val.update({'child_ids': [(0, 0, bill_add_val)]})
                        partner_ids.write(customer_val)
                if s_id:
                    shipping_id = partner_obj.search([('name', '=', s_id)])
                    if shipping_id:
                        shipping_id.update(shipp_add_val)
                    else:
                        customer_val.update({'child_ids': [(0, 0, shipp_add_val)]})
                        partner_ids.write(customer_val)

    def vendor_record(self,vendors):
        partner_obj=request.env['res.partner']
        country_obj=request.env['res.country']
        vd_list = []
        for vendor in vendors:
            print("vendor................................", vendor)
            vd_list.append(vendor)
            name = vendor or ''
            print("name................", name)
            email = vendor.PrimaryEmailAddr or ''
            phone = vendor.PrimaryPhone or ''
            vendor_activity = vendor.Active or False
            if vendor.Fax:
                fax = vendor.Fax
                fax = fax.FreeFormNumber
            else:
                fax = ''

            mobile = vendor.Mobile if vendor.Mobile else ''
            # notes = vendor.Notes if vendor.Notes else ''
            account_rece_id = request.env['account.account'].search([('user_type_id', '=', 'Receivable')])
            account_pay_id = request.env['account.account'].search([('user_type_id', '=', 'Payable')])
            if vendor.WebAddr:
                web_add = vendor.WebAddr
                web_url = web_add.URI
            else:
                web_url = ''
            if vendor.TermRef:
                term = vendor.TermRef
                id = term.value
                term_id = request.env['account.payment.term'].search([('quickbook_id', '=', id)])
                if term_id:
                    term_id = term_id
                else:
                    term_id = request.env['account.payment.term'].create(
                        {'name': term.name, 'quickbook_id': term.value})

            else:
                pass
            # if vendor.Title:
            #     cust_title = request.env['res.partner.title'].search([('shortcut', '=', vendor.Title)])
            #     if cust_title:
            #         title = cust_title.id
            #     else:
            #         title_id = request.env['res.partner.title'].create({'name': vendor.Title})
            #         title = title_id.id
            # else:
            #     title = ''
            bll_address = vendor.BillAddr
            global bll_address
            if vendor.BillAddr:
                bill_address = vendor.BillAddr
                b_city = bill_address.City
                # b_country=bill_address.Country
                b_country_code = bill_address.CountrySubDivisionCode
                b_address1 = bill_address.Line1
                b_address2 = bill_address.Line2
                b_address3 = bill_address.Line3
                b_zip = bill_address.PostalCode
                b_id = bill_address.Id
                b_type = 'invoice'
                global b_id
                x = 1
            else:

                b_address1 = ''
                b_address2 = ''
                b_city = ''
                b_zip = ''
                b_type = ''
                b_id = ''
                b_country_code=''

                x = 2
            country_ids_b = country_obj.search([('code', '=', b_country_code)])
            if country_ids_b:
                country_id_b = country_ids_b.id
            else:
                country_id_b = False
            quick_id = vendor.Id
            bill_add_val = {
                'street': b_address1,
                'street2': b_address2,
                'city': b_city,
                'zip': b_zip,
                'type': b_type,
                'name': b_id,
                # 'country_id': country_id_b
            }
            global bill_add_val

            vendor_val = {
                'name': name,
                'company_type': 'company',
                # 'street': b_address1,
                # 'street2': b_address2,
                'city': b_city,
                'zip': b_zip,
                'email': email,
                'quick_id': quick_id,
                # 'title': title,
                'mobile': mobile,
                # 'country_id': country_id_b,
                'fax': fax,
                # 'comment':notes,
                'supplier': True,
                'customer': False,
                'website': web_url,
                'property_account_receivable_id': account_rece_id,
                'property_account_payable_id': account_pay_id

            }
            # partner_ids = partner_obj.search([('email','=',email),('name','=',name),('supplier','=',True)])
            partner_ids = partner_obj.search([('quick_id', '=', quick_id), ('supplier', '=', True)])
            if not partner_ids:
                if x == 1:
                    vendor_val.update({'child_ids': [(0, 0, bill_add_val)]})
                if x == 2:
                    pass
                partner_id = partner_obj.create(vendor_val)
            else:
                partner_ids.write(vendor_val)
                if b_id:
                    billing_id = partner_obj.search([('name', '=', b_id)])
                    if billing_id:
                        billing_id.update(bill_add_val)

                    else:
                        vendor_val.update({'child_ids': [(0, 0, bill_add_val)]})
                        partner_ids.write(vendor_val)


    def chart_of_account(self,accounts):
        logger.error('chart of account==============////////////%s')
        account_obj=request.env['account.account']
        lis=[]
        logger.error('accounts==============////////////%s', len(accounts))
        for account in accounts:
            logger.error('account==============////////////%s', account)
            print("account,,,,,,,,,,,,", account)
            acc_type = account.AccountType
            logger.error('account==============////////////%s', acc_type)
            id = account.Id
            logger.error('id==============////////////%s', id)
            Name = account.Name
            logger.error('Name==============////////////%s', Name)
            lis.append(acc_type)
            if acc_type == 'Accounts Payable':
                type = 'Payable'
                reconcile = True
            if acc_type == 'Bank':
                type = 'Bank and Cash'
                reconcile = False
            if acc_type == 'Accounts Receivable':
                type = 'Receivable'
                reconcile = True
            if acc_type == 'Other Current Asset':
                type = 'Current Assets'
                reconcile = True
            if acc_type == 'Fixed Asset':
                type = 'Current Assets'
                reconcile = True
            if acc_type == 'Credit Card':
                type = 'Credit Card'
                reconcile = False
            if acc_type == 'Other Current Liability':
                type = 'Current Liabilities'
                reconcile = True
            if acc_type == 'Long Term Liability':
                type = 'Current Liabilities'
                reconcile = True
            if acc_type == 'Equity':
                type = 'Equity'
                reconcile = False
            if acc_type == 'Income':
                type = 'Income'
                reconcile = False
            if acc_type == 'Cost of Goods Sold':
                type = 'Current Liabilities'
                reconcile = True
            if acc_type == 'Expense':
                type = 'Expenses'
                reconcile = False
            if acc_type == 'Other Income':
                type = 'Other Income'
                reconcile = False
            if acc_type == 'Other Expense':
                type = 'Expenses'
                reconcile = False

            acc_type_id = request.env['account.account.type'].search([('name', '=', type)])
            if acc_type_id:
                acc_val = {
                    'name': Name,
                    'user_type_id': acc_type_id.id,
                    'quickbook_chart_id': id,
                    'reconcile': reconcile
                }
            else:
                acc_val = {}
            acc_id = request.env['account.account'].search([('quickbook_chart_id', '=', id)])
            if not acc_id:
                account_id = account_obj.create(acc_val)
            else:
                acc_id.write(acc_val)


    def product_product(self,items):
        for item in items:
            print("item..............", item)
            product_val = {}
            if item.AssetAccountRef:
                income_account = item.AssetAccountRef
                account_id = request.env['account.account'].search([('quickbook_chart_id', '=', income_account.value)])
                if account_id:
                    account_income = account_id.id
                    product_val.update({'property_account_income_id': account_income})
            else:
                pass

            if item.ExpenseAccountRef:
                expense_account = item.ExpenseAccountRef
                account_id = request.env['account.account'].search(
                    [('quickbook_chart_id', '=', expense_account.value)])
                if account_id:
                    product_val.update({'property_account_expense_id': account_id})
            else:
                pass
            if item.ParentRef:
                category_parent = item.ParentRef
                category_obj = request.env['product.category']
                categ_val = {
                    'name': category_parent.name,
                    'quickbook_id': category_parent.value,
                    'property_valuation': 'manual_periodic'
                }
                categ_id = category_obj.search([('quickbook_id', '=', category_parent.value)])
                if not categ_id:
                    categ_id = category_obj.create(categ_val)
                else:
                    categ_id.write(categ_val)
                product_val.update({'categ_id': categ_id.id})

            desc = item.Description
            id = item.Id
            name = item.Name
            sku = item.Sku
            type = item.Type
            purchase_desc = item.PurchaseDesc
            qty_on_hand = item.QtyOnHand
            logger.error('++++qty_on_hand++++++qty_on_hand+++++++ %s',qty_on_hand)
            logger.error('++++qty_on_hand++++++qty_on_hand+++++++ %s', str(qty_on_hand))
            qty_on_hand_1=str(qty_on_hand)
            if '-' in qty_on_hand_1:
                qty_on_hand=0
            else:
                qty_on_hand=qty_on_hand
            p_type = ''
            if type == 'Service':
                p_type = 'service'
            elif type == 'Inventory':
                p_type = 'product'

            sale_price = item.UnitPrice
            description_sale = item.Description
            purchase_cost = item.PurchaseCost
            purchase_desc = item.PurchaseDesc

            product_val.update({
                'name': name,
                'type': p_type,
                'default_code': sku,
                'list_price': sale_price,
                'quick_prod_id': id,
                'description_sale': description_sale,
                'description_purchase': purchase_desc,
                # 'categ_id':1,
                'standard_price': purchase_cost,
                # 'new_quantity':qty_on_hand
            })

            # parent_ref=item.ParentRef
            # # categ_name=parent_ref.name
            # # categ_id=parent_ref.value

            # # if item.parent_ref:
            # #     parent_ref=item.ParentRef
            # #     category_name=parent_ref.name
            # #
            # # else:
            # #    pass

            product_tmp_id = request.env['product.template'].search([('quick_prod_id', '=', id)])
            if not product_tmp_id:
                tem_id = request.env['product.template'].create(product_val)
                product_product_id = request.env['product.product'].search([('product_tmpl_id', '=', tem_id.id)])
                product_product_id.quick_prod_id = tem_id.quick_prod_id
                if product_val.get('type') == 'product':
                    # location_id = request.env['stock.location'].search(
                    #     [('name', '=', 'WH'), ('usage', '=', 'view')])
                    # stock_loc_id = request.env['stock.location'].search([('location_id', '=', location_id.id)])

                    lot_id = request.env['stock.production.lot'].search([('product_id','=',product_product_id.id)])
                    if not lot_id:
                        lot_id = request.env['stock.production.lot'].create({'product_id':product_product_id.id})
                    stock_val = {
                        'lot_id': lot_id.id,
                        'new_quantity': qty_on_hand,
                        'product_id': product_product_id.id,

                    }
                    stock_product_change_id = request.env['stock.change.product.qty'].create(stock_val)
                    stock_product_change_id.change_product_qty()
                else:
                    pass
            else:
                product_tmp_id.write(product_val)

    def get_payment_term(self, client):
        logger.error('get_payment_term==============////////////%s')
        query = "SELECT * FROM term"
        p_terms = Term.query(query, qb=client)
        logger.error('p_terms==============////////////%s',p_terms)
        print("p_terms..................", p_terms)
        term_id=[]
        for term in p_terms:
            term_id.append(term.Name)
            print("term,,,,,,,,,,,,,,", term)
            line_ids = {
                'value': 'balance',
                'option': 'day_after_invoice_date',
                'days': term.DueDays,
            }
            term_val = {
                'name': term.Name,
                'active': True,
                'quickbook_id': term.Id,
                # 'line_ids':line_ids
            }

            payment_term_id = request.env['account.payment.term'].search([('quickbook_id', '=', term.Id)])
            logger.error('payment_term_id==============////////////%s', payment_term_id)
            if not payment_term_id:
                term_val.update({'line_ids': [(0, 0, line_ids)]})
                request.env['account.payment.term'].create(term_val)
            else:
                payment_term_id.write(term_val)

    def tax(self,client):
        query = "SELECT * FROM taxrate"
        tax_response = TaxRate.query(query, qb=client)
        for tax in tax_response:
            print("tax............", tax)
            quick_id = tax.Id
            name = tax.Name
            rate = tax.RateValue
            tax_vals_data = {
                'name': name,
                'type_tax_use': 'sale',
                'amount_type': 'percent',
                'amount': rate,
                'tax_group_id': 1
            }
            tax_id = request.env['account.tax'].search([('quick_id', '=', quick_id)])
            if not tax_id:
                tax_n_id = request.env['account.tax'].create(tax_vals_data)
            else:
                tax_id.write(tax_vals_data)

    def customer_invoice(self,invoices):
        invoice_obj = request.env['account.invoice']
        for invoice in invoices:
            print("invoice,,,,,,,,,,,,,,,,,,", invoice)
            customer_ref = invoice.CustomerRef
            if customer_ref:
                name = customer_ref.name
                logger.error('++++name+++++++++++++ %s',name)
            else:
                name=''
            customer_quickbook_id = customer_ref.value or False
            logger.error('++++customer_quickbook_id+++++++++++++ %s', customer_quickbook_id)
            email = invoice.BillEmail
            if email:
                email_address = email.Address or ''
                logger.error('++++email_address+++++++++++++ %s', email_address)
            else:
                email_address=''
            invoice_date = invoice.TxnDate or ''
            # if invoice.TxnTaxDetail:
            #     tax_detail = invoice.TxnTaxDetail
            #     tax_code = tax_detail.TxnTaxCodeRef
            #     print("tax_code/////////////////", tax_code)
            #     if tax_code is None:
            #         pass
            #     else:
            #         # tax_vals = {
            #         #     'name': tax_code.name,
            #         #     'type_tax_use': 'sale',
            #         #     'amount_type': 'percent',
            #         #     'amount': 0.0000,
            #         #     'tax_group_id': 1
            #         # }
            #         if tax_code.value:
            #             tax_quickbook_id = tax_code.value
            #             tax = invoice.TxnTaxDetail
            #             tax_n_id = request.env['account.tax'].search([('quick_id', '=', tax_quickbook_id)])
            #             # tax_id.write(tax_vals)
            #             # tax_n_id = tax_id.id
            #
            # total_tax = tax.TotalTax or False
            due_date = invoice.DueDate or ''
            logger.error('++++due_date+++++++++++++ %s', due_date)
            invoice_line = invoice.Line
            logger.error('++++invoice_line+++++++++++++ %s', invoice_line)
            description_invoice = invoice.CustomerMemo or ''
            logger.error('++++description_invoice+++++++++++++ %s', description_invoice)
            invoice_no = invoice.DocNumber or ''
            logger.error('++++invoice_no+++++++++++++ %s', invoice_no)
            quickbook_invoice_id = invoice.Id or ''
            logger.error('++++quickbook_invoice_id+++++++++++++ %s', quickbook_invoice_id)
            line_list = []
            line_dict = {}
            # payment_term = invoice.SalesTermRef
            # term_quickbook_id = payment_term.value

            if invoice.BillAddr:
                logger.error('++++invoice.BillAddr+++++++++++++ %s', invoice.BillAddr)
                bill_address = invoice.BillAddr
                b_city = bill_address.City
                # b_country=bill_address.Country
                b_country_code = bill_address.CountrySubDivisionCode
                b_address1 = bill_address.Line1
                b_address2 = bill_address.Line2
                b_address3 = bill_address.Line3
                b_zip = bill_address.PostalCode
                b_id = bill_address.Id
                b_notes = bill_address.Note
                b_type = 'invoice'
                x = 1
                global b_id
            else:
                b_address1 = ''
                b_address2 = ''
                b_city = ''
                b_zip = ''
                b_type = ''
                b_id = ''
                b_country_code = ''
                b_notes = ''
                x = 2
            sll_address = invoice.ShipAddr
            global sll_address
            if invoice.ShipAddr:
                ship_address = invoice.ShipAddr
                s_city = ship_address.City
                # s_country = ship_address.Country
                s_country_code = ship_address.CountrySubDivisionCode
                s_address1 = ship_address.Line1
                s_address2 = ship_address.Line2
                s_address3 = ship_address.Line3
                s_zip = ship_address.PostalCode
                s_id = ship_address.Id
                s_type = 'delivery'
                s_notes = ship_address.Note
                global s_id
                y = 1
            else:
                s_address1 = ''
                s_address2 = ''
                s_city = ''
                s_zip = ''
                s_type = ''
                s_country_code = ''
                s_id = ''
                s_notes = ''
                y = 2

            bill_add_val = {
                'street': b_address1,
                'street2': b_address2,
                'city': b_city,
                'zip': b_zip,
                'type': b_type,
                'name': b_id,
                # 'country_id':country_id_b,
                'comment': b_notes

            }

            shipp_add_val = {
                'street': s_address1,
                'street2': s_address2,
                'city': s_city,
                'zip': s_zip,
                'type': s_type,
                'name': s_id,
                # 'country_id':country_id_s,
                'comment': s_notes
            }

            customer_val = {
                'name': name,
                'quick_id': customer_quickbook_id,
                'property_account_receivable_id': 1,
                'property_account_payable_id': 2
            }

            for line in invoice_line:
                print("each,,,,,,,,,,,,,", line)
                logger.error('++++line+++++++++++++ %s', line)
                value = str(line)
                logger.error('++++value+++++++++++++ %s', value)
                if 'None' in value:
                    logger.error('++++value+++++++++++++ %s')
                    pass
                else:
                    logger.error('++++else+++++++++++++ %s')
                    amount = line.Amount or False
                    description = line.Description or ''
                    if line.SalesItemLineDetail:
                        sales_item_line = line.SalesItemLineDetail
                        tax_boolean = sales_item_line.TaxCodeRef
                        tax_val = tax_boolean.value
                        # if (tax_val == 'TAX' and tax_n_id):
                        #     tax_id = tax_n_id
                        # else:
                        #     tax_id=''
                        item_ref = sales_item_line.ItemRef
                        produ_name = item_ref.name or ''
                        product_id = item_ref.value or False
                        qty = sales_item_line.Qty or False
                        rate = sales_item_line.UnitPrice or False
                        quickbook_id = line.Id or False
                        # account_id = request.env['account.account'].browse(140)
                        product_vals = {
                            'name': produ_name,
                            'quick_prod_id': product_id,
                        }
                        product_id = request.env['product.product'].search([('quick_prod_id', '=', product_id)])
                        if not product_id:
                            product_id = request.env['product.product'].create(product_vals)
                            prod_id = product_id.id
                        else:
                            product_id.write(product_vals)
                            prod_id = product_id.id
                        acc_id = accounts = product.product_tmpl_id.get_product_accounts(fpos)
                        line_dict = {
                            'product_id':prod_id,
                            'name': description,
                            'account_id': product_id.property_account_income_id.id,
                            'quantity': qty,
                            'price_unit': rate,

                            # 'invoice_line_tax_ids': [(6, 0, [tax_id])]
                        }

                        invoice_line_id = request.env['account.invoice.line'].create(line_dict)
                        line_list.append(invoice_line_id.id)

            print("line_list...............", line_list)
            journal_browse_id = request.env['account.journal'].browse(1)
            partner_id = request.env['res.partner'].search([('quick_id', '=', customer_quickbook_id)])
            if partner_id:
                part_id = partner_id.id
            if not partner_id:
                if (x == 1 and y == 1):
                    customer_val.update({'child_ids': [(0, 0, bill_add_val), (0, 0, shipp_add_val)]})
                if (x == 1 and y == 2):
                    customer_val.update({'child_ids': [(0, 0, bill_add_val)]})
                if (y == 1 and x == 2):
                    customer_val.update({'child_ids': [(0, 0, shipp_add_val)]})
                if (x == 2 and y == 2):
                    pass
                partner_id = request.env['res.partner'].create(customer_val)
                part_id = partner_id.id
            account_id = request.env['account.account'].search([('user_type_id', '=', 'Receivable')])
            # account_payment_term_id = request.env['account.payment.term'].search(
            #     [('quickbook_id', '=', term_quickbook_id)])
            # if account_payment_term_id:
            #     term_id = account_payment_term_id.id
            # else:
            #     term_id = request.env['account.payment.term'].create(
            #         {'name': payment_term.name, 'quickbook_id': payment_term.value})
            invoice_vals = {
                'partner_id': part_id,
                'quick_invoice_id': quickbook_invoice_id,
                'journal_id': journal_browse_id.id,
                'account_id': account_id.id,
                'name': invoice_no,
                # 'amount_tax': total_tax,
                'date_invoice': invoice_date,
                'state': 'draft',
                'type': 'out_invoice',
                'date_due': due_date,
                # 'payment_term_id': term_id,
                'invoice_line_ids': [(6, 0, line_list)]
            }
            print("invoice_vals///////////", invoice_vals)
            quick_inv_id = invoice_obj.search([('quick_invoice_id', '=', quickbook_invoice_id)])
            if not quick_inv_id:
                invoice_created_id = request.env['account.invoice'].create(invoice_vals)
                print("invoice_created_id...........", invoice_created_id)
                # product_id=request.env['product.product'].search([('quick_prod_id','=',product_id)])
    @http.route('/page/add_export_cust_data', auth='public', type='http', website=True , csrf = False)
    def add_export_cust_data(self, **post):
        print"post",post
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

        last_date = parse(post['last_dt_co'])
        tz = pytz.timezone("America/Toronto")
        aware_dt = tz.localize(last_date)
        cust_date = aware_dt.isoformat()
        logger.error('++++cust_date+++++++++++++ %s', cust_date)
        global oauth
        quick_config_obj = request.env['quick.configuration']
        config_ids = quick_config_obj.search([])
        quick_obj = request.env['quick.quick']
        quick_ids = quick_obj.search([])
        # config_data = quick_config_obj.browse(cr,uid,config_ids)
        date_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if quick_ids:
            quick_id = quick_ids.write( {'exportdate_cust' : date_time})
            print"quick_cust_id",quick_id
            logger.error('++++quick_id+++++++++++++ %s',quick_id)
        else:
            uid = quick_obj.create({'exportdate_cust' : date_time})
            print"=======uid=====",uid
        # data = Quickbook()
        # data = Quickbook()
        # print ("data////////////////",data)
        # oauth = data.connect()
        # print ("oauth//////////////",oauth)
        # request_token_url = config_ids.request_token_url
        # authorization_base_url = config_ids.authorization_base_url
        # token=oauth.fetch_token(request_token_url,config_ids.clientsecret,authorization_response='http://localhost:8069')
        # print ("token..............",token)

        session_manager = Oauth2SessionManager(
            client_id=config_ids.clientkey,
            client_secret=config_ids.clientsecret,
            base_url='http://localhost:8068/page/quick_book',
        )
        print ("session_manager...........", session_manager)
        callback_url = 'http://localhost:8068/page/quick_book'
        authorize_url = session_manager.get_authorize_url(callback_url)
        print ("authorize_url....dddddddd...........", authorize_url)
        # authorization_url = oauth.authorization_url(authorization_base_url)
        # print ("authorization_url............",authorization_url)
        url = request.httprequest.url
        state_dict = {
            'date': cust_date,
            'status': "Customer",
        }
        state_json = json.dumps(state_dict)
        encoded_params = base64.urlsafe_b64encode(state_json)
        state_param = str(encoded_params)
        authorize_url = authorize_url.replace('None', state_param)
        print ("url...................",url)
        if authorize_url:
            print ("id..................")
            global test
            test = 'export_cust'
            return json.dumps({'url': authorize_url})
        else:
            print ("else.,,,,,,,,,,,,,,,,,,,,")
            return request.render("quickbooks_connector_v10.quick_book_page")
        
        
        
    @http.route('/page/add_quick_b_vendor', auth='public', type='http', website=True)
    def add_quick_b_vendor(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        global oauth
        last_date = parse(post['last_dt_sup'])
        tz = pytz.timezone("America/Toronto")
        aware_dt = tz.localize(last_date)
        sup_date = aware_dt.isoformat()
        print"sup_date==========>>",sup_date
        # quick_config_obj = request.env['quick.configuration']
        #
        # config_ids = quick_config_obj.search([])
        # quick_obj = request.env['quick.quick']
        # quick_ids = quick_obj.search([])
        # # config_data = quick_config_obj.browse(cr,uid,config_ids)
        # date_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # if quick_ids:
        #     quick_sup_id = quick_ids.write({'lastupdate_sup' : date_time})
        # else:
        #     uid = quick_obj.create({'lastupdate_sup' : date_time})
        # data = Quickbook(config_ids.clientkey, config_ids.clientsecret, config_ids.request_token_url, config_ids.access_token_url, config_ids.authorization_base_url)
        # oauth = data.connect()
        # print"==========oauth=====",oauth
        # clientkey = config_ids.clientkey
        # clientsecret = config_ids.clientsecret
        # request_token_url = config_ids.request_token_url
        # access_token_url = config_ids.access_token_url
        # authorization_base_url = config_ids.authorization_base_url
        # oauth.fetch_request_token(request_token_url)
        # authorization_url = oauth.authorization_url(authorization_base_url)
        # # quick_ven=Quickbook()
        url=self.connect()
        authorize_url=url[0]
        state_dict = {
            'date': sup_date,
            'status': "Vendor",

        }
        state_json = json.dumps(state_dict)
        encoded_params = base64.urlsafe_b64encode(state_json)
        state_param = str(encoded_params)
        authorize_url = authorize_url.replace('None', state_param)
        url = request.httprequest.url
        if authorize_url:
            global test
            global sup_date_n
            test = 'vendor'
            sup_date_n = sup_date
            return json.dumps({'url': authorize_url})
        else:
            return request.website.render("quickbooks_connector_v10.quick_book_page")
        
        
    @http.route('/page/export_quick_b_vendor', auth='public', type='http', website=True)
    def export_quick_b_vendor(self, **post):

        print"post", post
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

        last_date = parse(post['last_dt_co'])
        tz = pytz.timezone("America/Toronto")
        aware_dt = tz.localize(last_date)
        cust_date = aware_dt.isoformat()
        logger.error('++++cust_date+++++++++++++ %s', cust_date)
        global oauth
        quick_config_obj = request.env['quick.configuration']
        config_ids = quick_config_obj.search([])
        quick_obj = request.env['quick.quick']
        quick_ids = quick_obj.search([])
        # config_data = quick_config_obj.browse(cr,uid,config_ids)
        date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # data = Quickbook()
        # data = Quickbook()
        # print ("data////////////////",data)
        # oauth = data.connect()
        # print ("oauth//////////////",oauth)
        # request_token_url = config_ids.request_token_url
        # authorization_base_url = config_ids.authorization_base_url
        # token=oauth.fetch_token(request_token_url,config_ids.clientsecret,authorization_response='http://localhost:8069')
        # print ("token..............",token)

        session_manager = Oauth2SessionManager(
            client_id=config_ids.clientkey,
            client_secret=config_ids.clientsecret,
            base_url='http://localhost:8068/page/quick_book',
        )
        print ("session_manager...........", session_manager)
        callback_url = 'http://localhost:8068/page/quick_book'
        authorize_url = session_manager.get_authorize_url(callback_url)
        print ("authorize_url....dddddddd...........", authorize_url)
        # authorization_url = oauth.authorization_url(authorization_base_url)
        # print ("authorization_url............",authorization_url)
        url = request.httprequest.url
        state_dict = {
            'date': cust_date,
            'status': "Vendor",
        }
        state_json = json.dumps(state_dict)
        encoded_params = base64.urlsafe_b64encode(state_json)
        state_param = str(encoded_params)
        authorize_url = authorize_url.replace('None', state_param)
        print ("url...................", url)
        if authorize_url:
            print ("id..................")
            global test
            test = 'export_vendor'
            return json.dumps({'url': authorize_url})
        else:
            print ("else.,,,,,,,,,,,,,,,,,,,,")
            return request.render("quickbooks_connector_v10.quick_book_page")

        # cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        # global oauth
        # quick_config_obj = request.env['quick.configuration']
        # config_ids = quick_config_obj.search([])
        # quick_obj = request.env['quick.quick']
        # quick_ids = quick_obj.search([])
        # # config_data = quick_config_obj.browse(cr,uid,config_ids)
        # date_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # if quick_ids:
        #     quick_sup_id = quick_ids.write( {'exportdate_sup' : date_time})
        # else:
        #     uid = quick_obj.create({'exportdate_sup' : date_time})
        # # data = Quickbook(config_ids.clientkey, config_ids.clientsecret, config_ids.request_token_url, config_ids.access_token_url, config_ids.authorization_base_url)
        # oauth = self.connect()
        # # oauth = data.connect()
        # request_token_url = config_ids.request_token_url
        # authorization_base_url = config_ids.authorization_base_url
        # oauth.fetch_request_token(request_token_url)
        # authorization_url = oauth.authorization_url(authorization_base_url)
        # url = request.httprequest.url
        # if authorization_url:
        #     global test
        #     test = 'export_vendor'
        #     return json.dumps({'url': authorization_url})
        # else:
        #     return request.website.render("quickbooks_connector_v10.quick_book_page")
        #
        
        
        
    
    @http.route('/page/add_quick_b_account', auth='public', type='http', website=True)
    def add_quick_b_account(self, **post):
        last_date = parse(post['last_dt_acc'])
        tz = pytz.timezone("America/Toronto")
        aware_dt = tz.localize(last_date)
        acc_date = aware_dt.isoformat()
        print"acc_date",acc_date
        quick_config_obj = request.env['quick.configuration']
        quick_obj = request.env['quick.quick']
        quick_ids = quick_obj.search([])
        date_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if quick_ids:
            quick_item_id = quick_ids.write({'lastupdate_acc' : date_time})
        else:
            uid = quick_obj.create( {'lastupdate_acc' : date_time})
        config_ids = quick_config_obj.search([])
        # # config_data = quick_config_obj.browse(cr,uid,config_ids)
        # data = Quickbook(config_ids.clientkey, config_ids.clientsecret, config_ids.request_token_url, config_ids.access_token_url, config_ids.authorization_base_url)
        # oauth = data.connect()
        # request_token_url = config_ids.request_token_url
        # authorization_base_url = config_ids.authorization_base_url
        # oauth.fetch_request_token(request_token_url)
        # authorization_url = oauth.authorization_url(authorization_base_url)
        url= self.connect()
        authorize_url=url[0]
        url = request.httprequest.url
        print"=============url",url
        values = {
            'account':True
        }
        state_dict = {
            'date':acc_date,
            'status': "Accounts",
        }
        state_json = json.dumps(state_dict)
        encoded_params = base64.urlsafe_b64encode(state_json)
        state_param = str(encoded_params)
        authorize_url = authorize_url.replace('None', state_param)
        if authorize_url:
            global test
            global acc_date_n
            test = 'accounts'
            acc_date_n = acc_date
            return json.dumps({'url': authorize_url})
        else:
            return request.website.render("quickbooks_connector_v10.quick_book_page",values)
        
        
    @http.route('/page/add_quick_b_items', auth='public', type='http', website=True)
    def add_quick_b_items(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        global oauth 
        last_date = parse(post['last_dt_it'])
        tz = pytz.timezone("America/Toronto")
        aware_dt = tz.localize(last_date)
        item_date = aware_dt.isoformat()
        # print"item_date",item_date
        # quick_config_obj = request.env['quick.configuration']
        # quick_obj = request.env['quick.quick']
        # quick_ids = quick_obj.search([])
        # date_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # if quick_ids:
        #     quick_item_id = quick_ids.write({'lastupdate_item' : date_time})
        # else:
        #     uid = quick_obj.create({'lastupdate_item' : date_time})
        # config_ids = quick_config_obj.search([])
        # # config_data = quick_config_obj.browse(cr,uid,config_ids)
        # data = Quickbook(config_ids.clientkey, config_ids.clientsecret, config_ids.request_token_url, config_ids.access_token_url, config_ids.authorization_base_url)
        # oauth = data.connect()
        # print"==========oauth=====",oauth
        # print"========add_quick_b_data=====",post
        #
        # clientkey = config_ids.clientkey
        # clientsecret = config_ids.clientsecret
        # request_token_url = config_ids.request_token_url
        # access_token_url = config_ids.access_token_url
        # authorization_base_url = config_ids.authorization_base_url
        # oauth.fetch_request_token(request_token_url)
        # authorization_url = oauth.authorization_url(authorization_base_url)
        # print"=====authorization_url",authorization_url
        # url = request.httprequest.url
        # print"=============url",url
        url = self.connect()
        authorize_url = url[0]
        state_dict = {
            'date': item_date,
            'status': "Item",
        }
        state_json = json.dumps(state_dict)
        encoded_params = base64.urlsafe_b64encode(state_json)
        state_param = str(encoded_params)
        authorize_url = authorize_url.replace('None', state_param)
        url = request.httprequest.url
        values = {
            'item':True
        }
        if authorize_url:
            global test
            global item_date_n
            test = 'items'
            item_date_n = item_date
            return json.dumps({'url': authorize_url})
        else:
            return request.render("quickbooks_connector_v10.quick_book_page",values)
        
        
    @http.route('/page/export_quick_b_items', auth='public', type='http', website=True)
    def export_quick_b_items(self, **post):
        print"post", post
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

        last_date = parse(post['export_dt_it'])
        tz = pytz.timezone("America/Toronto")
        aware_dt = tz.localize(last_date)
        cust_date = aware_dt.isoformat()
        logger.error('++++cust_date+++++++++++++ %s', cust_date)
        global oauth
        quick_config_obj = request.env['quick.configuration']
        config_ids = quick_config_obj.search([])
        quick_obj = request.env['quick.quick']
        quick_ids = quick_obj.search([])
        # config_data = quick_config_obj.browse(cr,uid,config_ids)
        date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # data = Quickbook()
        # data = Quickbook()
        # print ("data////////////////",data)
        # oauth = data.connect()
        # print ("oauth//////////////",oauth)
        # request_token_url = config_ids.request_token_url
        # authorization_base_url = config_ids.authorization_base_url
        # token=oauth.fetch_token(request_token_url,config_ids.clientsecret,authorization_response='http://localhost:8069')
        # print ("token..............",token)

        session_manager = Oauth2SessionManager(
            client_id=config_ids.clientkey,
            client_secret=config_ids.clientsecret,
            base_url='http://localhost:8068/page/quick_book',
        )
        print ("session_manager...........", session_manager)
        callback_url = 'http://localhost:8068/page/quick_book'
        authorize_url = session_manager.get_authorize_url(callback_url)
        print ("authorize_url....dddddddd...........", authorize_url)
        # authorization_url = oauth.authorization_url(authorization_base_url)
        # print ("authorization_url............",authorization_url)
        url = request.httprequest.url
        state_dict = {
            'date': cust_date,

        }
        state_json = json.dumps(state_dict)
        encoded_params = base64.urlsafe_b64encode(state_json)
        state_param = str(encoded_params)
        authorize_url = authorize_url.replace('None', state_param)

        # cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        # global oauth
        # quick_config_obj = request.env['quick.configuration']
        # quick_obj = request.env['quick.quick']
        # quick_ids = quick_obj.search([])
        # date_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # if quick_ids:
        #     quick_item_id = quick_ids.write({'exportdate_item' : date_time})
        # else:
        #     uid = quick_obj.create({'exportdate_item' : date_time})
        # config_ids = quick_config_obj.search([])
        # # config_data = quick_config_obj.browse(cr,uid,config_ids)
        # data = Quickbook(config_ids.clientkey, config_ids.clientsecret, config_ids.request_token_url, config_ids.access_token_url, config_ids.authorization_base_url)
        # oauth = data.connect()
        # request_token_url = config_ids.request_token_url
        # authorization_base_url = config_ids.authorization_base_url
        # oauth.fetch_request_token(request_token_url)
        # authorization_url = oauth.authorization_url(authorization_base_url)
        # url = request.httprequest.url
        values = {
            'item':True
        }
        if authorize_url:
            global test
            test = 'export_items'
            return json.dumps({'url': authorize_url})
        else:
            return request.render("quickbooks_connector_v10.quick_book_page",values)
        
        
    @http.route('/page/add_quick_b_invoice', auth='public', type='http', website=True)
    def add_quick_b_invoice(self, **post):
        print"post",post
        fr_date = parse(post['from_dt_in'])
        print"fr_date",fr_date
        tz = pytz.timezone("America/Toronto")
        aware_dt = tz.localize(fr_date)
        fr_date_n = aware_dt.isoformat()
        print"fr_date_n",fr_date_n
        to_date = parse(post['to_dt_in'])
        print"to_date",to_date
        tz = pytz.timezone("America/Toronto")
        aware_to_dt = tz.localize(to_date)
        to_date_n = aware_to_dt.isoformat()
        print"to_date_n",to_date_n
#        date = post['from_dt_in']
#        new_dt = date.replace(' ','T')
#        print"new_dt",new_dt
#        dt = new_dt+ "-04:00"
#        print"dt",dt
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        global oauth 
        quick_config_obj = request.env['quick.configuration']
        quick_obj = request.env['quick.quick']
        quick_ids = quick_obj.search([])
        date_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if quick_ids:
            vals = {
                    'from_date_in':date_time,
                    'to_date_in':False
            }
            print"vals",vals
            quick_invoice_id = quick_ids.write(vals)
            print"quick_invoice_id",quick_invoice_id
        else:
            vals = {
                    'from_date_in':date_time,
                    'to_date_in':False,
            }
            print"vals",vals
            uid = quick_obj.create(vals)
            print"=======uid=====",uid
        config_ids = quick_config_obj.search([])
        url = self.connect()
        authorize_url=url[0]
        state_dict = {
            'date': fr_date_n,
            'date1':to_date_n,
            'status': "Invoice",
        }
        state_json = json.dumps(state_dict)
        encoded_params = base64.urlsafe_b64encode(state_json)
        state_param = str(encoded_params)
        authorize_url = authorize_url.replace('None', state_param)

        # clientkey = config_ids.clientkey
        # clientsecret = config_ids.clientsecret
        # request_token_url = config_ids.request_token_url
        # access_token_url = config_ids.access_token_url
        # authorization_base_url = config_ids.authorization_base_url
        # logger.error('++++request_token_url+++++++++ %s',request_token_url)
        # oauth.fetch_request_token(request_token_url)
        # authorization_url = oauth.authorization_url(authorization_base_url)
        # url = request.httprequest.url
        values = {
            'invoice':True
        }
        if authorize_url:
            global test
            global from_dt
            global to_dt
            test = 'invoice'
            from_dt  = fr_date_n
            to_dt = to_date_n
            return json.dumps({'url': authorize_url})
        else:
            return request.render("quickbooks_connector_v10.quick_book_page",values)
        
        
    @http.route('/page/export_quick_b_invoice', auth='public', type='http', website=True)
    def export_quick_b_invoice(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        from_date = parse(post['from_dt_ex_in'])
        tz = pytz.timezone("America/Toronto")
        aware_from_dt = tz.localize(from_date)
        inv_frm_date = aware_from_dt.isoformat()

        to_date = parse(post['to_date_ex_in'])
        ts = pytz.timezone("America/Toronto")
        aware_to_dt = ts.localize(to_date)
        inv_to_date = aware_to_dt.isoformat()

        global oauth 
        quick_config_obj = request.env['quick.configuration']
        quick_obj = request.env['quick.quick']
        quick_ids = quick_obj.search([])
        date_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if quick_ids:
            vals = {
                    'from_date_ex_in':date_time,
                    'to_date_ex_in':False
            }
            print"vals",vals
            quick_invoice_id = quick_ids.write(vals)
            print"quick_invoice_id",quick_invoice_id
        else:
            vals = {
                    'from_date_ex_in':date_time,
                    'to_date_ex_in':False
            }
            print"vals",vals
            uid = quick_obj.create(vals)
            print"=======uid=====",uid
        config_ids = quick_config_obj.search([])
        # config_data = quick_config_obj.browse(cr,uid,config_ids)
        # data = Quickbook(config_ids.clientkey, config_ids.clientsecret, config_ids.request_token_url, config_ids.access_token_url, config_ids.authorization_base_url)
        # oauth = data.connect()
        # request_token_url = config_ids.request_token_url
        # authorization_base_url = config_ids.authorization_base_url
        # oauth.fetch_request_token(request_token_url)
        # authorization_url = oauth.authorization_url(authorization_base_url)
        session_manager = Oauth2SessionManager(
            client_id=config_ids.clientkey,
            client_secret=config_ids.clientsecret,
            base_url='http://localhost:8068/page/quick_book',
        )
        print ("session_manager...........", session_manager)
        callback_url = 'http://localhost:8068/page/quick_book'
        authorize_url = session_manager.get_authorize_url(callback_url)
        print ("authorize_url....dddddddd...........", authorize_url)
        # authorization_url = oauth.authorization_url(authorization_base_url)
        # print ("authorization_url............",authorization_url)
        url = request.httprequest.url
        state_dict = {
            'date': inv_to_date,


        }
        state_json = json.dumps(state_dict)
        encoded_params = base64.urlsafe_b64encode(state_json)
        state_param = str(encoded_params)
        authorize_url = authorize_url.replace('None', state_param)

        values = {
            'export_invoice':True
        }
        print"authorization_url_inv",authorize_url
        if authorize_url:
            global test
            global from_dt
            global to_dt
            test = 'export_invoice'
            from_dt  = post['from_dt_ex_in']
            to_dt = post['to_date_ex_in']
            return json.dumps({'url': authorize_url})
        else:
            return request.render("quickbooks_connector_v10.quick_book_page",values)
        
        
        
    @http.route('/page/add_quick_b_purchase', auth='public', type='http', website=True)
    def add_quick_b_purchase(self, **post):
        print"post",post
        fr_date = parse(post['from_dt_po'])
        print"fr_date",fr_date
        tz = pytz.timezone("America/Toronto")
        aware_dt = tz.localize(fr_date)
        fr_date_po = aware_dt.isoformat()
        print"fr_date_po",fr_date_po
        to_date = parse(post['to_dt_po'])
        print"to_date",to_date
        tz = pytz.timezone("America/Toronto")
        aware_to_dt = tz.localize(to_date)
        to_date_po = aware_to_dt.isoformat()
        print"to_date_po",to_date_po
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        global oauth 
        quick_config_obj = registry.get('quick.configuration')
        quick_obj = registry.get('quick.quick')
        quick_ids = quick_obj.search(cr, uid, []) 
        date_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if quick_ids:
            vals = {
                    'from_date_pr':date_time,
                    'to_date_pr':False,
            }
            quick_purchase_id = quick_obj.write(cr, SUPERUSER_ID, quick_ids, vals)
        else:
            vals = {
                    'from_date_pr':date_time,
                    'to_date_pr':False,
            }
            uid_val = quick_obj.create(cr, SUPERUSER_ID, vals)
        config_ids = quick_config_obj.search(cr, uid, []) 
        config_data = quick_config_obj.browse(cr,uid,config_ids)
        data = Quickbook(config_data.clientkey, config_data.clientsecret, config_data.request_token_url, config_data.access_token_url, config_data.authorization_base_url)
        oauth = data.connect()
        request_token_url = config_data.request_token_url
        authorization_base_url = config_data.authorization_base_url
        oauth.fetch_request_token(request_token_url)
        authorization_url = oauth.authorization_url(authorization_base_url)
        if authorization_url:
            global test
            global from_dt
            global to_dt
            test = 'purchase'
            from_dt  = fr_date_po
            to_dt = to_date_po
            return json.dumps({'url': authorization_url})
        else:
            return request.render("quickbooks_connector_v10.quick_book_page")
        
    @http.route('/page/export_quick_b_purchase', auth='public', type='http', website=True)
    def export_quick_b_purchase(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        global oauth 
        quick_config_obj = registry.get('quick.configuration')
        quick_obj = registry.get('quick.quick')
        quick_ids = quick_obj.search(cr, uid, []) 
        date_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if quick_ids:
            vals = {
                    'from_date_ex_pr':date_time,
                    'to_date_ex_pr':False,
            }
            quick_purchase_id = quick_obj.write(cr, SUPERUSER_ID, quick_ids, vals)
        else:
            vals = {
                    'from_date_ex_pr':date_time,
                    'to_date_ex_pr':False,
            }
            uid_val = quick_obj.create(cr, SUPERUSER_ID, vals)
        config_ids = quick_config_obj.search(cr, uid, []) 
        config_data = quick_config_obj.browse(cr,uid,config_ids)
        data = Quickbook(config_data.clientkey, config_data.clientsecret, config_data.request_token_url, config_data.access_token_url, config_data.authorization_base_url)
        oauth = data.connect()
        request_token_url = config_data.request_token_url
        authorization_base_url = config_data.authorization_base_url
        oauth.fetch_request_token(request_token_url)
        authorization_url = oauth.authorization_url(authorization_base_url)
        if authorization_url:
            global test
            global from_dt_pr
            global to_dt_pr
            test = 'export_purchase'
            from_dt_pr  = post['from_dt_ex_po']
            to_dt_pr = post['to_dt_ex_po']
            return json.dumps({'url': authorization_url})
        else:
            return request.render("quickbooks_connector_v10.quick_book_page")
        
        
    @http.route('/page/add_quick_b_sale', auth='public', type='http', website=True)
    def add_quick_b_sale(self, **post):
        print"add_quick_b_sale"
        fr_date = parse(post['from_dt_so'])
        tz = pytz.timezone("America/Toronto")
        aware_dt = tz.localize(fr_date)
        fr_date_so = aware_dt.isoformat()
        to_date = parse(post['to_dt_so'])
        tz = pytz.timezone("America/Toronto")
        aware_to_dt = tz.localize(to_date)
        to_date_so = aware_to_dt.isoformat()
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        global oauth 
        quick_config_obj = registry.get('quick.configuration')
        quick_obj = registry.get('quick.quick')
        quick_ids = quick_obj.search(cr, uid, [])
        date_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if quick_ids:
            vals = {
                    'from_date_so':date_time,
                    'to_date_so':False,
            }
            quick_sale_id = quick_obj.write(cr, SUPERUSER_ID, quick_ids, vals)
        else:
            vals = {
                    'from_date_so':date_time,
                    'to_date_so':False,
            }
            uid_val = quick_obj.create(cr, SUPERUSER_ID, vals)
        config_ids = quick_config_obj.search(cr, uid, []) 
        config_data = quick_config_obj.browse(cr,uid,config_ids)
        data = Quickbook(config_data.clientkey, config_data.clientsecret, config_data.request_token_url, config_data.access_token_url, config_data.authorization_base_url)
        oauth = data.connect()
        request_token_url = config_data.request_token_url
        authorization_base_url = config_data.authorization_base_url
        oauth.fetch_request_token(request_token_url)
        authorization_url = oauth.authorization_url(authorization_base_url)
        if authorization_url:
            global test
            global from_dt
            global to_dt
            test = 'sale'
            from_dt  = fr_date_so
            to_dt = to_date_so
            return json.dumps({'url': authorization_url})
        else:
            return request.render("quickbooks_connector_v10.quick_book_page")
        
    @http.route('/page/export_quick_b_sale', auth='public', type='http', website=True)
    def export_quick_b_sale(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        global oauth 
        quick_config_obj = registry.get('quick.configuration')
        quick_obj = registry.get('quick.quick')
        quick_ids = quick_obj.search(cr, uid, [])
        date_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if quick_ids:
            vals = {
                    'from_date_ex_so':date_time,
                    'to_date_ex_so':False,
            }
            quick_sale_id = quick_obj.write(cr, SUPERUSER_ID, quick_ids, vals)
        else:
            vals = {
                    'from_date_ex_so':date_time,
                    'to_date_ex_so':False,
            }
            uid_val = quick_obj.create(cr, SUPERUSER_ID, vals)
        config_ids = quick_config_obj.search(cr, uid, []) 
        config_data = quick_config_obj.browse(cr,uid,config_ids)
        data = Quickbook(config_data.clientkey, config_data.clientsecret, config_data.request_token_url, config_data.access_token_url, config_data.authorization_base_url)
        oauth = data.connect()
        request_token_url = config_data.request_token_url
        authorization_base_url = config_data.authorization_base_url
        oauth.fetch_request_token(request_token_url)
        authorization_url = oauth.authorization_url(authorization_base_url)
        if authorization_url:
            global test
            global from_dt_sr
            global to_dt_sr
            test = 'export_sale'
            from_dt_sr  = post['from_dt_ex_so']
            to_dt_sr = post['to_dt_ex_so']
            return json.dumps({'url': authorization_url})
        else:
            return request.render("quickbooks_connector_v10.quick_book_page")
        
        
    def get_customer(self, tag):
        cust = []
        print"=====tag=======",tag
#        tags = tag.getElementsByTagName('Customer')
        for node in tag:
            customer = {}
            print"======node=========",node
            
            for cNode in node.childNodes:
                logger.error('++++cNode.nodeName+++++++++++++ %s',cNode.nodeName)
                logger.error('++++cNode.childNodes[0].data+++++++++++++ %s',cNode.childNodes[0])
                if cNode.nodeName == 'Id':
                    customer.update({'quick_id': cNode.childNodes[0].data})
                if cNode.nodeName == 'FullyQualifiedName':
                    customer.update({'name': cNode.childNodes[0].data})
                if cNode.nodeName == 'MetaData':
                    for child_node in cNode.childNodes:
                        if child_node.nodeName == 'CreateTime':
                            customer.update({'date': child_node.childNodes[0].data})
                if cNode.nodeName == 'DisplayName':
                    customer.update({'display_name': cNode.childNodes[0].data})
                if cNode.nodeName == 'Active':
                    customer.update({'active': cNode.childNodes[0].data})
                if cNode.nodeName == 'PrimaryPhone':
                    for child_node in cNode.childNodes:
                        if child_node.nodeName == 'FreeFormNumber':
                            customer.update({'phone': child_node.childNodes[0].data})
                if cNode.nodeName == 'PrimaryEmailAddr':
                    for child_node in cNode.childNodes:
                        if child_node.nodeName == 'Address':
                            customer.update({'email': child_node.childNodes[0].data})
                if cNode.nodeName == 'BillAddr':
                    for child_node in cNode.childNodes:
                        if child_node.nodeName == 'Line1':
                            customer.update({'street': child_node.childNodes[0].data})
                        if child_node.nodeName == 'City':
                            customer.update({'city': child_node.childNodes[0].data})
                        if child_node.nodeName == 'CountrySubDivisionCode':
                            customer.update({'country': child_node.childNodes[0].data})
                        if child_node.nodeName == 'PostalCode':
                            customer.update({'zip': child_node.childNodes[0].data})  
            cust.append(customer)
        print"cust========>",cust
        logger.error('++++cust+++++++++++++ %s',cust)
        return cust
    

    def export_customer(self,realmid,acess_token,context):
        print"realmid===>", realmid
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        quick_config_obj = request.env['quick.configuration']
        config_ids = quick_config_obj.search([])
        # config_data = quick_config_obj.browse(cr,uid,config_ids)
        partner_obj = request.env['res.partner']
        # print'context---------------',context
        if context.get('customer_ids', False):
            update = False
            customer_ids = context['customer_ids']
        else:
            update = True
            # customer_ids = partner_obj.search([])
            # [('quick_id', '=', False), ('quick_export', '=', False), ('faulty', '=', False)])
            customer_ids = partner_obj.search(
                [('quick_id', '=', False), ('quick_export', '=', False), ('faulty', '=', False)])

        print"customer_ids", customer_ids
        for customer_data in customer_ids:
            print".................................customer_data.............................", customer_data
            # headers = {'content-type': 'application/xml'
            #
            #            }

            cust_data = ''
            cust_data += """<Customer xmlns="http://schema.intuit.com/finance/v3" domain="QBO" sparse="false">
                                                        <FullyQualifiedName>%s</FullyQualifiedName>
                                                        <CompanyName>%s</CompanyName>
                                                        <DisplayName>%s</DisplayName>
                                                        <PrimaryPhone>
                                                            <FreeFormNumber>%s</FreeFormNumber>
                                                        </PrimaryPhone>
                                                        <PrimaryEmailAddr>
                                                            <Address>%s</Address>
                                                        </PrimaryEmailAddr>
                                                        <BillAddr>
                                                            <Line1>%s</Line1>
                                                            <City>%s</City>
                                                            <Country>%s</Country>
                                                            <CountrySubDivisionCode>%s</CountrySubDivisionCode>
                                                            <PostalCode>%s</PostalCode>
                                                        </BillAddr>
                                                    </Customer>""" % (
                customer_data.parent_id.name, customer_data.parent_id.name or '', customer_data.parent_id.name, customer_data.phone,
                customer_data.email or '', customer_data.street, customer_data.street2 or '', customer_data.city,
                customer_data.country_id.name, customer_data.zip)
            print"=cust_data=========>", cust_data
            # getresource = 'https://sandbox-quickbooks.api.intuit.com/v3/company/' + realmid + '/customer?minorversion=12'
            getresource = 'https://sandbox-quickbooks.api.intuit.com/v3/company/' + realmid + '/customer?minorversion=4'

            print"getresource================>", getresource
            # getresource = config_ids.url+config_ids.company+'/customer'
            logger.error('++++cust_data+++++++++++++ %s', cust_data)
            cust_data = cust_data.encode('utf-8')
            # ===========================================================#
            auth_client = AuthClient(
                client_id=config_ids.clientkey,
                client_secret=config_ids.clientsecret,
                redirect_uri='http://localhost:8068 /page/quick_book',
                environment='sandbox'
            )
            sc = [Scopes.ACCOUNTING]
            auth_url = auth_client.get_authorization_url(sc)
            print"auth_url====>", auth_url
            auth_header = 'Bearer {0}'.format(acess_token)
            print"auth_header====>", auth_header
            # ===========================================================#
            headers = {
                'Authorization': auth_header,
                'Accept': 'application/xml',
                'content-type': 'application/xml'
            }

            r = requests.post(getresource, data=cust_data, headers=headers)
            print"r================>", r
            logger.error('++++r.status_code+++++++++++++ %s', r.status_code)
            print"r========>", r.content
            data = r.content
            responseDOM = parseString(data)
            print'responseDOM.toprettyxml()---export_customer-----', responseDOM.toprettyxml()
            logger.error('++++r.toprettyxml+++++++++++++ %s', responseDOM.toprettyxml())
            quick_id = False
            if r.status_code == 200:
                tag = responseDOM.getElementsByTagName('Customer')

                for node in tag:
                    print"node.childNodesnode.childNodes", node.childNodes
                    for cNode in node.childNodes:
                        print"=cNode.nodeName======>", cNode.nodeName
                        if cNode.nodeName == 'Id':
                            quick_id = cNode.childNodes[0].data
                            print"quick_id", quick_id
                if quick_id:
                    cust_id = customer_data.write(
                        {'faulty': False, 'faulty_reason': False, 'quick_export': True, 'quick_id': quick_id})
                    print"cust_id", cust_id

            if not quick_id:
                tag = responseDOM.getElementsByTagName('Error')
                for node in tag:
                    for cNode in node.childNodes:
                        print'cNode.nodeName-----', cNode.nodeName
                        if cNode.nodeName == 'Detail':
                            faulty_reason = cNode.childNodes[0].data
                customer_data.write({'faulty': True, 'faulty_reason': faulty_reason})

        if update:
            update_customer_ids = partner_obj.search([('quick_id', '=', True)])
            #            update_customer_ids =[10]
            for update_customer_data in update_customer_ids:
                print"update_customer_data", update_customer_data
                headers = {'content-type': 'application/xml'}
                up_cust_data = ''
                phone = ''
                email = ''
                if update_customer_data.phone:
                    phone = """<PrimaryPhone>
                                                <FreeFormNumber>%s</FreeFormNumber>
                                            </PrimaryPhone>""" % (update_customer_data.phone)

                if update_customer_data.email:
                    email = """<PrimaryEmailAddr>
                                                <Address>%s</Address>
                                            </PrimaryEmailAddr>""" % (update_customer_data.email)

                up_cust_data += """<Customer xmlns="http://schema.intuit.com/finance/v3" domain="QBO" sparse="false">
                                                            <sparse>True</sparse>
                                                            <Id>%s</Id>
                                                            <FullyQualifiedName>%s</FullyQualifiedName>
                                                            <CompanyName>%s</CompanyName>
                                                            <DisplayName>%s</DisplayName>
                                                            %s
                                                            %s
                                                            <BillAddr>
                                                                <Line1>%s</Line1>
                                                                <City>%s</City>
                                                                <Country>%s</Country>
                                                                <CountrySubDivisionCode>%s</CountrySubDivisionCode>
                                                                <PostalCode>%s</PostalCode>
                                                            </BillAddr>
                                                            <SyncToken>0</SyncToken>
                                                        </Customer>""" % (
                    update_customer_data.quick_id, update_customer_data.name,
                    update_customer_data.parent_id.name or '', update_customer_data.name, phone, email,
                    update_customer_data.street, update_customer_data.street2 or '', update_customer_data.city,
                    update_customer_data.country_id.name, update_customer_data.zip)
                print"=up_cust_data=========>", up_cust_data
                getresource = config_ids.url + config_ids.company + '/customer'
                logger.error('++++update_cust_data++++request+++++++++ %s', up_cust_data)
                r = oauth.post(getresource, data=up_cust_data, headers=headers)
                logger.error('++++r.status_code+++++++++++++ %s', r.status_code)
                print"r========>", r.content
                data = r.content
                responseDOM = parseString(data)
                logger.error('++++r.toprettyxml++++jkjk+++++++++ %s', responseDOM.toprettyxml())
                print'responseDOM.toprettyxml()---export_customer-----', responseDOM.toprettyxml()

    def get_vendor(self, tag):
        vendors = []
        print"=====tag=======",tag
        print"=====Welcomeeeeeeeee======="
#        tags = tag.getElementsByTagName('Customer')
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        country_obj = request.env['res.country']
        partner_obj = request.env['res.partner']
        for node in tag:
            sup = {}
            print"======node=========",node
            for cNode in node.childNodes:
                if cNode.nodeName == 'Id':
                    sup.update({'quick_id': cNode.childNodes[0].data})
                if cNode.nodeName == 'GivenName':
                    sup.update({'fn_name': cNode.childNodes[0].data})
                if cNode.nodeName == 'FamilyName':
                    sup.update({'ln_name': cNode.childNodes[0].data})
                if cNode.nodeName == 'MetaData':
                    for child_node in cNode.childNodes:
                        if child_node.nodeName == 'CreateTime':
                            sup.update({'date': child_node.childNodes[0].data})
                if cNode.nodeName == 'DisplayName':
                    sup.update({'display_name': cNode.childNodes[0].data})
                if cNode.nodeName == 'PrimaryPhone':
                    for child_node in cNode.childNodes:
                        if child_node.nodeName == 'FreeFormNumber':
                            sup.update({'phone': child_node.childNodes[0].data})
                if cNode.nodeName == 'PrimaryEmailAddr':
                    for child_node in cNode.childNodes:
                        if child_node.nodeName == 'Address':
                            sup.update({'email': child_node.childNodes[0].data})
                if cNode.nodeName == 'WebAddr':
                    for child_node in cNode.childNodes:
                        if child_node.nodeName == 'URI':
                            sup.update({'website': child_node.childNodes[0].data})
                if cNode.nodeName == 'BillAddr':
                    for child_node in cNode.childNodes:
                        if child_node.nodeName == 'Line1':
                            sup.update({'street': child_node.childNodes[0].data})
                        if child_node.nodeName == 'City':
                            sup.update({'city': child_node.childNodes[0].data})
                        if child_node.nodeName == 'CountrySubDivisionCode':
                            sup.update({'country': child_node.childNodes[0].data})
                        if child_node.nodeName == 'PostalCode':
                            sup.update({'zip': child_node.childNodes[0].data})  
            vendors.append(sup)
        print"vendor========>",vendors
        for vendor in vendors:
            name = ''
            if vendor.get('fn_name'):
                name += vendor.get('fn_name')
                vendor.pop('fn_name')
            if vendor.get('ln_name'):
                name += ' '+vendor.get('ln_name')
                vendor.pop('ln_name')
            if not(name):
                vendor.update({'name': vendor.get('display_name')})
            else:
                vendor.update({'name': name})
            
            country_ids = country_obj.search([('code','=',vendor.get('country'))])
            print "==================country_ids================",country_ids
            if country_ids:
                vendor.update({'country_id': country_ids[0].id})
            # else:
            #     vendor.update({'country_id': False})
            partner_ids = partner_obj.search([('email','=',vendor.get('email')),('name','=',vendor.get('name'))])
            vendor.update({'supplier': True,'customer':False})
            print"vendor",vendor
            print"partner_ids",partner_ids
            if not partner_ids:
                partner_id = partner_obj.create(vendor)
                print"partner_id",partner_id
            else:
                partner_ids.write({'quick_id': vendor.get('quick_id')})
        return True
    
    
    def export_vendor(self,realmid,access_token):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        quick_config_obj = request.env['quick.configuration']
        config_ids = quick_config_obj.search([])
        # config_data = quick_config_obj.browse(config_ids)
        partner_obj = request.env['res.partner']
        # supplier_ids = partner_obj.search( [('quick_id','=',False),('quick_export','=',False),('supplier','=',True),('faulty','=',False)])
        supplier_ids = partner_obj.search([('supplier','=',True),('faulty','=',False)])
        print"supplier_ids",supplier_ids
        for supplier_data in supplier_ids:
            print"supplier_data",supplier_data
            headers = {'content-type': 'application/xml'}
            sup_data = ''
            sup_data += """<Vendor xmlns="http://schema.intuit.com/finance/v3"  sparse="false">
                        <CompanyName>%s</CompanyName>
                        <DisplayName>%s</DisplayName>
                        <PrimaryPhone>
                          <FreeFormNumber>%s</FreeFormNumber>
                        </PrimaryPhone>
                        <Mobile>
                          <FreeFormNumber>%s</FreeFormNumber>
                        </Mobile>
                        <PrimaryEmailAddr>
                          <Address>%s</Address>
                        </PrimaryEmailAddr>
                      </Vendor>"""% (supplier_data.parent_id.name or '',supplier_data.name,supplier_data.phone,supplier_data.mobile or supplier_data.phone,supplier_data.email)
            # print"=sup_data=========>",sup_data
            # getresource = config_ids.url+config_ids.company+'/vendor'
            getresource = 'https://sandbox-quickbooks.api.intuit.com/v3/company/' + realmid + '/vendor?minorversion=4'
            sup_data = sup_data.encode('utf-8')
            auth_header = 'Bearer {0}'.format(access_token)
            print"auth_header====>", auth_header
            headers = {
                'Authorization': auth_header,
                'Accept': 'application/xml',
                'content-type': 'application/xml'
            }
            # ===========================================================#

            r = requests.post(getresource, data=sup_data, headers=headers)

            # r = oauth.post(getresource,data = sup_data,headers=headers)
            logger.error('++++r.status_code+++++++++++++ %s',r.status_code)
            print"status========>", r.status_code
            print"response========>",r.content

            if r.status_code==200:

                data = r.content
                responseDOM = parseString(data)
                tag = responseDOM.getElementsByTagName('Vendor')
                quick_id = False
                for node in tag:
                    for cNode in node.childNodes:
                        if cNode.nodeName == 'Id':
                            quick_id = cNode.childNodes[0].data
                            print"quick_id",quick_id
                if quick_id:
                    sup_id = supplier_data.write({'quick_export' : True,'quick_id': quick_id})
                    print"sup_id",sup_id
                    
    
                    
    
    
    
    def get_account(self, tag):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        account_orm = request.env['quick.account']
        
        acc_i = []
        for node in tag:
            accounts = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'Id':
                    accounts.update({'quick_acc_id': cNode.childNodes[0].data})
                if cNode.nodeName == 'Name':
                    accounts.update({'name': cNode.childNodes[0].data})
                if cNode.nodeName == 'AccountType':
                    accounts.update({'acc_type': cNode.childNodes[0].data})
                if cNode.nodeName == 'Classification':
                    accounts.update({'classification': cNode.childNodes[0].data})
                if cNode.nodeName == 'Active':
                    accounts.update({'active': cNode.childNodes[0].data})
            acc_i.append(accounts)
        print"acc_i",acc_i
        for account in acc_i:
            account_ids = account_orm.search([('quick_acc_id','=',accounts.get('quick_acc_id'))])
            if not account_ids:
                account_id = account_orm.create(account)
        return True
    
    def get_items(self, tag):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        product_orm = request.env['product.product']
        item_i = []
        for node in tag:
            items = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'Id':
                    items.update({'quick_prod_id': cNode.childNodes[0].data})
                if cNode.nodeName == 'Name':
                    items.update({'name': cNode.childNodes[0].data})
                if cNode.nodeName == 'QtyOnHand':
                    items.update({'qty_available': cNode.childNodes[0].data})
                if cNode.nodeName == 'MetaData':
                    for child_node in cNode.childNodes:
                        if child_node.nodeName == 'CreateTime':
                            items.update({'create_date': child_node.childNodes[0].data})
                if cNode.nodeName == 'UnitPrice':
                    items.update({'lst_price': float(cNode.childNodes[0].data)})
                if cNode.nodeName == 'PurchaseCost':
                    items.update({'standard_price': cNode.childNodes[0].data})
                if cNode.nodeName == 'Type':
                    if cNode.childNodes[0].data == 'Service':
                        items.update({'type': 'service'})
                    if cNode.childNodes[0].data == 'Inventory':
                        items.update({'type': 'product'})
            item_i.append(items)
        print"items",item_i
        for items in item_i:
            product_ids = product_orm.search([('name','=',items.get('name'))])
            if not product_ids:
                product_id = product_orm.create(items)
                print "items.get('qty_available')",items.get('qty_available'),type(items.get('qty_available'))
                if items.get('qty_available'):
                    amt = items.get('qty_available')
                    amount = amt[:1]
                    if  amount == '-':
                        self.set_stock(0,product_id)
                    else:
                        self.set_stock(items.get('qty_available'),product_id)
        return True


    def export_items(self,realmid,access_token,accounts):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        quick_config_obj = request.env['quick.configuration']
        config_ids = quick_config_obj.search([])
        # config_data = quick_config_obj.browse(cr,uid,config_ids)
        product_obj = request.env['product.product']
        quick_acc_obj = request.env['quick.account']
        product_ids = product_obj.search([])
        # product_ids = product_obj.search([('quick_prod_id','=',False),('quick_export','=',False)])
        print"product_ids",product_ids
        AssetAccountRef = ''
        for product_data in product_ids:
            print"product_data",product_data
            logger.error('++++product_data++++++++++ %s',product_data)
            # headers = {'content-type': 'application/xml'}
            prod_data = ''
            if product_data.type == 'product':
                if not product_data.property_account_income_id:
                    if product_data.categ_id.property_account_income_categ_id:
                        print "===================product_data.categ_id.property_account_income_categ_id===================",product_data.categ_id.property_account_income_categ_id
#                    if product_data.categ_id.property_stock_account_input_categ:
                        acc_ids = quick_acc_obj.search([('acc_id','=',product_data.categ_id.property_account_income_categ_id.id)])
                        
                    else:
                        continue
                else:
                    acc_ids = quick_acc_obj.search([('acc_id','=',product_data.property_account_income_id.id)])
                    if not acc_ids:
                       account_ids = product_data.property_account_income_id.quickbook_chart_id
                # quick_acc_data = quick_acc_obj.browse(cr,SUPERUSER_ID,acc_ids)
                print"acc_ids",acc_ids
                logger.error('++++acc_ids+++++++++++++ %s',acc_ids)
                if not product_data.property_account_expense_id:
                    if product_data.categ_id.property_account_expense_categ_id:
                        acc_exp_ids = quick_acc_obj.search([('acc_id','=',product_data.categ_id.property_account_expense_categ_id.id)])
                        print"acc_exp_ids",acc_exp_ids
                        logger.error('++++acc_exp_ids++++++++++ %s',acc_exp_ids)
                    else:
                        continue
                else:
                    acc_exp_ids = quick_acc_obj.search([('acc_id','=',product_data.property_account_expense_id.id)])
                    account_exp_ids = product_data.property_account_expense_id.quickbook_chart_id
                logger.error('++++acc_exp_ids+++++++++++++ %s',acc_exp_ids)
                for account in accounts:
                     acc_type = account.AccountType
                     if acc_type == 'Current Asset':
                        account_asset_ids = account.Id
                        AssetAccountRef = account_asset_ids
                # if product_data.categ_id.property_stock_valuation_account_id:
                #     acc_asset_ids = quick_acc_obj.search([('acc_id','=',product_data.categ_id.property_stock_valuation_account_id.id)])
                #     if not acc_asset_ids:
                #         account_asset_ids = product_data.categ_id.property_stock_valuation_account_id.quickbook_chart_id
                #     AssetAccountRef = acc_asset_ids.quick_acc_id if acc_asset_ids else account_asset_ids
                #     print"acc_asset_ids",acc_asset_ids
                #     logger.error('++++acc_asset_ids+++++++++++ %s',acc_asset_ids)
                # else:
                #     continue
                logger.error('++++acc_exp_ids+++++++++++++ %s',acc_exp_ids)
                date = parse(product_data.create_date)
                tz = pytz.timezone("America/Toronto")
                aware_dt = tz.localize(date)
                cr_date = aware_dt.isoformat()
                if acc_ids or account_ids:
                 IncomeAccountRef = acc_ids.quick_acc_id if acc_ids else account_ids
                if not IncomeAccountRef:
                    IncomeAccountRef = ''
                if acc_ids or account_ids:
                   ExpenseAccountRef = acc_exp_ids.quick_acc_id if acc_exp_ids else account_exp_ids
                if not ExpenseAccountRef:
                    ExpenseAccountRef = ''

                # if not AssetAccountRef:
                #     AssetAccountRef = ''

                
#                prod_data += """<Item xmlns="http://schema.intuit.com/finance/v3" sparse="false">
#                            <Name>%s</Name>
#                            <Taxable>true</Taxable>
#                            <IncomeAccountRef >247</IncomeAccountRef>
#                            <PurchaseCost>%s</PurchaseCost>
#                            <ExpenseAccountRef>169</ExpenseAccountRef>
#                            <AssetAccountRef>248</AssetAccountRef>
#                            <Type>Inventory</Type>
#                            <TrackQtyOnHand>true</TrackQtyOnHand>,
#                            <QtyOnHand>%s</QtyOnHand>,
#                            <InvStartDate>%s</InvStartDate>
#                        </Item>"""% (product_data.name,product_data.lst_price,product_data.qty_available,cr_date)

                prod_data += """<Item xmlns="http://schema.intuit.com/finance/v3" sparse="false">
                            <Name>%s</Name>
                            <IncomeAccountRef >530</IncomeAccountRef>
                            <PurchaseCost>%s</PurchaseCost>
                            <ExpenseAccountRef>559</ExpenseAccountRef>
                            <AssetAccountRef>560</AssetAccountRef>
                            <Type>Inventory</Type>
                            <TrackQtyOnHand>true</TrackQtyOnHand>,
                            <QtyOnHand>%s</QtyOnHand>,
                            <InvStartDate>%s</InvStartDate>
                        </Item>"""% (product_data.name,product_data.lst_price,product_data.qty_available,cr_date)
                        
            if product_data.type == 'service':
                if product_data.property_account_income_id:
                    acc_ids = product_data.property_account_income_id.quick_chart_id
                else:
                    if not product_data.property_account_income_id:
                      acc_ids = quick_acc_obj.search([('acc_id','=',product_data.categ_id.property_account_income_categ_id.id)])
                    else:
                      acc_ids = quick_acc_obj.search([('acc_id','=',product_data.property_account_income_id.id)])
                print"acc_ids",acc_ids
                # quick_acc_data = quick_acc_obj.browse(cr,SUPERUSER_ID,acc_ids)

                prod_data += """<Item xmlns="http://schema.intuit.com/finance/v3" sparse="false">
                    <Name>%s</Name>
                    <IncomeAccountRef >%s</IncomeAccountRef>
                    <PurchaseCost>%s</PurchaseCost>
                    <Type>Service</Type>
                    <TrackQtyOnHand>false</TrackQtyOnHand>,
                </Item>"""% (product_data.name,acc_ids.quick_acc_id or ' ',product_data.lst_price )

            print"=prod=========>",prod_data
            # getresource = config_ids.url+config_ids.company+'/item'
            getresource = 'https://sandbox-quickbooks.api.intuit.com/v3/company/' + realmid + '/item?minorversion=4'
            prod_data = prod_data.encode('utf-8')
            auth_header = 'Bearer {0}'.format(access_token)
            print"auth_header====>", auth_header
            headers = {
                'Authorization': auth_header,
                'Accept': 'application/xml',
                'content-type': 'application/xml'
            }






            r = requests.post(getresource,data = prod_data,headers=headers)
            logger.error('++++prod_data+++++++++++++ %s',prod_data)
            logger.error('++++r.status_code+++++++++++++ %s',r.status_code)
            logger.error('++++r.content+++++++++++++ %s',r.content)
            print"r========>",r.content
            if r.status_code==200:

                data = r.content
                responseDOM = parseString(data)
                tag = responseDOM.getElementsByTagName('Item')
                quick_id = False
                for node in tag:
                    for cNode in node.childNodes:
                        if cNode.nodeName == 'Id':
                            quick_id = cNode.childNodes[0].data
                            print"quick_id",quick_id
                if quick_id:
                    prod_id = product_data.write({'quick_export' : True,'quick_prod_id': quick_id})
                    print"prod_id",prod_id
    
    def set_stock(self, qty, product_id):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        stock_inventory_line_obj=request.env['stock.inventory.line']
        stock_inventory_obj=request.env['stock.inventory']
        pro_obj=request.env['product.product']
        location_obj=request.env['stock.location']
        print "=================product_id=================",product_id
        inventory_id = stock_inventory_obj.create({'name':'update stock'+' '+str(datetime.now())})
        inventory_id.prepare_inventory()
        # product_data=pro_obj.browse(cr,SUPERUSER_ID,product_id)
        location_ids = location_obj.search([('name','=','Stock'),('usage','=','internal')])
        print"location_ids",location_ids
        vals={
            'inventory_id':inventory_id.id,
            'location_id':location_ids.id and location_ids[0].id or False,
            'product_id':product_id.id,
            'product_uom_id':product_id.product_tmpl_id.uom_id.id,
            'product_qty':qty
        }
        print"===vals==>>>>>",vals
        stock_inventory_line_obj.create(vals)
        inventory_id.action_done()
        return True
        
    
    
    
    def get_invoice(self, tag):
        
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        tax_orm = request.env['account.tax']
        # shop_orm = request.env['sale.shop']
        # payinvoice_orm = request.env['pay.invoice']
        invoice_orm = request.env['account.invoice']
        partner_obj = request.env['res.partner']
        cmpany_obj = request.env['res.company']
        comapny_ids = cmpany_obj.search([])
        product_orm = request.env['product.product']
        product_categ_obj = request.env['product.category']
        invoice_line_obj = request.env['account.invoice.line']
#        shop_id = shop_orm.search(cr,SUPERUSER_ID,[('sale_channel_shop','=',False)])
#        shop_data = shop_orm.browse(cr,SUPERUSER_ID,shop_id[0])
        invoice_i = []
        for node in tag:
            logger.error('++++tag+++++++++++++ %s',node.toprettyxml())
            invoices = {}
            invoice_line = []
            tax_id = False
            for cNode in node.childNodes:
                if cNode.nodeName == 'Id':
                    invoices.update({'quick_invoice_id': cNode.childNodes[0].data})
                if cNode.nodeName == 'CustomerRef':
                    invoices.update({'partner_id': cNode.childNodes[0].data})
                    partner_name = cNode.childNodes[0].data
                if cNode.nodeName == 'CurrencyRef':
                    invoices.update({'currency_id': cNode.childNodes[0].data})
                if cNode.nodeName == 'Balance':
                    invoices.update({'residual': cNode.childNodes[0].data})
                if cNode.nodeName == 'TotalAmt':
                    invoices.update({'ammount_total': cNode.childNodes[0].data})
                if cNode.nodeName == 'MetaData':
                    for child_node in cNode.childNodes:
                        if child_node.nodeName == 'CreateTime':
                            invoices.update({'date_invoice': child_node.childNodes[0].data})
                if cNode.nodeName == 'TxnTaxDetail':
                    for child_node in cNode.childNodes:
                        if child_node.nodeName == 'TotalTax':
                            invoices.update({'amount_tax': child_node.childNodes[0].data})
                        if child_node.nodeName == 'TxnTaxCodeRef':
                            tax_code= child_node.childNodes[0].data
                            invoices.update({'tax_code': child_node.childNodes[0].data})

                if cNode.nodeName == 'BillEmail':
                    for child_node in cNode.childNodes:
                        if child_node.nodeName == 'Address':
                            email = child_node.childNodes[0].data

                if cNode.nodeName == 'Line':
                    line = {}
                    for child_node in cNode.childNodes:
                        if child_node.nodeName == 'Description':
                            line.update({'name': child_node.childNodes[0].data})
                        if child_node.nodeName == 'SalesItemLineDetail':
                            for child_node1 in child_node.childNodes:
                                if child_node1.nodeName == 'ItemRef':
                                    line.update({'product_id': child_node1.childNodes[0].data})
                                if child_node1.nodeName == 'Qty':
                                    line.update({'quantity': child_node1.childNodes[0].data})
                                if child_node1.nodeName == 'UnitPrice':
                                    line.update({'price_unit': child_node1.childNodes[0].data})
                                if child_node1.nodeName == 'TaxCodeRef':
                                    line.update({'invoice_line_tax_id': child_node1.childNodes[0].data})
#                        if child_node.nodeName == 'Amount':
#                            line.update({'invoice_line_tax_id': child_node.childNodes[0].data})
                        
                    invoice_line.append(line)
                    invoices.update({'lines':invoice_line})
            invoice_i.append(invoices)
        print"invoice",invoice_i
        
        for invoice in invoice_i:
            logger.error('++++invoice+++++++++++++ %s',invoice)
            invoice_ids = invoice_orm.search( [('quick_invoice_id','=',invoice.get('quick_invoice_id'))])
            if not invoice_ids:
                logger.error('+++invoice.get(partner_id)++++++++++ %s',invoice.get('partner_id'))
                partner_quick_id = int(invoice.get('partner_id'))
                logger.error('++++partner_quick_id+++++++++++++ %s',partner_quick_id)
                partner_id = partner_obj.search(  [('quick_id','=',partner_quick_id)])
                # if not partner_id:
                #     vals = {
                #         'name' : partner_name,
                #         'email':email
                #     }
                #     partner_id = partner_obj.create(vals)

                print"partner_id",partner_id
                logger.error('++++partner_id+++++++++++++ %s',partner_id)
                # user_data=partner_obj.browse(cr,SUPERUSER_ID,partner_id)
                print"partner_id",partner_id.name
#                logger.error('++++user_data.name+++++++++++++ %s',user_data.name)
#                logger.error('++++partner_id.name+++++++++++++ %s',partner_id[0])
#                logger.error('++++partner_id.name+++++++++++++ %s',partner_id[0].name)
                journal_ids = request.env['account.journal'].search([('type', '=', 'sale'), ('company_id', '=', comapny_ids.id)],
                limit=1)
                print"invoice.get('quick_invoice_id')",invoice.get('quick_invoice_id')
                logger.error('++++partner_id+++++++++++++ %s',partner_id)

                invoice_vals = {
                        'partner_id' : partner_id.id,
                        'date_invoice' : invoice.get('date_invoice'),
                        'name': partner_id.name,
                        'state' : 'draft',
                        'type' : 'out_invoice',
                        'account_id': partner_id.property_account_receivable_id.id,
                        'journal_id': journal_ids.id,
#                                    'currency_id': invoice.get('currency_id'),
                        'company_id': comapny_ids.id,
                        'quick_invoice_id':invoice.get('quick_invoice_id'),
                        'amount_tax':invoice.get('amount_tax'),
                        'residual':invoice.get('residual'),
                        'quick_export':True
                }
                print"===>invoice_vals",invoice_vals
                tax_id = None
                if invoice.get('tax_code'):
                    logger.error('++++tax_code+++++++++++++ %s',invoice.get('tax_code'))
                    tax_ids = tax_orm.search([('quick_id','=',invoice.get('tax_code'))])
                    logger.error('++++tax_ids+++++++++++++ %s',tax_ids)
                    if len(tax_ids):
                        tax_id = [(6, 0, tax_ids)]
#                logger.error('++++invoice_vals+++++++++++++ %s',invoice_vals)
                invoice_id = invoice_orm.create(invoice_vals)
                if invoice_id:
                    for line in invoice.get('lines'):
                        print"line",line
                        if line:
                            product_ids = product_orm.search([('quick_prod_id','=',line.get('product_id'))])
                            print"product_ids",product_ids
                            print"line.get('invoice_line_tax_id')",line.get('invoice_line_tax_id')
                            invoice_line_tax_id = None
                            if line.get('invoice_line_tax_id') == 'TAX':
                                invoice_line_tax_id = tax_id 
                            if product_ids:
                                print "==============invoice_id===================",invoice_id
                                print "==============tax_id===================",tax_id
                                if not product_ids.property_account_income_id:
                                    categ_id = product_categ_obj.search([('id','=',product_ids.categ_id.id)])
                                    print "=================categ_id=========",categ_id
                                    if categ_id:
                                        account_id = categ_id.property_account_income_categ_id.id
                                        print "=======if==========account_id========", account_id
                                else:
                                    account_id = product_ids.property_account_income_id.id
                                    print "=================account_id=========", account_id

                                line_vals = {
                                    'invoice_id' : invoice_id.id,
                                    'product_id' : product_ids.id and product_ids[0].id,
                                    'name' : line.get('name') or '',
                                    'quantity' :line.get('quantity') or 0.00,
                                    'price_unit' :line.get('price_unit') or False,
                                    'invoice_line_tax_id':invoice_line_tax_id,
                                    'account_id':account_id
                                }
                                print"line_vals",line_vals
#                                logger.error('++++line_vals+++++++++++++ %s',line_vals)
                                line_id = invoice_line_obj.create(line_vals)
                                print"line_id",line_id
                    
#                    invoice_orm.button_reset_taxes(cr,SUPERUSER_ID,[invoice_id])
                    logger.error('++++line_vals+++++++++++++ %s',invoice.get('residual'))
                    if float(invoice.get('residual')) == 0.0:
#                        payinvoice_orm.pay_invoice(cr,SUPERUSER_ID,False,[invoice_id],{})
                        invoice_id.write({'paid_on_qb':True})
                    else:
                        if float(invoice.get('residual')) != float(invoice.get('ammount_total')):
                            payamount = float(invoice.get('ammount_total'))-float(invoice.get('residual'))
                            logger.error('++++import+++++++++++++ %s',payamount)
#                            payinvoice_orm.pay_invoice_someamount(cr,SUPERUSER_ID,False,[invoice_id],payamount,{})
            else:
                qb_balance = invoice.get('residual')
                # invoice_data = invoice_orm.browse(cr,SUPERUSER_ID,invoice_ids[0])
                if invoice_ids.state not in ['paid','draft','cancel']:
                    if float(qb_balance) != float(invoice_ids.residual):
                        payamount = float(invoice_ids.residual) - float(qb_balance)
                        logger.error('++++qb_balance+++++++++++++ %s',qb_balance)
                        logger.error('++++exit+++residual++++++++++ %s',invoice_ids.residual)
#                        if payamount >= 0.01:
#                            payinvoice_orm.pay_invoice_someamount(cr,SUPERUSER_ID,False,[invoice_data.id],payamount,{})
                        
                            
        return True
    
    
    def export_invoice(self,from_dt,to_dt,realmid,access_token):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        quick_config_obj = request.env['quick.configuration']
        quick_acc_obj = request.env['quick.account']
        sale_obj = request.env['sale.order']
        # pos_obj = request.env['pos.order']
        product_obj = request.env['product.product']
        config_ids = quick_config_obj.search([])
        # config_data = quick_config_obj.browse(cr,uid,config_ids)
        invoice_obj = request.env['account.invoice']
        headers = {'content-type': 'application/xml'}
        prod_data = ''
        res_obj = request.env['res.partner']
        print"from_dt=====  >",from_dt,to_dt
        fr_date = parse(from_dt)
        fr_dt_up = fr_date.strftime('%m/%d/%Y')
        to_date = parse(to_dt)
        to_dt_up = to_date.strftime('%m/%d/%Y')
        print"-fr_dt_up--------",fr_dt_up,to_dt_up
        invoice_ids = invoice_obj.search([('quick_invoice_id','=',False),('date_invoice','>=',fr_dt_up),('date_invoice','<=',to_dt_up),('state','not in',['cancel','draft'])])
        print"invoice_ids",invoice_ids
#        invoice_ids=[97]
        logger.error('++++invoice_ids+++++++++++++ %s',invoice_ids)
        for invoice_data in invoice_ids:
#            pos_id = pos_obj.search(cr,SUPERUSER_ID,[('name','=',invoice_data.origin)])
            if not invoice_data.partner_id.quick_id:
                print"invoice_data.partner_id.quick_id-------@@@@@",invoice_data.partner_id.quick_id
                print"invoice_data.partner_id.quick_id-------@@@@@",invoice_data.partner_id.quick_id
                if not invoice_data.partner_id.quick_id:
                    print'context-----------------#@@@@@@@@--------',context
                    context = request.env.context.copy()
                    context.update({'customer_ids':[invoice_data.partner_id.id]})
                    request.env.context = context
                    # self.with_context({'customer_ids': [invoice_data.partner_id.id]}).export_customer(realmid,access_token)
                    self.export_customer(realmid, access_token, context=context)
                    cr.commit()
                
            print"invoice_data",invoice_data
            headers = {'content-type': 'application/xml'}
            invoice_data_xml = ''
            line_data=''
            faulty = False
            qb_tax_code = ''
            item_id = ''
            acc_ids = ''
            acc_exp_ids = ''
            acc_asset_ids = ''
            for line in invoice_data.invoice_line_ids:
                product_data = line.product_id
                logger.error('product_data========%s',product_data)
                if not line.price_unit > 0.0 or not line.quantity >0.0:
                    continue
                print"------line.product_id.type------",line.product_id
             
               
                if not line.product_id.quick_prod_id:
                    prod_QB_id = product_obj.search([('name','=','Odoo QB Products')])
                    print"prod_QB_id===============",prod_QB_id
                    if not prod_QB_id:
                        tz = pytz.timezone("America/Toronto")
                        date = parse(product_data.create_date)
                        aware_dt = tz.localize(date)
                        cr_date = aware_dt.isoformat()
    #                    IncomeAccountRef = quick_acc_data.quick_acc_id
    #                    
    #                    if not IncomeAccountRef:
    #                        IncomeAccountRef = ''
    #                    ExpenseAccountRef = quick_acc_obj.browse(cr,SUPERUSER_ID,acc_exp_ids).quick_acc_id
    #                    if not ExpenseAccountRef:
    #                        ExpenseAccountRef = ''
    #                    AssetAccountRef = quick_acc_obj.browse(cr,SUPERUSER_ID,acc_asset_ids).quick_acc_id
    #                    if not AssetAccountRef:
    #                        AssetAccountRef = ''
    #                    print"IncomeAccountRef================",IncomeAccountRef
                        if not product_data.property_account_income_id:
                            print"product_data.property_account_income_id",product_data.property_account_income_id
                            acc_ids = quick_acc_obj.search([('acc_id','=',product_data.categ_id.property_account_income_categ_id.id)])
                        else:
                            print"product_data.property_account_income_id",product_data.property_account_income_id.id
                            print"product_data.property_account_income_id.id",product_data.property_account_income_id.id
                            acc_ids = quick_acc_obj.search([('acc_id','=',product_data.property_account_income_id.id)])
                        print"acc_ids",acc_ids
                        # quick_acc_data = quick_acc_obj.browse(cr,SUPERUSER_ID,acc_ids)
                        prod_data += """<Item xmlns="http://schema.intuit.com/finance/v3" sparse="false">
                                        <Name>Odoo QB Products</Name>
                                        <IncomeAccountRef >%s</IncomeAccountRef>
                                        <PurchaseCost>%s</PurchaseCost>
                                        <Type>Service</Type>
                                        <TrackQtyOnHand>false</TrackQtyOnHand>,
                                    </Item>"""% (acc_ids.quick_acc_id,product_data.lst_price)
                        getresource = config_ids.url+config_ids.company+'/item'
                        r = oauth.post(getresource,data = prod_data,headers=headers)
                        logger.error('++++prod_data+++++++++++++ %s',prod_data)
                        logger.error('++++r.status_code+++++++++++++ %s',r.status_code)
                        logger.error('++++r.content+++++++++++++ %s',r.content)
                        print"r========>",r.content
                        if r.status_code==200:
                            data = r.content
                            responseDOM = parseString(data)
                            tag = responseDOM.getElementsByTagName('Item')
                            quick_id = False
                            for node in tag:
                                for cNode in node.childNodes:
                                    if cNode.nodeName == 'Id':
                                        quick_id = cNode.childNodes[0].data
                                        print"quick_id",quick_id
                            if quick_id:
                                prod_id = product_data.write({'quick_export' : True,'quick_prod_id': quick_id})
                                cr.commit()
                                product_id = product_obj.create({ 'name': 'Odoo QB Products', 'quick_export' : True,'quick_prod_id': quick_id })
                                print"prod_id",prod_id
                                item_id = quick_id
                    else:
                        item_id = prod_QB_id.quick_prod_id
                else:
                    item_id =   line.product_id.quick_prod_id    
                line_data += """ <Line>
                                <Description>%s</Description>
                                <Amount>%s</Amount>
                                <DetailType>SalesItemLineDetail</DetailType><SalesItemLineDetail>"""%(line.name,line.price_subtotal)
                if len(line.invoice_line_tax_ids):
                    line_data +="""<TaxCodeRef>TAX</TaxCodeRef>"""
                    if qb_tax_code == '':
                        qb_tax_code = line.invoice_line_tax_ids.quick_id
                
                line_data += """
                            <ItemRef>%s</ItemRef>
                            <UnitPrice>%s</UnitPrice>
                            <Qty>%s</Qty>
                          </SalesItemLineDetail>
                        </Line> """% (item_id,line.price_unit,line.quantity)
            print'-----faulty-----',faulty
            if faulty:
                break
            po_number = False    
#            if len(pos_id):
#                partner_quick_id = 834 # web customer
#                po_number = invoice_data.origin
#            else:
#                partner_quick_id = 821 # web customer
                
#            cr.execute("""select order_id from sale_order_line_invoice_rel where invoice_id=%s""", (invoice_data.id,))
#            order_id = [i[0] for i in cr.fetchall()]
#            custome_data = ''
#            if len(order_id):
#                sale_data = sale_obj.browse(cr,SUPERUSER_ID,order_id[0])
#                if not sale_data.shop_id.sale_channel_shop:
#                    partner_quick_id = invoice_data.partner_id.quick_id
#                else:
#                    if sale_data.unique_sales_rec_no:
#                        po_number = str(invoice_data.partner_id.name)+' / '+str(sale_data.unique_sales_rec_no)
#            if invoice_data.partner_id.group_id.name == 'Wholesale':
#                partner_quick_id = invoice_data.partner_id.quick_id
#            if po_number:
#                custome_data +="""<CustomField>
#                    <DefinitionId>1</DefinitionId>
#                    <Name>P.O. Number</Name>
#                    <Type>StringType</Type>
#                    <StringValue>%s</StringValue>
#                    </CustomField>"""% (po_number)
                        
#            7 = Labour -- 0%
#            8 = Tax Sales CA - 8.25% -- 8.25%
#            13 = Tax Sales CA - 8.0% -- 8.0%
            print"invoice_data.partner_id.quick_id========",invoice_data.partner_id.quick_id
            invoice_data_xml += """<Invoice xmlns="http://schema.intuit.com/finance/v3">"""\
                                +line_data+"""<CustomerRef>%s</CustomerRef></Invoice>"""% (invoice_data.partner_id.quick_id)
            print"=invoice_data=========>",invoice_data
#            getresource = 'https://sandbox-quickbooks.api.intuit.com/v3/company/193514292321532/invoice'
#             getresource = config_ids.url+config_ids.company+'/invoice'
#             getresource = config_ids.url+'/invoice'

            print"invoice_data_xml",invoice_data_xml


            getresource = 'https://sandbox-quickbooks.api.intuit.com/v3/company/' + realmid + '/invoice?minorversion=4'


            invoice_data_xml = invoice_data_xml.encode('utf-8')
            auth_header = 'Bearer {0}'.format(access_token)
            print"auth_header====>", auth_header
            headers = {
                'Authorization': auth_header,
                 'Accept': 'application/xml',
                 'content-type': 'application/xml'
            }
            r = requests.post(getresource,data = invoice_data_xml,headers=headers)
            # r = oauth.post(getresource,data = invoice_data_xml,headers=headers)
            logger.error('++++r.status_code+++++++++++++ %s',r.status_code)


            print"r&s========>", r.status_code

            print"r========>",r.content
            if r.status_code==200:
                data = r.content
                responseDOM = parseString(data)
                tag = responseDOM.getElementsByTagName('Invoice')
                quick_id = False
                for node in tag:
                    for cNode in node.childNodes:
                        if cNode.nodeName == 'Id':
                            quick_id = cNode.childNodes[0].data
                            print"quick_id",quick_id
                if quick_id:
                    inv_id = invoice_data.write({'quick_export' : True,'quick_invoice_id': quick_id})
                    print"inv_id",inv_id












#            invoice_data_xml += """<Invoice xmlns="http://schema.intuit.com/finance/v3">"""+line_data+custome_data+"""<CustomerRef>%s</CustomerRef><TxnTaxDetail><TxnTaxCodeRef>%s</TxnTaxCodeRef><TotalTax>%s</TotalTax></TxnTaxDetail></Invoice>"""% (partner_quick_id,qb_tax_code,invoice_data.amount_tax)
#            print"=invoice_data=========>",invoice_data
#            logger.error('++++invoice_data_xml+++++++++++++ %s',invoice_data_xml)
#            getresource = config_data.url+config_data.company+'/invoice'
#            print"invoice_data_xml",invoice_data_xml
#            r = oauth.post(getresource,data = invoice_data_xml,headers=headers)
#            logger.error('++++r.status_code+++++++++++++ %s',r.status_code)
#            logger.error('++++r.content+++++++++++++ %s',r.content)
#            print"r========>",r.content
#            data = r.content
#            responseDOM = parseString(data)
#            print'responseDOM.toprettyxml()--------', responseDOM.toprettyxml()
#            quick_id = False
#            if r.status_code==200:
#                tag = responseDOM.getElementsByTagName('Invoice')
#                
#                for node in tag:
#                    for cNode in node.childNodes:
#                        if cNode.nodeName == 'Id':
#                            quick_id = cNode.childNodes[0].data
#                            print"quick_id",quick_id
#                if quick_id:
#                    paid_amount = 0.0
#                    if invoice_data.state == 'paid':
#                        paid_amount = invoice_data.amount_total
#                    if invoice_data.residual != invoice_data.amount_total:
#                        paid_amount = invoice_data.amount_total-invoice_data.residual
#                    
#                    if paid_amount >=0.01:    
#                        getresource = config_data.url+config_data.company+'/payment'
#                        payment_data_xml ="""<Payment xmlns="http://schema.intuit.com/finance/v3">
#                        <CustomerRef>%s</CustomerRef>
#                        <TotalAmt>%s</TotalAmt>
#                        <Line>
#                            <Amount>%s</Amount>
#                            <LinkedTxn>
#                                <TxnId>%s</TxnId>
#                                <TxnType>Invoice</TxnType>
#                            </LinkedTxn>
#                        </Line>
#                        </Payment>#"""% (partner_quick_id,invoice_data.amount_total,paid_amount,quick_id)
#                        logger.error('++++payment_data_xml+++++++++++++ %s',payment_data_xml)
#                        r = oauth.post(getresource,data = payment_data_xml,headers=headers)
#                        if r.status_code==200 and invoice_data.state == 'paid':
#                            invoice_data.write({'paid_on_qb':True})
#                    inv_id = invoice_data.write({'faulty':False,'faulty_reason':False,'quick_export' : True,'quick_invoice_id': quick_id})
#                    print"inv_id",inv_id
#                    
#            if not quick_id:
#                tag = responseDOM.getElementsByTagName('Error')
#                for node in tag:
#                    for cNode in node.childNodes:
#                        print'cNode.nodeName-----',cNode.nodeName
#                        if cNode.nodeName == 'Detail':
#                            faulty_reason = cNode.childNodes[0].data
#                print'faulty_reason-----',faulty_reason
#                invoice_data.write({'faulty' : True,'faulty_reason': faulty_reason})
#        cr.commit()        
#        unpaid_invoice_ids = invoice_obj.search(cr, SUPERUSER_ID, [('quick_invoice_id','=',True),('paid_on_qb','=',False),('state','in',['paid'])], context=context)
#        for unpaid_invoice_data in invoice_obj.browse(cr,SUPERUSER_ID,unpaid_invoice_ids):
#            if unpaid_invoice_data.state == 'paid':
##                partner_quick_id = 821 # web customer
#                cr.execute("""select order_id from sale_order_invoice_rel where invoice_id=%s""", (unpaid_invoice_data.id,))
#                order_id = [i[0] for i in cr.fetchall()]
#                if len(order_id):
#                    sale_data = sale_obj.browse(cr,SUPERUSER_ID,order_id[0])
#                    if not sale_data.shop_id.sale_channel_shop:
#                        partner_quick_id = unpaid_invoice_data.partner_id.quick_id
#                        if not partner_quick_id:
#                            context.update({'customer_ids':[unpaid_invoice_data.partner_id.id]})
#                            self.export_customer()
#                            cr.commit()
#                            partner_quick_id = unpaid_invoice_data.partner_id.quick_id
#                            
#                getresource = config_data.url+config_data.company+'/payment'
#                payment_data_xml ="""<Payment xmlns="http://schema.intuit.com/finance/v3">
#                <CustomerRef>%s</CustomerRef>
#                <TotalAmt>%s</TotalAmt>
#                <Line>
#                    <Amount>%s</Amount>
#                    <LinkedTxn>
#                        <TxnId>%s</TxnId>
#                        <TxnType>Invoice</TxnType>
#                    </LinkedTxn>
#                </Line>
#                </Payment>#"""% (partner_quick_id,unpaid_invoice_data.amount_total,unpaid_invoice_data.amount_total,unpaid_invoice_data.quick_invoice_id)
#                logger.error('++++payment_data_xml+++++++++++++ %s',payment_data_xml)
#                r = oauth.post(getresource,data = payment_data_xml,headers=headers)
#                if r.status_code==200:
#                    unpaid_invoice_data.write({'paid_on_qb':True})
        
    

      
      
        
       
        
    
