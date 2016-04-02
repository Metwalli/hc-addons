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
from openerp import fields, models, api, _
from openerp.tools.translate import _
from openerp.exceptions import UserError

#--------  Test Configuration --------

#TODO: when create new lab test make default values for the fields type= service and service_type= 'lab_test'(Done)
#TODO: optimize Normal Range for the patients(Done)
#TODO: Printing barcode for specimens depending on Specialization and test
#TODO: Create Profile
#TODO: Create Formula

class ProductProduct(models.Model):
    _inherit = "product.product"

    lab_test_ids = fields.One2many('hc.lab.test', 'product_id', string='Test Definition', select=True, ondelete='cascade')

    @api.model
    def create(self, vals):
        product = super(ProductProduct,self).create(vals)
        if product.service_type == 'lab_test':
            test_vals = {}
            test_vals['product_id'] = product.id
            test_vals['name'] = product.name
            test_vals['type'] = 'normal'
            self.env['hc.lab.test'].create(test_vals)
        return product

class HCLabTestMethod(models.Model):
    _name = "hc.lab.test.method"

    name = fields.Char('Name', size=255, required=True)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name Must be Unique')
    ]

class HCLabTestSpecimen(models.Model):
    _name = "hc.lab.test.specimen"

    name = fields.Char('Name', size=255, required=True)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name Must be Unique')
    ]

class HCLabTestSpecimenLine(models.Model):
    _name = "hc.lab.test.specimen.line"

    test_id = fields.Many2one('hc.lab.test', 'Specimen', required=True, ondelete='cascade')
    specimen_id = fields.Many2one('hc.lab.test.specimen', 'Specimen', required=True)
    qty = fields.Integer('Quantity')
    uom_id = fields.Many2one('product.uom', 'Unit of Measure')
    expiry = fields.Integer('Expiry(Hrs)')

class HCLabTest(models.Model):
    _name = "hc.lab.test"

    product_id = fields.Many2one('product.product', 'Product', domain=[('service_type', '=', 'lab_test')], required=True)
    name = fields.Char('Name', required=True, size=200)
    abbreviation = fields.Char('Abbreviation', size=22, help='Short Name')
    code = fields.Char('Code', size=22)
    perform_to = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('both', 'Both')
    ], string='Performed To', default= 'both')
    performed_time = fields.Integer('Performed Time')
    performed_time_unit = fields.Selection([
        ('minute', 'Minute(s)'),
        ('hour', 'Hour(s)'),
        ('day', 'Day(s)'),
        ('month', 'Month(s)'),
        ('year', 'Year(s)')
    ], string='Perform Time Unit')
    outsourcing = fields.Boolean('OutSourcing')
    type = fields.Selection([
        ('normal', 'Normal'),
        ('culture', 'Culture')
    ], string='Test Type', required=True, default= 'normal')
    method_id = fields.Many2one('hc.lab.test.method', string='Method')
    specimen_line_ids = fields.One2many('hc.lab.test.specimen.line', 'test_id', 'Test Specimens')
    component_ids = fields.One2many('hc.lab.test.component', 'test_id', 'Test Components', select=True, ondelete='cascade')
    category_id = fields.Many2one('product.category', related='product_id.categ_id', string='Category', readonly=True)
    separate_specimen = fields.Boolean('Separate Specimen')


    @api.multi
    def get_test_id(self, product_id):
        return self.search([('product_id', '=', product_id)])

    @api.onchange('product_id')
    def product_id_change(self):
        if self.product_id:
            self.name = self.product_id.name
        else:
            self.name = ''

class HCLabTestComponent(models.Model):
    _name = "hc.lab.test.component"
    _order = 'test_id,sequence'

    name = fields.Char('Name', size=50, required=True)
    sequence = fields.Integer('Sequence', help="Gives the sequence order when displaying a list Components.")
    uom_id = fields.Many2one('product.uom', 'Unit of Measure', help="Default Unit of Measure used for Numeric Test.")
    test_id = fields.Many2one('hc.lab.test', 'Test Name', domain=[('type', '=', 'normal')], required=True, select=True, ondelete='cascade')
    type = fields.Selection([('num', 'Numeric'), ('text', 'Text')], 'Result Type', default= 'num',
                            help="A Result Type of Test, Numeric Or Text")
    normal_range_ids = fields.One2many('hc.lab.test.component.normal_range', 'component_id', 'Normal Range')
    default_value_ids = fields.One2many('hc.lab.test.component.default_values', 'component_id', 'Default Values')

class HCLabTestComponentNormalRange(models.Model):
    _name = "hc.lab.test.component.normal_range"

    component_id = fields.Many2one('hc.lab.test.component', 'Component', required=True, domain=[('type', '=', 'num')], ondelete='cascade')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('all', 'All')
    ], string='Gender', required=True)
    age_from = fields.Integer('Age From')
    age_to = fields.Integer('Age To')
    age_unit = fields.Selection([
        ('minute', 'Minute(s)'),
        ('hour', 'Hour(s)'),
        ('day', 'Day(s)'),
        ('month', 'Month(s)'),
        ('year', 'Year(s)')
    ], string='Perform Time Unit', default= 'year')
    range_desc = fields.Char('Range Description', size=255)
    unit = fields.Many2one('product.uom', related= 'component_id.uom_id', string='Unit', readonly=True)
    high_value = fields.Float('High Value', required=True)
    low_value = fields.Float('Low Value', required=True)

    _sql_constraints = [
        ('cmpt_gender_uniq', 'unique(component_id,gender)', 'The Gender must be Unique for Component'),
        ('min_less_max_check', 'CHECK(high_value >= low_value)', 'Low Value must less than High Value'),
    ]

    @api.model
    def create(self, vals):
        if not vals['range_desc']:
            unt = ''
            if self.component_id.uom_id:
                unt = self.component_id.uom_id.name
            vals['range_desc'] = str(vals['gender']) + ": " + str(vals['low_value']) + "-" + str(vals['high_value']) + " " + unt
        return super(HCLabTestComponentNormalRange, self).create(vals)


class HCLabTestComponentDefaultValues(models.Model):
    _name = "hc.lab.test.component.default_values"

    name = fields.Char('Value', required=True)
    component_id = fields.Many2one('hc.lab.test.component', 'Component', required=True, domain=[('type', '=', 'text')], ondelete='cascade')

    _sql_constraints = [
        ('cmpt_name_uniq', 'unique(component_id,name)', 'The Name must be Unique for Component'),
    ]

class HCLabTestOrganism(models.Model):
    _name = 'hc.lab.test.organism'

    code = fields.Char('Code', size=20, required=True)
    name = fields.Char('Name', size=255, required=True)

class HCLabTestAntibiotic(models.Model):
    _name = 'hc.lab.test.antibiotic'

    code = fields.Char('Code', size=20, required=True)
    name = fields.Char('Name', size=255, required=True)

class HCLabTestAntibioticSensitive(models.Model):
    _name = 'hc.lab.test.antibiotic_sensitive'

    code = fields.Char('Code', size=22, required=True)
    name = fields.Char('Value', size=20, required=True)

#------------ Test Orders ----------------

# TODO: Create Test Line Workflow
# TODO: Create Report for Group Test Printing (Done)
# TODO: on Done By Field show only the Laboratory Technician

class HCLabTestOrder(models.Model):
    _name = "hc.lab.test.order"
    _inherits = {
        'hc.service.order': 'service_order_id'
    }
    _order = "order_date desc,order_no"

    service_order_id = fields.Many2one('hc.service.order', 'Service Order1', required=True, readonly=True, ondelete='restrict')
    order_no = fields.Char('Order No', size=20, readonly=True)
    order_date = fields.Datetime('Order Date', readonly=True)
    order_line_ids = fields.One2many('hc.lab.test.order.line', 'test_order_id', 'Test Lines')
    state = fields.Selection(related='order_line_ids.state', string='State')

    @api.multi
    @api.depends('order_line_ids.state')
    def _check_all_lines_in_new_state(self):
        if any(line.state != 'new' for line in  self.order_line_ids):
            return False
        else:
            return True

    @api.multi
    @api.depends('order_line_ids.state')
    def _check_any_line_result_entered(self):
        if any(line.state == 'result_entered' for line in self.order_line_ids):
            return True
        else:
            return False

    @api.multi
    @api.depends('order_line_ids.state')
    def _check_all_lines_result_verified(self):
        if any(line.state != 'result_verified' for line in self.order_line_ids):
            return False
        else:
            return True

    @api.multi
    @api.depends('order_line_ids.state')
    def _check_fully_done(self):
        if any(line.state not in ('result_entered', 'result_verified', 'dispatch', 'done') for line in self.order_line_ids):
            return False
        else:
            return True
    @api.multi
    @api.depends('order_line_ids.state')
    def _check_done(self):
        if self.state != 'cancel':
            if not any(line.state != 'cancel' for line in self.order_line_ids):# if no line in order
                return False
            if any(line.state not in ('result_verified', 'dispatch')for line in self.order_line_ids):
                return False
            for line in self.order_line_ids:
                if line.state != 'cancel':
                    line.action_set_state('done')
            return True
        else:
            return False

    @api.multi
    @api.depends('order_line_ids.state')
    def action_cancel(self):
        self.ensure_one()
        if any(line.state not in ('draft', 'new') for line in self.order_line_ids):
            raise UserError(_('Cannot cancel order not in draft or new state!'))
        for line in self.order_line_ids:
            line.action_button_cancel()
        return True

    @api.multi
    def action_button_confirm(self):
        self.signal_workflow('order_confirm')
        return True

    @api.multi
    def action_confirm(self):
        for o in self:
            if not any(line.state != 'cancel' for line in o.order_line_ids):
                raise UserError(_('You cannot confirm an order which has no line.'))
            if o.state != 'draft':
                raise UserError(_('You cannot confirm an order not in draft state.'))
            order_no = self.env['ir.sequence'].next_by_code('hc.lab.test.order')
            for line in o.order_line_ids:
                if line.state != 'cancel':
                    line.action_set_state('new')
            o.write({'order_no': order_no, 'order_date': fields.Datetime.now()})
        return True

    @api.v7
    def action_button_collect_sample(self, cr, uid,ids, context=None):
        self.signal_workflow(cr, uid, ids, 'collect_sample')
        return True
    @api.multi
    def action_collect_sample(self):
        for line in self.order_line_ids:
            if line.state in ('new', 'sample_recollect'):
                line.write({'state': 'sample_collected', 'sample_collected': True, 'sample_collect_date': fields.Datetime.now()})
        return True

    @api.multi
    def action_set_state(self, value):
        for o in self:
            o.write({'state': value})
        return True

    @api.multi
    def action_lab_test_results_print(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'hc_lab.report_test_order_result')

    @api.multi
    def button_dispatch(self):
        self.signal_workflow('order_dispatch')
        return True

    @api.multi
    def action_dispatch(self):
        for line in self.order_line_ids:
            if line.state in ('result_entered', 'result_verified'):
                line.action_set_state('dispatch')
        return True

    @api.multi
    def action_done(self):
        for line in self.order_line_ids:
            if line.state != 'cancel':
                line.action_set_state('done')
        return True

class HCLabTestOrderLine(models.Model):
    _name = 'hc.lab.test.order.line'
    _inherits = {
        'hc.service.order.line': 'service_line_id'
    }
    _description = 'Laboratory Test Order Lines'
    _order = 'test_order_id,sequence'

    sequence = fields.Integer('Sequence')
    service_line_id = fields.Many2one('hc.service.order.line', 'Order Line', required=True, readonly=True, ondelete='restrict', help='This field added to connect test line with service line')
    test_id = fields.Many2one('hc.lab.test', string='Test', required=True, readonly=True, states={'draft': [('readonly', False)]})
    test_order_id = fields.Many2one('hc.lab.test.order', 'Lab Test Order', required=True, readonly=True, ondelete='restrict', states={'draft': [('ondelete', 'cascade')],'new': [('ondelete', 'cascade')]})
    order_date = fields.Datetime(related='test_order_id.order_date', string='Order Date')
    sample_collected = fields.Boolean('Collect Sample', readonly=True, states={'new': [('readonly', False)], 'sample_collected': [('readonly', False)], 'sample_recollect': [('readonly', False)]})
    sample_collect_date = fields.Datetime('Sample Collection Date', readonly=True)
    sample_collected_by = fields.Many2one('hr.employee', 'Sample Collect By', readonly=False, states={'draft': [('readonly', True)], 'new': [('readonly', True)], 'sample_recollect': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('new', 'New Order'),
        ('sample_collected', 'Sample Collected'),
        ('sample_recollect', 'Sample Recollect'),
        ('result_entered', 'Results Entered'),
        ('result_verified', 'Results Verified'),
        ('dispatch', 'Dispatch'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
        ], 'Test Line State', readonly=True, default= 'draft')
    test_type = fields.Selection(related='test_id.type', string='Test Type')
    line_result_ids = fields.One2many('hc.lab.test.order.line.results', 'test_line_id', string= 'Test Results', readonly=True, states={'new': [('readonly', False)], 'sample_collected': [('readonly', False)], 'sample_recollect': [('readonly', False)], 'result_entered': [('readonly', False)]})
    culture_organism_ids = fields.One2many('hc.lab.test.order.line.culture_organism', 'test_line_id', string='Organism', states={'result_verified': [('readonly', '=', True)], 'dispatch': [('readonly', '=', True)]})
    done_by = fields.Many2one('hr.employee', 'Done By', readonly=True, states={'result_entered': [('readonly', False)]})
    done_date = fields.Datetime('Results Entered Date', readonly=True)
    result_verified = fields.Boolean('Verify Results', readonly=True, states={'result_entered': [('readonly', False)], 'result_verified': [('readonly', False)]})
    verified_by = fields.Many2one('hr.employee', 'Verified By', readonly=True, states={'result_verified': [('readonly', False)]})

    @api.multi
    def _check_result_entered(self, vals):
        for cmpt in vals:
            if cmpt[2]:
                if('value' in cmpt[2]):
                    if (cmpt[2]['value']):
                        return True
        return False

    @api.multi
    def _check_remove_all_result(self, vals):
        i = 0
        for r in self.line_result_ids:
            if r.value:
                if(not vals[i][2]) or (vals[i][2] and ('value' not in vals[i][2] or vals[i][2]['value'])):
                    return False
            i += 1
        return True

    @api.multi
    @api.onchange('sample_collected')
    def _onchange_sample_collected(self):
        if self.sample_collected:
            self.state = 'sample_collected'
            self.sample_collect_date = fields.Datetime.now()
            self.sample_collected_by = self.get_employee_id(self.env.uid)
        else:
            self.state = 'new'
            self.sample_collect_date = False
            self.sample_collected_by = False
        return

    @api.onchange('result_verified')
    def _onchange_result_verified(self):
        if self.result_verified:
            self.state = 'result_verified'
            self.verified_by = self.get_employee_id(self.env.uid)
        else:
            self.state = 'result_entered'
            self.verified_by = False

    @api.multi
    def write(self, vals):
        if self.test_id.type == 'culture':
            if 'culture_organism_ids' in vals:
                if vals['culture_organism_ids']:
                    vals['state'] = 'result_entered'
                    vals['done_date'] = fields.Datetime.now()
            elif(not self.culture_organism_ids):
                if('sample_collected' in vals and vals['sample_collected']):
                    vals['state'] = 'sample_collected'
                    vals['sample_collect_date'] = fields.Datetime.now()
                    vals['sample_collected_by'] = self.get_employee_id(self.env.uid)
                else:
                    vals['state'] = 'new'
                    vals['sample_collect_date'] = False
                    vals['sample_collected_by'] = False
        else:
            if 'line_result_ids' in vals:
                if self.state in ('new', 'sample_collected', 'sample_recollect'):
                    if(self._check_result_entered(vals['line_result_ids'])):
                        vals['state'] = 'result_entered'
                        vals['done_date'] = fields.Datetime.now()
                    elif('sample_collected' in vals and vals['sample_collected']):
                        vals['state'] = 'sample_collected'
                        vals['sample_collect_date'] = fields.Datetime.now()
                        vals['sample_collected_by'] = self.get_employee_id(self.env.uid)
                    else:
                        vals['state'] = 'new'
                        vals['sample_collect_date'] = False
                        vals['sample_collected_by'] = False
                elif self.state == 'result_entered':
                    if self._check_remove_all_result(vals['line_result_ids']):
                        if self.sample_collected:
                            vals['state'] = 'sample_collected'
                        else:
                            vals['state'] = 'new'

        return super(HCLabTestOrderLine, self).write(vals)

    @api.multi
    def action_button_cancel(self):
        for line in self:
            if line.state not in ('draft', 'new'):
                raise UserError(_('You cannot cancel a line that has been already done state'))
            line.write({'state': 'cancel'})
        return

    @api.multi
    @api.model
    def action_create_result_components(self):
        """
             To Create Test Components.
        """
        components = self.env['hc.lab.test.component'].search([('test_id', '=', self.test_id.id)])
        if not self.line_result_ids:
            LineResults = self.env['hc.lab.test.order.line.results']
            for c in components:
                normal_range_ids = self.env['hc.lab.test.component.normal_range'].search([('component_id', '=', c.id)])
                nrmlrng= ""
                sql = "SELECT * FROM hc_lab_test_component_normal_range " \
                      "WHERE component_id= " + str(c.id) + " " \
                        "AND((gender = 'all' OR gender ='" + str(self.patient_id.gender) + "') " \
                            "AND((age_from <= " + str(self.patient_id.age) + " AND age_to >= " + str(self.patient_id.age) + ")OR(age_to =0)))"
                self.env.cr.execute(sql)
                nrs = self.env.cr.dictfetchall()
                hv=0
                lv=0
                for n in nrs:
                    nrmlrng = n['range_desc']
                    hv = n['high_value']
                    lv = n['low_value']
                #for nr in self.pool.get('hc.lab.test.component.normal_range').browse(cr,uid,normal_range_ids,context=context):
                #   nrmlrng += nr.gender + ": "+ str(nr.low_value) + " - " + str(nr.high_value)+ "\n"
                LineResults.create({
                    'component_id': c.id,
                    'label': c.name,
                    'test_line_id': self.id,
                    'normal_range': nrmlrng,
                    'low_value': lv,
                    'high_value': hv,
                    'unit': c.uom_id.name or False,
                })
        return True

    @api.multi
    def action_recollect_sample(self):
        self.state = 'sample_recollect'
        self.sample_collected = False
        return

    @api.multi
    def action_set_state(self, value):
        self.ensure_one()
        return self.write({'state': value})

    @api.multi
    def action_dispatch_report(self):
        self.ensure_one()
        return self.write({'state': 'dispatch'})

    @api.multi
    def button_confirm(self):
        self.ensure_one()
        return self.write({'state': 'new'})

    @api.multi
    def get_employee_id(self, uid):
        return self.env['hr.employee'].search([('user_id', '=', uid)]).id


class HCLabTestOrderLineCultureOrganism(models.Model):
    _name = "hc.lab.test.order.line.culture_organism"

    test_line_id = fields.Many2one('hc.lab.test.order.line', 'Test Line', required=True, ondelete='cascade')
    organism_id = fields.Many2one('hc.lab.test.organism', 'Organism', required=True, ondelete='cascade')
    name = fields.Char('Name', required=True, size=55)
    observation_period = fields.Selection([
        ('24hrs', '24 Hours'),
        ('48hrs', '48 Hours'),
        ('72hrs', '72 Hours'),
        ('4days', '4 Days')
    ], string='Observation Period')
    antibiotic_study_ids = fields.One2many('hc.lab.test.order.line.culture_organism.antibiotic_study', 'culture_organism_id', string='Antibiotic')
    state = fields.Selection(related='test_line_id.state', string='State', readonly=True)

    @api.onchange('organism_id')
    def onchange_organism_id(self):
        if self.organism_id:
            self.name = self.organism_id.name
        else:
            self.name = ''

class HCLabTestOrderLineCultureOrganismAntibioticStudy(models.Model):
    _name = "hc.lab.test.order.line.culture_organism.antibiotic_study"

    culture_organism_id = fields.Many2one('hc.lab.test.order.line.culture_organism', 'Culture Organism', required=True, ondelete='cascade')
    antibiotic_id = fields.Many2one('hc.lab.test.antibiotic', 'Antibiotic', required=True, ondelete='cascade')
    name = fields.Char('Name', required=True, size=55)
    sensitive = fields.Many2one('hc.lab.test.antibiotic_sensitive', string='Value', required=True)#Antibiotic Values may be S+,S++,S--, and so on
    state = fields.Selection(related='culture_organism_id.state', string='State', states={'result_verified': [('readonly', True)], 'dispatch': [('readonly', True)], 'done': [('readonly', True)]})

    @api.onchange('antibiotic_id')
    def onchange_antibiotic_id(self):
        if self.antibiotic_id:
            self.name = self.antibiotic_id.name
        else:
            self.name = ''

class HCLabTestOrderLineResults(models.Model):
    _name = "hc.lab.test.order.line.results"

    @api.one
    @api.depends('value')
    def _compute_num_value(self):
        if self.component_id.type == 'num' and self.value:
            self.num_value = eval(self.value)

    test_line_id = fields.Many2one('hc.lab.test.order.line', 'Test Order', required=True, ondelete='cascade')
    order_date = fields.Datetime(related='test_line_id.order_date', string='Order Date', store=True)
    patient_id = fields.Many2one(related='test_line_id.patient_id', string='Patient', readonly=True)
    test_id = fields.Many2one('hc.lab.test', related= 'test_line_id.test_id', string='Test', readonly=True)
    component_id = fields.Many2one('hc.lab.test.component', 'Component', readonly=True, required=True, domain=[('test_id' , '=', 'test_id')], ondelete='cascade')
    label = fields.Char('Label', readonly=True)
    value = fields.Char('Value', size=50, readonly=True, states={'new': [('readonly', False)], 'sample_collected': [('readonly', False)], 'sample_recollect': [('readonly', False)], 'result_entered': [('readonly', False)]})
    default_value_id = fields.Many2one('hc.lab.test.component.default_values', string='Default Values')
    normal_range = fields.Text('Normal Range', readonly=True)
    high_value = fields.Float('High Value', readonly=True)
    low_value = fields.Float('Low Value', readonly=True)
    flag = fields.Char('Result Flag', help= "This Field Showing on Result report if the value more than normal range show Flag meaning, and so on")
    unit = fields.Char('Unit', size=50, readonly=True)
    state = fields.Selection(related='test_line_id.state', string='State', readonly=True)
    value_type = fields.Selection(related='component_id.type', size=22, string='Result Type', readonly=True)
    num_value = fields.Float('Num Results', compute='_compute_num_value', store=True)
    _sql_constraints = [
        ('test_line_id_component_id_uniq', 'unique(test_line_id,component_id)', 'The Component must be Unique in line'),
    ]

    @api.onchange('default_value_id')
    def onchange_default_value_id(self):
        if self.default_value_id:
            self.value = self.default_value_id.name
        else:
            self.value = False
