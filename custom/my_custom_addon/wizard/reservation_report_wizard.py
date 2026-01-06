from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import io
import xlsxwriter

class VehicleReservationReportWizard(models.TransientModel):
    _name = 'vehicle.reservation.report.wizard'
    _description = 'Reservation Report Wizard'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    
    file_data = fields.Binary(string='File Data')
    file_name = fields.Char(string='File Name')

    def action_export_excel(self):
        # Search for reservations
        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('date_reservation', '>=', self.date_from),
            ('date_reservation', '<=', self.date_to)
        ]
        reservations = self.env['vehicle.reservation'].search(domain)

        if not reservations:
            raise UserError(_("No reservations found for the selected criteria."))

        # Create Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Reservations')

        # Formats
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1})
        text_format = workbook.add_format({'border': 1})

        # Headers
        headers = ['Reference', 'Customer', 'Vehicle', 'Reservation Date', 'Expiry Date', 'Status']
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_format)

        # Data
        for row_num, res in enumerate(reservations, start=1):
            worksheet.write(row_num, 0, res.name, text_format)
            worksheet.write(row_num, 1, res.partner_id.name, text_format)
            worksheet.write(row_num, 2, res.vehicle_id.make + ' ' + res.vehicle_id.model, text_format)
            worksheet.write(row_num, 3, res.date_reservation, date_format)
            worksheet.write(row_num, 4, res.date_expiry, date_format)
            worksheet.write(row_num, 5, res.state, text_format)

        workbook.close()
        output.seek(0)
        
        file_content = base64.b64encode(output.read())
        output.close()

        self.write({
            'file_data': file_content,
            'file_name': f'Reservations_{self.partner_id.name}_{self.date_from}_{self.date_to}.xlsx'
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'vehicle.reservation.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self.env.context,
        }
