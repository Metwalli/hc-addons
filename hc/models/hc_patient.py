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
from openerp.exceptions import UserError

#TODO compute age field depending on dob field (Done)
#TODO: Show blood Group in the view(Done)
#TODO: Security for HealthCare Modules

class ResPartner(models.Model):
    _inherit = 'res.partner'

    patient_ids = fields.One2many('hc.patient', 'partner_id', 'Patients')

#Todo: add latest Service Order in Patient view(Done)
#Todo: make patients Menu the default when open Healthcare
class HCPatient(models.Model):
    _name = 'hc.patient'
    _inherits = {
        'res.partner': 'partner_id',
    }

    @api.one
    @api.depends('dob')
    def _compute_age(self):
        if self.dob:
            current_date = fields.Date.from_string(fields.Date.today())
            dob = fields.Date.from_string(self.dob)
            diff_date = current_date - dob
            age = diff_date.days / 365
            self.age = age
        else:
            self.age = 0

    @api.multi
    def _compute_patient_type(self):
        for patient in self:
            if patient.age <= 50:
                if patient.age <= 18:
                    if patient.age <= 5:
                        patient.patient_type = 'infant'
                    else:
                        patient.patient_type = 'children'
                else:
                    patient.patient_type = 'adult'
            else:
                patient.patient_type = 'aged'

    @api.model
    def create(self, vals):
        vals['name'] = vals['first_name'] + ' ' + str(vals['middle_name']).replace('False','') + ' ' + vals['last_name']
        vals['uhid'] = self.env['ir.sequence'].next_by_code('hc.patient')
        result = super(HCPatient, self).create(vals)
        return result

    @api.multi
    def write(self, vals):

        vals['name'] = str(vals['first_name'] if 'first_name' in vals else self.first_name).replace('False', '')
        vals['name'] = vals['name'] + ' ' + str(vals['middle_name'] if 'middle_name' in vals else self.middle_name).replace("False", "")
        vals['name'] = vals['name'] + ' ' + str(vals['last_name'] if 'last_name' in vals else self.last_name).replace("False", "")

        res = super(HCPatient, self).write(vals)
        return res

    first_name = fields.Char('First Name', size=30, required=True, translate=True)
    middle_name = fields.Char('Middle Name', size=30,  translate=True)
    last_name = fields.Char('Last Name', size=30, required=True, translate=True)
    partner_id = fields.Many2one('res.partner', 'Related Partner', translate=True, required=True, ondelete='cascade',
                                  help='Partner-related data of the patient')
    photo = fields.Binary(string='Picture')
    gender = fields.Selection([('Male', 'Male'), ('Female', 'Female'),('Unknown', 'Unknown'), ], string='Gender', required=True)
    blood_type = fields.Selection([('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O'), ], string='Blood Type')
    rh = fields.Selection([('+', '+'), ('-', '-'), ], string='Rh')
    general_info = fields.Text(string='General Information', help='General information about the patient')
    allergies = fields.Text(string='Allergies', help='Write allergies, may be effect of the patient like Foods, Drink or Drugs ...')
    current_address = fields.Many2one('res.partner', string='Address', help='Contact information.')
    state = fields.Selection([
        ('out_patient', 'Out Patient'),
        ('in_patient', 'In Patient'),
        ('blocked', 'Blocked'),
        ('deceased', 'Deceased')
    ], string='Patient State', default='out_patient', required=True)
    ssn = fields.Char(size=256, string='SSN')
    dob = fields.Date(string='Date of Birth')
    age = fields.Integer(string='Age', readonly= True, compute='_compute_age', store=True)
    patient_type = fields.Char(compute='_compute_patient_type', string='Patient Type',
                               help='compute patient depends on age (children, infants, aged,...)')
    marital_status = fields.Selection([('s', 'Single'),
                                        ('m', 'Married'),
                                        ('w', 'Widowed'),
                                        ('d', 'Divorced'),
                                        ('u', 'Unknown')
                                        ],string='Marital Status', sort=False)
    dod = fields.Datetime(string='Date of Death', readonly=True, states={'deceased': [('readonly', False)]})
    uhid = fields.Char(string='UHID', readonly=True,
                        help='Patient Identifier provided by the Healthcare Center')

    @api.multi
    @api.onchange('state')
    def onchange_state(self):
        if(self.state == 'deceased'):
            return self.update({'dod': fields.Datetime.now()})

    @api.multi
    def get_patient(self, partner_id):
        patient = self.search(['partner_id', '=', partner_id])
        return patient

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
