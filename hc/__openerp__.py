# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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


{
	'name': 'HealthCare Information System',
	'version': '1.0.0',
	'category': 'HealthCare',
	'summary': 'HealthCare Information System',
	'depends': ['base', 'product','account_voucher', 'hr'],
	'author': 'Metwalli',
	'website': 'https://www.odoo.com',
	'summary': 'Patients, Patient Invoices, Memos',
	'sequence': 9,
    'data':[
        'views/account_invoice_view.xml',
        'views/hc_view.xml',
        'views/hc_patient_view.xml',
        'views/hc_service_order_sequence.xml',
        'views/hc_service_order_view.xml',
        'views/hc_patient_sequence.xml',
        'views/hc_service_order_workflow.xml',
        'report/hc_service_order_report_view.xml',
        #'security/hc_security.xml',
        #'security/ir.model.access.csv',
    ],
    'description': """
This module allows to Manage HealthCare Operations inside Odoo
=================================================================

Use This Module to make the following:
- Create Patients.
- Patient Invoices.
- Patient Refunds.
- Patient Payments.

HealthCare can be found in the 'HealthCare' menu.
""",
	'installable': True,
	'application':True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
