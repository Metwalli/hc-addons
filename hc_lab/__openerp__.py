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
	'name': 'HC Laboratory System',
	'version': '1.0.0',
	'category': 'HealthCare',
	'summary': 'HC Laboratory System',
	'depends': ['hc'],
	'description': """
This module allows to Manage Laboratory Operations inside Odoo
=================================================================

Use This Module to make the following:
- Create New Laboratory Test as Products.
- Create Components for the Test, Enter the Normal Ranges and Default Values for specified Component.
- Create Test Order for specified Patient.
- Show Test Order which ordering on Sale Application.
- Enter Results for ordering Tests and Printing it.

Laboratory can be found in the 'Open HIS' menu.
""",
	'author': 'Open HIS',
	'website': 'https://www.odoo.com',
	'summary': 'Laboratory Test Configuration, Test Orders',
	'sequence': 3,
    'data':[
        'views/hc_lab_view.xml',
        #'views/hc_lab_report.xml',
        'views/hc_lab_test_order_workflow.xml',
        #'views/report_lab_test_order_results.xml',
        'views/lab_order_sequence.xml',
        #'security/hc_lab_security.xml',
        #'security/ir.model.access.csv'
        ],
	'installable': True,
	'application':True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
