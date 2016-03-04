# -*- coding: utf-8 -*-
#__author__ = 'Metwalli'

from openerp import fields, api, models, _
from openerp.exceptions import UserError
from openerp.tools.translate import _

class HCServiceOrder(models.Model):
    _inherit = "hc.service.order"

    case_sheet_id = fields.Many2one('hc.physician.case_sheet', 'Case Sheet', readonly=True, ondelete='restrict')
    lab_test_ids = fields.One2many('hc.service.order.line', 'order_id', domain=[('product_id.service_type', '=', 'lab_test')], readonly=True, states={'draft': [('readonly', False)]}, string="Laboratory Tests")
    rad_test_ids = fields.One2many('hc.service.order.line', 'order_id', domain=[('product_id.service_type', '=', 'rad_test')], readonly=True, states={'draft': [('readonly', False)]}, string="Radiology Test")
    procedure_ids = fields.One2many('hc.service.order.line', 'order_id', domain=[('product_id.service_type', '=', 'procedure')], readonly=True, states={'draft': [('readonly', False)]}, string="Procedures")

    @api.multi
    def _check_contains_physician_consultation(self):
        for service_line in self.order_line_ids:
            if service_line.product_id.service_type == 'consultation' and service_line.state in ('confirmed', 'invoiced'):
                return True
        return False

    @api.multi
    @api.model
    def action_create_consultation_order(self):
        ConsultationOrder = self.env['hc.physician.consultation.order']
        for service_line in self.order_line_ids:
            if service_line.product_id.service_type == 'consultation' and service_line.state in ('confirmed', 'invoiced'):
                consultation_order_id = ConsultationOrder.search([('service_line_id', '=', service_line.id)])
                if not consultation_order_id:
                    consultation_ids = self.env['hc.consultation'].search([('product_id', '=',service_line.product_id.id )])
                    if not consultation_ids:
                        raise UserError(_('Cannot find the Consultation, Please define Consultation for this product: "%s".') % \
                                        (service_line.product_id.name))
                    parent= False
                    if service_line.is_follow_up:
                        visit_type = 'follow_up'
                    else:
                        visit_type= 'first_visit'
                    ConsultationOrder.create({
                        'service_line_id': service_line.id,
                        'consultation_id': consultation_ids[0].id,
                        'visit_type': visit_type,
                        'request_date': fields.Datetime.now(),
                        'state': 'new',
                    })
