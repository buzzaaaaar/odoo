from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_dealer_customer = fields.Boolean(string='Is Dealer Customer', default=False)
    driving_license_number = fields.Char(string='Driving License Number')
    preferred_vehicle_type = fields.Selection([
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('hatchback', 'Hatchback'),
        ('truck', 'Truck'),
        ('van', 'Van'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid')
    ], string='Preferred Vehicle Type')
    
    # Requirement: Purchase history (related vehicles)
    # This can be a One2many to sale orders or directly to vehicles if we link them.
    # Since we are linking vehicles to sales orders, we can just show sales orders.
    # But let's add a smart button or one2many to bought vehicles if possible.
    # We can infer this from sale orders or add a direct link on vehicle if needed. 
    # For now, standard sale order history on partner is available.
    
    purchased_vehicle_ids = fields.Many2many('vehicle.vehicle', compute='_compute_purchased_vehicles', string='Purchased Vehicles')

    def _compute_purchased_vehicles(self):
        for partner in self:
            # Find vehicles sold to this partner via sale orders
            orders = self.env['sale.order'].search([('partner_id', '=', partner.id), ('state', 'in', ['sale', 'done'])])
            # This requires the link in sale order line, which we haven't defined yet fully but will exist.
            # We will assume sale_order_line has `vehicle_id`.
            # To avoid circular dependency issues or missing field errors before `sale_order` module is loaded/updated,
            # we should be careful. But since we are defining the module, it's fine.
            # We'll use a try-except or just `mapped('order_line.vehicle_id')`
            
            vehicles = orders.mapped('order_line.vehicle_id')
            partner.purchased_vehicle_ids = vehicles
