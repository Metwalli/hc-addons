# -*- coding: utf-8 -*-
#__author__ = 'Metwalli'

from datetime import datetime
from openerp import api, fields, models, _
from openerp.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    doctor_id = fields.Many2one('resource.resource', 'Doctor', domain=[('is_doctor', '=', True)], readonly=True, states={'draft': [('readonly', False)]})
    order_id = fields.Many2one('hc.service.order', 'Service Order', readonly=True, ondelete='restrict', states={'draft': [('ondelete', 'cascade')]}, copy=False)

    @api.multi
    def check_invoice_constraints(self, vals):
        if 'invoice_line_ids' in vals:
            if len(vals['invoice_line_ids']) > 1:
                for line in vals['invoice_line_ids']:
                    if self.env['product.product'].browse([line[2]['product_id']]).service_type == 'consultation':
                        return False
        return True

    @api.model
    def create(self, vals):
        if not self.check_invoice_constraints(vals):
            raise UserError(_('Cannot Save this Invoice, The Consultation must be independent'))
        else:
            return super(AccountInvoice, self).create(vals)

    @api.multi
    def invoice_contains_healthcare_service(self):
        services_list = ['consultation', 'lab_test', 'rad_test', 'procedure', 'operation', 'ward']
        for line in self.invoice_line_ids:
            if line.product_id.type == 'service' and line.product_id.service_type in services_list:
                return True
        return False

    @api.multi
    def _get_invoice_details(self, lines):
        patient = self.env['hc.patient'].search([('partner_id', '=', self.partner_id.id)])
        res = {
            'patient_id': patient.id,
            'doctor_id': self.doctor_id.id,
            'order_date': fields.Datetime.now(),
            'order_line_ids': [(6, 0, lines)],
            'state': 'progress',
            'auto_order': True,
        }
        return res

    @api.multi
    @api.model
    def action_create_service_order(self):
        self.ensure_one()
        services_list = {'consultation', 'lab_test', 'rad_test', 'procedure', 'operation', 'ward'}
        ServiceOrder = self.env['hc.service.order']
        if not self.order_id:
            created_lines = []
            for line in self.invoice_line_ids:
                if not line.order_line_id and line.product_id.type == 'service' and line.product_id.service_type in services_list:
                    line_id = line.action_create_order_line()
                    created_lines.append(line_id)
            vals = self._get_invoice_details(created_lines)
            order_id = ServiceOrder.create(vals)
            self.write({'order_id': order_id.id})

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    order_line_id = fields.Many2one('hc.service.order.line', 'Service Order Line', readonly=True, copy=False)
    order_id = fields.Many2one('hc.service.order', related='order_line_id.order_id', string= 'Service Order', readonly=True)

    @api.multi
    def _prepare_order_line(self):
        res = {
            'product_id': self.product_id.id,
            'name': self.product_id.name,
            'product_uom_id': self.uom_id.id,
            'product_uom_qty': self.quantity,
            'state': 'invoiced'
        }
        return res

    @api.multi
    @api.model
    def action_create_order_line(self):
        OrderLine = self.env['hc.service.order.line']
        vals = self._prepare_order_line()
        if vals:
            line_id = OrderLine.create(vals)
            self.write({'order_line_id': line_id.id})
        return line_id.id

