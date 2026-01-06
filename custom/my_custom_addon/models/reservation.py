from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class VehicleReservation(models.Model):
    _name = 'vehicle.reservation'
    _description = 'Vehicle Reservation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Reservation Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    vehicle_id = fields.Many2one('vehicle.vehicle', string='Vehicle', required=True, domain="[('status', '=', 'available')]", tracking=True)
    date_reservation = fields.Datetime(string='Reservation Date', default=fields.Datetime.now, required=True)
    date_expiry = fields.Datetime(string='Expiry Date', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('done', 'Done') # When vehicle is sold? Or just released?
    ], string='Status', default='draft', tracking=True)
    
    # Requirement: Vehicle status updates to Reserved when active
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('vehicle.reservation') or _('New')
        return super(VehicleReservation, self).create(vals)

    def action_confirm(self):
        for rec in self:
            if rec.vehicle_id.status != 'available':
                raise ValidationError(_("Vehicle is not available for reservation!"))
            rec.vehicle_id.action_reserved()
            rec.state = 'active'

    def action_cancel(self):
        for rec in self:
            if rec.state == 'active':
                rec.vehicle_id.action_available()
            rec.state = 'cancelled'

    def action_expire(self):
        for rec in self:
            if rec.state == 'active':
                rec.vehicle_id.action_available()
                rec.state = 'expired'
                
    @api.model
    def _cron_expire_reservations(self):
        expired_reservations = self.search([
            ('state', '=', 'active'),
            ('date_expiry', '<', fields.Datetime.now())
        ])
        for reservation in expired_reservations:
            reservation.action_expire()
