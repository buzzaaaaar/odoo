from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Vehicle(models.Model):
    _name = 'vehicle.vehicle'
    _description = 'Vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Vehicle ID', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    make = fields.Char(string='Make', required=True, tracking=True)
    model = fields.Char(string='Model', required=True, tracking=True)
    variant = fields.Char(string='Variant')
    year = fields.Integer(string='Manufacturing Year', required=True)
    vehicle_type = fields.Selection([
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('hatchback', 'Hatchback'),
        ('truck', 'Truck'),
        ('van', 'Van'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid')
    ], string='Vehicle Type', required=True, tracking=True)
    transmission = fields.Selection([
        ('manual', 'Manual'),
        ('automatic', 'Automatic')
    ], string='Transmission', required=True)
    fuel_type = fields.Selection([
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid')
    ], string='Fuel Type', required=True)
    engine_capacity = fields.Float(string='Engine Capacity (L)')
    color = fields.Char(string='Color')
    mileage = fields.Float(string='Mileage (km)', tracking=True)
    vin = fields.Char(string='VIN Number', required=True, copy=False, help="Vehicle Identification Number")
    purchase_price = fields.Monetary(string='Purchase Price', currency_field='currency_id')
    selling_price = fields.Monetary(string='Selling Price', currency_field='currency_id', required=True, tracking=True)
    condition = fields.Selection([
        ('new', 'New'),
        ('used', 'Used')
    ], string='Condition', required=True, default='new')
    status = fields.Selection([
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold')
    ], string='Status', default='available', tracking=True, required=True, copy=False)
    image_ids = fields.Many2many('ir.attachment', string='Images', help="Add vehicle images")
    
    notes = fields.Text(string='Notes')
    
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    _sql_constraints = [
        ('vin_unique', 'unique(vin)', 'The VIN number must be unique!')
    ]

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('vehicle.vehicle') or _('New')
        return super(Vehicle, self).create(vals)

    def action_available(self):
        self.status = 'available'

    def action_reserved(self):
        self.status = 'reserved'

    def action_sold(self):
        self.status = 'sold'

    def action_print_report(self):
        return self.env.ref('my_custom_addon.action_report_vehicle_list').report_action(self or self.search([]))
