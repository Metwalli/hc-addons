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
	'name': 'Physician Module',
	'version': '1.0.0',
	'category': 'HealthCare',
	'summary': 'Physician System',
	'depends': ['hc'],
	'description': """
This module allows Doctors to Manage their Clinic inside Odoo
=================================================================

Use Physician to Request Doctor Consultation and Store all Operations which applying to specified Patient
  in the Patients Folder (Medical Record)
  On this Module Doctor can make the following:
  - Store Patient Diagnosis.
  - Request Laboratory Tests.
  - Request Radiology Tests.
  - Request Procedures.
  - Request Drugs.

Clinic Application in the 'Open HIS' menu.
""",
	'author': 'Open HIS',
	'website': 'https://www.odoo.com',
	'summary': 'Clinic Config, Doctors, Consultation Request',
	'sequence': 9,
    'data':[
        'views/hc_physician_view.xml',
        'views/hc_service_order_workflow.xml',
        #'security/hc_physician_security.xml',
        #'security/ir.model.access.csv',
        ],
	'installable': True,
	'application':True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
