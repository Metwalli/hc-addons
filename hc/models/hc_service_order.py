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


#TODO show the invoices only for patient in Patients invoices list
#TODO: Show Patient Record Folder which contain List of services orders to the patient

#TODO: when add doctor on doctors send is_doctor= True (Done)
#TODO: Complete Security to show own and doctors orders

class HCServiceOrder(models.Model):
    _name = 'hc.service.order'
    _order = 'order_no desc,order_date desc'

    @api.multi
    def _compute_invoiced(self):
        for service_order in self:
            service_order.invoiced = True
            if service_order.state not in('draft', 'cancel') and len(service_order.order_line_ids) > 0:
                for line in service_order.order_line_ids:
                    if line.state != 'cancel' and (not line.invoiced):
                        service_order.invoiced = False
                        break
            else:
                service_order.invoiced = False

    name = fields.Char('Description', translate=True, required=True, default= 'draft order', copy=False, readonly=True, states={'draft': [('readonly', False)]})
    order_no = fields.Char('Order No', translate=True, size=20, readonly=True)
    patient_id = fields.Many2one('hc.patient', 'Patient Name', required=True, readonly=True, states={'draft':[('readonly', False)]})
    doctor_id = fields.Many2one('resource.resource', 'Doctor', domain=[('is_doctor', '=', True)], readonly=True, states={'draft': [('readonly', False)]})
    order_date = fields.Datetime('Order Date', readonly=True)
    order_line_ids = fields.One2many('hc.service.order.line', 'order_id', string='Order Lines', readonly=True, states={'draft':[('readonly', False)]})
    product_id = fields.Many2one('product.product', related='order_line_ids.product_id', string='Product')
    invoice_ids = fields.One2many('account.invoice', 'order_id', 'Invoices', readonly=True, copy=False, help="This is the list of invoices that have been generated for this sales order. The same service order may have been invoiced in several times (by line for example).")
    invoiced = fields.Boolean(compute='_compute_invoiced', string='Paid', help="It indicates that an invoice has been paid.")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('to_invoice', 'To Invoice'),
        ('progress', 'In Progress'),
        ('invoice_except', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ], string='Status', default= 'draft')
    auto_order = fields.Boolean('Auto Generating Order', default=False)
    note = fields.Text('Notes')
    user_id = fields.Many2one('res.users', 'User', readonly=True, default=lambda self: self.env.user, states={'draft': [('readonly', False)]})

    @api.multi
    def _check_order_constraints(self, vals):
        if 'order_line_ids' in vals:
            if len(vals['order_line_ids']) > 1:
                for line in vals['order_line_ids']:
                    if self.env['product.product'].browse([line[2]['product_id']]).service_type == 'consultation':
                        return False
        return True

    @api.multi
    def _check_is_free_follow_up(self):
        rec = self.get_consultation_follow_up()
        if rec:
            if rec['discount'] == 100:
                return True
        else:
            return False


    @api.model
    def create(self, vals):
        if not self._check_order_constraints(vals):
            raise UserError(_('Cannot Save this Order, The Consultation must independent order'))
        if 'auto_order' in vals and vals['auto_order']:
            vals['order_no'] = self.env['ir.sequence'].next_by_code('hc.service.order')
            vals['name'] = vals['order_no']
        return super(HCServiceOrder, self).create(vals)

    @api.multi
    def write(self, vals):
        if not self._check_order_constraints(vals):
            raise UserError(_('Cannot Save this Order, The Consultation must independent order'))
        return super(HCServiceOrder, self).write(vals)
#Consultation Orders

    @api.multi
    def action_set_state(self, value):
        self.ensure_one()
        self.write({'state': value})

    @api.multi
    def action_button_confirm(self):
        self.signal_workflow('order_confirm')
        return True

    @api.multi
    def action_wait(self):
        self.ensure_one()
        if not any(line.state != 'cancel' for line in self.order_line_ids):
            raise UserError(_('You cannot confirm a Service order which has no line.'))
        order_no = self.env['ir.sequence'].next_by_code('hc.service.order')
        for line in self.order_line_ids:
            if line.state != 'cancel':
                line.action_set_state('confirmed')
        self.write({'name': order_no, 'order_no': order_no, 'state': 'confirmed', 'order_date': fields.Datetime.now()})
        return True

    @api.multi
    def action_invoice_cancel(self):
        self.ensure_one()
        for line in self.order_line_ids:
            if line.state != 'cancel':
                line.action_set_state('exception')
            self.write({'state': 'invoice_except'})
        return True

    @api.multi
    def action_invoice_end(self):
        self.ensure_one()
        self.write({'state': 'progress'})

    @api.multi
    def action_router(self):
        self.ensure_one()
        for line in self.order_line_ids:
            if line.state != 'cancel':
                line.action_set_state('invoiced')
        return True

    @api.multi
    def action_cancel(self):
        self.ensure_one()
        for inv in self.invoice_ids:
            if inv.state not in ('draft', 'cancel'):
                raise UserError(_('Cannot cancel this Service order! First cancel all invoices attached to this Service order.'))
            inv.signal_workflow('invoice_cancel')
        for line in self.order_line_ids:
            if line.state != 'cancel':
                line.action_set_state('cancel')
        self.write({'state': 'cancel'})
        return True

    def prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a
           Service order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param order: hc.service.order record to invoice
        """
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define sales journal for this company: "%s" (id:%d).') % (self.company_id.name, self.company_id.id))
        invoice_vals = {
            'order_id': self.id,
            'name': self.order_no,
            'origin': self.order_no,
            'type': 'out_invoice',
            'reference': self.patient_id.name + ':' + self.name,
            'account_id': self.patient_id.partner_id.property_account_receivable_id.id,
            'partner_id': self.patient_id.partner_id.id,
            'journal_id': journal_id,
            'comment': self.note,
            'doctor_id': self.doctor_id.id,
            'payment_term': False,
            'user_id': False,
        }
        return invoice_vals

    @api.multi
    def action_create_invoice(self):
        """
        """
        self.ensure_one()
        Invoice = self.env['account.invoice']
        draft_invoice = Invoice.search([('order_id', '=', self.id), ('state', '=', 'draft')])
        lines_not_invoiced_flag = False
        for line in self.order_line_ids:
            if (not line.invoice_line_ids):
                lines_not_invoiced_flag = True
                break
        if lines_not_invoiced_flag:
            if not draft_invoice:
                vals = self.prepare_invoice()
                inv_id = Invoice.create(vals)
            else:
                inv_id = draft_invoice
            for line in self.order_line_ids:
                if (not line.invoice_line_ids) or(line.invoice_line_ids and line.invoice_line_ids.invoice_id.state == 'cancel'):
                    line.action_create_invoice_line(inv_id)
            self.write({'state': 'to_invoice'})

    @api.multi
    def action_view_invoice(self):
        '''
        This function returns an action that display existing invoices of given sales order ids. It can either be a in a list or in a form view, if there is only one invoice to show.
        '''
        invoice_ids = self.mapped('invoice_ids')
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('account.action_invoice_tree1')
        list_view_id = imd.xmlid_to_res_id('account.invoice_tree')
        form_view_id = imd.xmlid_to_res_id('account.invoice_form')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'graph'], [False, 'kanban'], [False, 'calendar'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(invoice_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % invoice_ids.ids
        elif len(invoice_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = invoice_ids.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    def get_last_consultation_order(self, product_id, patient_id):
        c_ids = self.search([('id', '!=', self.id), ('patient_id', '=', patient_id), ('product_id', '=', product_id), ('state', 'not in', ('draft', 'cancel')), ('order_line_ids.parent_id', '=', False)])
        if not c_ids:
            return False
        consultation_orders = self.browse(c_ids)
        last_date = consultation_orders[0].order_date
        last_order = consultation_orders[0]
        for co in consultation_orders:
            if co.order_date > last_date :
                last_date = co.order_date
                last_order = co
        return last_order

    def get_consultation_follow_up(self):
        for service_line in self.order_line_ids:
            if service_line.product_id.service_type == 'consultation':
                consultation_ids = self.env['hc.consultation'].search([('product_id', '=', service_line.product_id.id )])
                consultation= self.env['hc.consultation'].browse(consultation_ids)
                if not consultation:
                    raise UserError(_('Cannot find the Consultation, Please define Consultation for this product: "%s".') % \
                                    (service_line.product_id.name))
                rec = {}
                last_consultation_order = self.get_last_consultation_order(service_line.product_id.id, self.patient_id.id)
                if last_consultation_order:
                    current_date = fields.Datetime.from_string(fields.Datetime.now())
                    diff_date = (current_date - fields.Datetime.from_string(last_consultation_order)).days
                    if consultation.plan_id:
                        min_no_days = 0
                        flag= False
                        for seq in consultation.plan_id.sequence_ids:
                            if ((diff_date - seq.no_of_days) <= 0):
                                flag= True
                                if min_no_days == 0:
                                    min_no_days= seq.no_of_days
                                    rec = seq
                                elif (seq.no_of_days < min_no_days ):
                                    min_no_days = seq.no_of_days
                                    rec = seq
                        if flag:
                            service_line.action_set_follow_up(last_consultation_order.order_line_ids.id)
                return rec

class HCServiceOrderLine(models.Model):
    _name = 'hc.service.order.line'
    _description = 'Service Order Lines'
    _order = 'order_id'

    @api.multi
    def _compute_line_invoiced(self):
        res= {}
        InvoiceLine = self.env['account.invoice.line']
        for line in self:
            inv_line = InvoiceLine.search([('order_line_id', '=', line.id), ('invoice_id.state', '=', 'paid')])
            if inv_line:
                line.invoiced = True
            else:
                line.invoiced = False
        return res

    order_id = fields.Many2one('hc.service.order', 'Service Order', readonly=True, select=True, states={'draft': [('readonly', False)]})
    patient_id = fields.Many2one('hc.patient', related='order_id.patient_id', string='Patient', readonly=True)
    doctor_id = fields.Many2one('resource.resource', related='order_id.doctor_id', string='Doctor', readonly=True)
    order_date = fields.Datetime(related='order_id.order_date', string='Order Date')
    name = fields.Char('Name', size=55, required=True, readonly=True, states={'draft': [('readonly', False)]})
    product_id = fields.Many2one('product.product', 'Item', required=True, readonly=True, states={'draft': [('readonly', False)]}, domain=[('type', '=', 'service'), ('service_type', '!=', False)])
    product_uom_id = fields.Many2one('product.uom', 'Unit of Measure', required=True, readonly=True, states={'draft': [('readonly', False)]})
    product_uom_qty = fields.Float('Quantity', default=1, required=True, readonly=True, states={'draft': [('readonly', False)]})
    note = fields.Text('Note')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('invoiced', 'Invoiced'),
        ('exception', 'Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ], 'State', readonly=True, default='draft')
    invoice_line_ids = fields.One2many('account.invoice.line', 'order_line_id', 'Invoice Lines', readonly=True, copy=False)
    invoiced = fields.Boolean(compute='_compute_line_invoiced', string='Invoiced', readonly=True)
    is_follow_up = fields.Boolean('Is Follow Up', help='This Field add to check if consultation service in Follow Up Or no ')
    parent_id = fields.Many2one('hc.service.order.line', 'Parent')

    _sql_constraints = [
        ('order_id_product_id_unique', 'UNIQUE(order_id,product_id)', 'The Line cannot be Duplicate in the Order')
    ]

    @api.multi
    def action_set_follow_up(self, pt_id):
        self.ensure_one()
        return self.write({'parent_id': pt_id, 'is_follow_up': True})

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return self.update({'name': '', 'product_uom_id': False})
        else:
            return self.update({'name': self.product_id.name, 'product_uom_id': self.product_id.uom_id.id})

    @api.multi
    def action_set_state(self, value):
        self.ensure_one()
        return self.write({'state': value})

    # TODO: Compute Price Unit
    @api.multi
    def _prepare_invoice_line(self, inv_id):
        """Prepare the dict of values to create the new invoice line for a
           sales order line. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record line: sale.order.line record to invoice
           :param int account_id: optional ID of a G/L account to force
               (this is used for returning products including service)
           :return: dict of values to create() the invoice line
        """
        res = {}
        account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
        if not account:
            raise UserError(_('Please define income account for this product: "%s" (id:%d).') % \
                        (self.product_id.name, self.product_id.id,))
        price_unit = self.env['product.uom']._compute_price(self.product_id.uom_id.id, False, self.product_uom_id.id)
        res = {
            'invoice_id': inv_id.id,
            'name': self.name,
            'origin': self.order_id.name,
            'account_id': account.id,
            'uom_id': self.product_uom_id.id,
            'quantity': self.product_uom_qty,
            'price_unit': price_unit,
            'product_id': self.product_id.id,
            'invoice_line_tax_id': False,
            'order_line_id': self.id
        }
        return res

    @api.multi
    def action_create_invoice_line(self, inv_id):
        vals = self._prepare_invoice_line(inv_id)
        if vals:
            line_id = self.env['account.invoice.line'].create(vals)
            return line_id
