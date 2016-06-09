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
from datetime import datetime, timedelta
import time
from openerp import api, fields, models, _
from openerp.tools.translate import _
from openerp.exceptions import UserError

class HCServiceOrder(models.Model):
    _inherit = "hc.service.order"

    # this function called on 'hc.service.order.basic' workflow
    @api.multi
    def _check_order_contains_lab_test(self):
        self.ensure_one()
        for service_line in self.order_line_ids:
            if service_line.product_id.service_type == 'lab_test':
                return True
        return False

    # TODO: check if the add the line to the order if the order in new state or create new order
    @api.multi
    @api.model
    def action_create_lab_test_order(self):
        self.ensure_one()
        TestOrder = self.env['hc.lab.test.order']
        Test = self.env['hc.lab.test']
        TestLine = self.env['hc.lab.test.order.line']
        test_order = TestOrder.search([('service_order_id', '=', self.id)])
        for service_line in self.order_line_ids:
            if service_line.product_id.service_type == 'lab_test' and service_line.state not in('exception', 'cancel'):
                test_id = Test.get_test_id(service_line.product_id.id)
                if not test_id:
                    raise UserError(_('Cannot find the Test, Please define Test for this product: "%s".') % \
                                    (service_line.product_id.name))
                test_line = TestLine.search([('service_line_id', '=', service_line.id)])
                if not test_line:
                    if not test_order:
                        order_no = self.env['ir.sequence'].next_by_code('hc.lab.test.order')
                        test_order = TestOrder.create({
                            'service_order_id': self.id,
                            'order_no': order_no,
                            'order_date': fields.Datetime.now(),
                            'state': 'new',
                        })
                    for i in xrange(int(service_line.product_uom_qty)):
                        test_line = TestLine.create({
                            'service_line_id': service_line.id,
                            'test_id': test_id.id,
                            'test_order_id': test_order.id,
                            'state': 'new',
                        })
                        if test_id.type == 'normal':
                            test_line.action_create_result_components()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
