# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class StockMove(models.Model):
    _inherit = 'stock.move'

    scan_barcode = fields.Char('Barcode')

    def onchange_barcode(self):
        if self.scan_barcode:
            stock_quant=self.env['stock.production.lot'].search([('product_id','=',self.product_id.id),('name','=',self.scan_barcode)])
            temp = 0
            for line in self.move_line_ids:
                if self.picking_id.picking_type_id.code=='incoming':
                    if not line._origin.lot_name:                        
                        line._origin.update({"lot_name" : self.scan_barcode,}); 
                        if self.product_id.tracking == 'serial':
                            line._origin.qty_done = 1

                        else:
                            line._origin.qty_done = line._origin.product_uom_qty
                        break
                    else:
                        temp+=1
                else:
                    if not line.lot_id or not line.qty_done:
                        lot_id = self.env['stock.production.lot'].search([('name','=',self.scan_barcode)])
                        lot_id = lot_id.filtered(lambda a: a.product_id.id == self.product_id.id);
                        if not lot_id:
                            raise UserError(_('%s Barcode not available in system') % self.scan_barcode)
                        if lot_id.product_id.id != self.product_id.id:
                            raise UserError(_('You have selected different product barcode'))
                        if self.product_id.tracking == 'serial':
                            if stock_quant:
                                if stock_quant.product_qty == 0.00:
                                    raise ValidationError(_('%s Serial Number was already used. Please use different serial number.') % self.scan_barcode)
                                else:
                                    line.lot_id = lot_id.id
                                    line.qty_done = 1
                        elif self.product_id.tracking == 'lot':
                            line.lot_id = lot_id.id
                            if lot_id.product_qty >= line.product_uom_qty:
                                line.qty_done = line.product_uom_qty
                            else:
                                line.qty_done = lot_id.product_qty
                        break
                    else:
                        temp+=1
            if temp == len(self.move_line_ids):
                raise UserError('All the serials/lots are assigned')
        self.scan_barcode = False
        return self.action_show_details()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
