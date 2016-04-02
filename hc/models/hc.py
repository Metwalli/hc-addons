# -*- coding: utf-8 -*-
# /#############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2004-TODAY Tech-Receptives(<http://www.techreceptives.com>)
#    Special Credit and Thanks to Thymbra Latinoamericana S.A.
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
#/#############################################################################
from datetime import datetime
from openerp import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'
    service_type = fields.Selection([
            ('consultation', 'Consultation'),
            ('lab_test', 'Laboratory Test'),
            ('rad_test', 'Radiology Test'),
            ('procedure', 'Procedure'),
            ('operation', 'Operation'),
            ('ward', 'Ward')
            ], string='Service Type')

class ResourceResource(models.Model):
    _inherit = 'resource.resource'
    is_doctor = fields.Boolean('Is a Doctor')

class HCConsultationVisitingPlanSequence(models.Model):
    _name = 'hc.consultation.visiting.plan.sequence'
    _description = 'Visiting Plan Sequence'

    name = fields.Char('Name', size=200, required=True )
    sequence = fields.Integer('Sequence' )
    no_of_days = fields.Integer('No of Days', required=True )
    discount = fields.Float('Discount %' )
    plan_id = fields.Many2one('hc.consultation.visiting.plan', 'Visiting Plan' )
    note = fields.Char('Note', size=150 )


class HCConsultationVisitingPlan(models.Model):
    _name = 'hc.consultation.visiting.plan'
    _description = 'Visiting Plan'

    name = fields.Char('Description', size=200, required=True)
    sequence_ids = fields.One2many('hc.consultation.visiting.plan.sequence', 'plan_id', 'Plan Sequence')

class HCConsultation(models.Model):
    _name = 'hc.consultation'

    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, domain=[('is_doctor', '=', True)])
    doctor_id = fields.Many2one('resource.resource', related='employee_id.resource_id', string='Doctor', readonly=True)
    user_id = fields.Many2one('res.users', related='employee_id.user_id', string='Login ID', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', required=True, domain=[('service_type', '=', 'consultation')])
    plan_id = fields.Many2one('hc.consultation.visiting.plan', 'Visiting Plan')

    _sql_constraints = [
        ('product_doctor_uniq', 'unique (employee_id, product_id)', 'The Product must be unique per Doctor!' ),
    ]


#TODO: when add doctor on doctors send is_doctor= True (Done)