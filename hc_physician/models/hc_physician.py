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
from openerp import fields, api, models, _
from openerp.exceptions import UserError
from openerp.tools.translate import _



class HCDiagnosis(models.Model):
    _name = 'hc.diagnosis'

    code = fields.Char('Diagnosis Code')
    name = fields.Text('Diagnosis Name', required=True)
    

    # TODO Create Invoice for Prescription Services List(Done)
    # TODO Complete Prescription States (Done)
    # TODO: Complete consultation Plan (Done)
    # TODO change consultation state to closed depends on consultation plan
    # TODO: add interface for prescription orders, which shows lab report,... (Done)
    # TODO: Drugs order
    # TODO: Create Templates Module in separately file Case sheet Templates
class HCPhysicianConsultationOrder(models.Model):
    _name = "hc.physician.consultation.order"
    _inherits = {
        'hc.service.order.line': 'service_line_id'
    }
    _order = 'request_date desc'
    _description = 'Doctor Consultation'
    
    service_line_id = fields.Many2one('hc.service.order.line', 'Order Line', required=True, readonly=True, ondelete= 'restrict')
    consultation_id = fields.Many2one('hc.consultation', 'Consultation', required=True, readonly=True, states={'draft': [('readonly', False)]})
    doctor_id = fields.Many2one('resource.resource', related='consultation_id.doctor_id', string='Doctor')
    user_id = fields.Many2one('res.users', related='consultation_id.user_id', string='Login ID')
    case_sheet_ids = fields.One2many('hc.physician.case_sheet', 'consultation_order_id', 'Case Sheet')
    request_date = fields.Datetime('Request Date', readonly=True)
    visited_date = fields.Datetime(related='case_sheet_ids.sheet_date', string='Visited Date', readonly=True)
    visit_type = fields.Selection([('first_visit', 'First Visit'), ('follow_up', 'Follow Up')], string='Visiting Type', required=True,
                                   help='this field show consultation type(First Visit or Follow up Visit), depending on consultation follow up plan \
                                        \nif type follow up must has parent')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('new', 'New'),
        ('visited', 'Visited'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
        ], string='State', default= 'draft')

    @api.multi
    def write(self, vals):
        if self.state == 'new':
            if 'case_sheet_ids' in vals and vals['case_sheet_ids']:
                vals['state'] = 'visited'
        return super(HCPhysicianConsultationOrder, self).write(vals)

    @api.multi
    def get_parent_id(self, line_id):
        last_order_ids = self.search([('service_line_id', '=', line_id)])
        return last_order_ids[0]

#TODO: Control case sheet period in the Consultation order
class HCPhysicianCaseSheet(models.Model):
    _name = "hc.physician.case_sheet"

    _description = 'Case Sheet'

    consultation_order_id = fields.Many2one('hc.physician.consultation.order', string="Consultation Order")
    patient_id = fields.Many2one('hc.patient', related= 'consultation_order_id.patient_id', string='Patient', readonly=True)
    doctor_id = fields.Many2one('resource.resource', related= 'consultation_order_id.doctor_id', string='Doctor', readonly=True)
    provisional_diagnosis_ids = fields.Many2many('hc.diagnosis', 'hc_physician_case_sheet_provisional_diagnosis_rel', 'case_sheet_id', 'diagnosis_id', string='Provisional Diagnosis', required=True)
    provisional_desc = fields.Text('Description')
    final_diagnosis_ids = fields.Many2many('hc.diagnosis', 'hc_physician_case_sheet_final_diagnosis_rel', 'case_sheet_id', 'diagnosis_id', string='Final Diagnosis')
    final_desc = fields.Text('Description')
    sheet_date = fields.Datetime('Case Sheet Date', readonly=True, default=fields.Datetime.now())
    examination_ids = fields.One2many('hc.service.order', 'case_sheet_id', string='Examinations')
    drug_order_ids = fields.One2many('hc.service.order', 'case_sheet_id', 'Drug Order')
    history = fields.Text('History')
    food_allergies = fields.Text('Food Allergies')
    drug_allergies = fields.Text('Drug Allergies')
    other_allergies = fields.Text('Other Allergies')
    chief_complaints = fields.Text('Chief Complaints')
    systemic_review = fields.Text('Systemic Review')

    @api.multi
    @api.model
    def create_examination(self):
        ServiceOrder = self.env['hc.service.order']
        draft_service_orders = ServiceOrder.search([('case_sheet_id', '=', self.id), ('state', '=', 'draft')])
        if draft_service_orders:
            raise UserError(_('You cannot Create New Examination order, while you have another in Draft State.'))
        ServiceOrder.create({
            'patient_id': self.patient_id.id,
            'doctor_id': self.doctor_id.id,
            'case_sheet_id': self.id
        })
