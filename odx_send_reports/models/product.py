from datetime import date, timedelta, datetime

from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def send_reports(self):
        web_base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        from_date = str(date.today() - timedelta(days=7))
        to_date = str(date.today())

        table = '''<p style="font-size: 16px;line-height: 20px;">
                                                                       Dear  ,<br>
                                                                          &#160;&#160;&#160;&#160; List Of Stock Product <br>
                                                                          &#160;&#160;&#160;&#160; %s
                                                                                  </p>
                                                                                   <table  border="1" width=60%% style="border-collapse:collapse;font-size: 16px;" >
                                                                              <thead>
                                                                                  <tr style="background-color:#0077b3;">
                                                                                      <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Serial No</font></b><br></td>
                                                                                      <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Image</font></b><br></td>
                                                                                      <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Name</font></b><br></td>
                                                                                      <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Quantity</font></b><br></td>
                                                                                      <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Make to Order</font></b><br></td>
                                                                                      <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Sale Price</font></b><br></td>
                                                                                      <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Cost Price</font></b><br></td>
                                                                                      <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Total Cost</font></b><br></td>
                                                                                      <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Profit</font></b><br></td>
                                                                                      <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Forcasted Profit</font></b><br></td>
                                                                                      <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Sale QTY</font></b><br></td>
                                                                                  </tr>
                                                                              </thead>
                                                                              <tbody>
                                                                               ''' % (to_date,)

        product_ids = self.env["product.product"].search([("qty_available", ">", 0.0)])
        mto_id = self.env.ref('stock.route_warehouse0_mto').id
        sale_order_ids = None
        sale_qty = 0
        serial_no = 0
        if from_date and to_date:
            sale_order_ids = self.env["sale.order"].search(
                [("confirmation_date", ">=", from_date), ("confirmation_date", "<=", to_date)])
        for product_id in product_ids:
            if from_date and to_date:
                sale_qty = sum(self.env["sale.order.line"].search(
                    [("product_id", "=", product_id.id), ("order_id", "in", sale_order_ids.ids)]).mapped(
                    "qty_delivered"))
            qoh = product_id.qty_available
            profit = product_id.lst_price - product_id.standard_price
            forcasted_profit = qoh * profit
            if mto_id in product_id.route_ids.ids:
                make_to_order = "YES"
            else:
                make_to_order = "NO"

            serial_no = serial_no + 1
            table += '''
                                                                        <tr>
                                                                            <td style="text-align: center;"><font style="color: #000000;">''' + str(
                serial_no) + '''</font><br></td>
                                                                            <td>  <img src = "${''' + web_base_url + '''}/banners?record=${''' + str(
                product_id.id) + '''}"/>
                    </td>
                                                                            <td style="text-align: center;"><font style="color: #000000;">''' + str(
                product_id.name) + '''</font><br></td>
                                        <td style="text-align: center;"><font style="color: #000000;">''' + str(
                qoh) + '''</font><br></td>
                                                                            <td style="text-align: center;"><font style="color: #000000;">''' + str(
                make_to_order) + '''</font><br></td>
                                                                            <td style="text-align: center;"><font style="color: #000000;">''' + str(
                product_id.lst_price) + '''</font><br></td>
                                        <td style="text-align: center;"><font style="color: #000000;">''' + str(
                product_id.standard_price) + '''</font><br></td>
                                                                            <td style="text-align: center;"><font style="color: #000000;">''' + str(
                product_id.standard_price * qoh) + '''</font><br></td>
                                                                            <td style="text-align: center;"><font style="color: #000000;">''' + str(
                profit) + '''</font><br></td>
                                        <td style="text-align: center;"><font style="color: #000000;">''' + str(
                forcasted_profit) + '''</font><br></td>
                                                                            <td style="text-align: center;"><font style="color: #000000;">''' + str(
                sale_qty) + '''</font><br></td>
                                                                        </tr>
                                                                            '''

        compose = self.env['mail.mail'].create({
            'subject': 'List Of Stock Product',
            'body_html': '%s' % table,
            'email_to': self.env.user.partner_id.email,
        })
        compose.send()

        table = '''<p style="font-size: 16px;line-height: 20px;">
                                                                               Dear  ,<br>
                                                                                  &#160;&#160;&#160;&#160;List Of MTO Product <br>
                                                                                  &#160;&#160;&#160;&#160;%s
                                                                                          </p>
                                                                                           <table  border="1" width=60%% style="border-collapse:collapse;font-size: 16px;" >
                                                                                      <thead>
                                                                                          <tr style="background-color:#0077b3;">
                                                                                              <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Serial No</font></b><br></td>
                                                                                              <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Image</font></b><br></td>
                                                                                              <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Name</font></b><br></td>
                                                                                              <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Quantity</font></b><br></td>
                                                                                              <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Category</font></b><br></td>

                                                                                          </tr>
                                                                                      </thead>
                                                                                      <tbody>
                                                                                       ''' % (to_date,)

        mto_id = self.env.ref('stock.route_warehouse0_mto')
        product_ids = self.env["product.product"].search([("route_ids", "in", [mto_id.id])])
        serial_no = 0
        for product_id in product_ids:
            # print(product_id.image_small)
            # print(type(product_id.image_small))
            serial_no += 1
            if product_id.categ_ids:
                category_list = [category_id.display_name for category_id in product_id.categ_ids]
            else:
                category_list = [""]
            for category in category_list:
                table += '''
                                                                                        <tr>
                                                                                            <td style="text-align: center;"><font style="color: #000000;">''' + str(
                    serial_no) + '''</font><br></td>
                                                                                            <td>  <img src = "${  ''' + web_base_url + '''}/banners?record=${''' + str(
                    product_id.id) + '''}"/>
                    </td>
                                                                                            <td style="text-align: center;"><font style="color: #000000;">''' + str(
                    product_id.name) + '''</font><br></td>
                                                        <td style="text-align: center;"><font style="color: #000000;">''' + str(
                    product_id.qty_available) + '''</font><br></td>
                                                                                            <td style="text-align: center;"><font style="color: #000000;">''' + str(
                    category) + '''</font><br></td>

                                                                                        </tr>
                                                                                            '''

        compose = self.env['mail.mail'].create({
            'subject': 'List Of MTO Product',
            'body_html': '%s' % table,
            'email_to': self.env.user.partner_id.email,
        })
        compose.send()

        table = '''<p style="font-size: 16px;line-height: 20px;">
                                                                                       Dear  ,<br>
                                                                                          &#160;&#160;&#160;&#160; Ordered Qty
                                                                                          ,<br>
                                                                                          &#160;&#160;&#160;&#160; %s to %s
                                                                                                  </p>
                                                                                                   <table  border="1" width=60%% style="border-collapse:collapse;font-size: 16px;" >
                                                                                              <thead>
                                                                                                  <tr style="background-color:#0077b3;">
                                                                                                      <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Serial No</font></b><br></td>
                                                                                                      <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Image</font></b><br></td>
                                                                                                      <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Name</font></b><br></td>
                                                                                                      <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Sale Qty</font></b><br></td>
                                                                                                      <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Based on Highest Sale percentage</font></b><br></td>
                                                                                                      <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Based on Total Sale percentage</font></b><br></td>
                                                                                                      <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Profit</font></b><br></td>
                                                                                                      <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Based on Highest Profit percentage</font></b><br></td>
                                                                                                      <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Based on Total Profit percentage</font></b><br></td>

                                                                                                  </tr>
                                                                                              </thead>
                                                                                              <tbody>
                                                                                               ''' % (
            from_date, to_date)

        high_sale = 0
        high_profit = 0
        total_sale = 0
        total_profit_report = 0
        serial_no = 0

        query_picking = """select pt.name as product_name , pp.id as product_id, sum(sl.product_uom_qty) as sale_qty, sum(sl.price_unit * sl.product_uom_qty) as profit from sale_order_line sl
                                inner join product_product pp on pp.id = sl.product_id
                                inner join product_template pt on pt.id = pp.product_tmpl_id
                                inner join sale_order so on so.id = sl.order_id
                                where so.state in ('done', 'sale') and
                                so.confirmation_date::date between '""" + str(from_date) + """' and '""" + str(
            to_date) + """'
                                group by pt.name, pp.id"""

        self.env.cr.execute(query_picking)
        results = self.env.cr.dictfetchall()

        for result in results:
            if result['sale_qty'] > high_sale:
                high_sale = result['sale_qty']
            total_sale += result['sale_qty']

            if result['profit'] > high_profit:
                high_profit = result['profit']
            total_profit_report += result['profit']

        for product_dict in results:
            serial_no += 1
            sale_percentage = 0
            total_sale_percentage = 0
            profit_percentage = 0
            total_profit_percentage = 0
            if high_sale:
                sale_percentage = round((product_dict.get("sale_qty") * 100) / high_sale, 2)
            if total_sale:
                total_sale_percentage = round((product_dict.get("sale_qty") * 100) / total_sale, 2)
            if total_profit_report:
                total_profit_percentage = round((product_dict.get("profit") * 100) / total_profit_report, 2)

            if high_profit:
                profit_percentage = round((product_dict.get("profit") * 100) / high_profit, 2)

            table += '''
                                                                                                    <tr>
                                                                                                        <td style="text-align: center;"><font style="color: #000000;">''' + str(
                serial_no) + '''</font><br></td>
                <td>  <img src = "${''' + web_base_url + '''}/banners?record=${''' + str(
                product_dict.get("product_id")) + '''}"/>
                    </td>

                                                                                                        <td style="text-align: center;"><font style="color: #000000;">''' + str(
                product_dict.get("product_name")) + '''</font><br></td>
                                                                    <td style="text-align: center;"><font style="color: #000000;">''' + str(
                product_dict.get("sale_qty")) + '''</font><br></td>
                                                                                                        <td style="text-align: center;"><font style="color: #000000;">''' + str(
                sale_percentage) + '''</font><br></td>
                  <td style="text-align: center;"><font style="color: #000000;">''' + str(
                total_sale_percentage) + '''</font><br></td>
                                                                                                        <td style="text-align: center;"><font style="color: #000000;">''' + str(
                product_dict.get("profit")) + '''</font><br></td>
                                                                                                        <td style="text-align: center;"><font style="color: #000000;">''' + str(
                profit_percentage) + '''</font><br></td>
                                                                    <td style="text-align: center;"><font style="color: #000000;">''' + str(
                total_profit_percentage) + '''</font><br></td>
                                                                                                    </tr>


                                                                                                        '''

        compose = self.env['mail.mail'].create({
            'subject': 'Orderd Qty',
            'body_html': '%s' % table,
            'email_to': self.env.user.partner_id.email,
        })
        compose.send()

        table = '''<p style="font-size: 16px;line-height: 20px;">
                                                                                               Dear  ,<br>
                                                                                                  &#160;&#160;&#160;&#160; Delivered Qty
                                                                                                  <br>
                                                                                                  &#160;&#160;&#160;&#160; %s to %s
                                                                                                          </p>
                                                                                                           <table  border="1" width=60%% style="border-collapse:collapse;font-size: 16px;" >
                                                                                                      <thead>
                                                                                                          <tr style="background-color:#0077b3;">
                                                                                                              <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Serial No</font></b><br></td>
                                                                                                              <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Image</font></b><br></td>
                                                                                                              <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Name</font></b><br></td>
                                                                                                              <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Sale Qty</font></b><br></td>
                                                                                                              <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Based on Highest Sale percentage</font></b><br></td>
                                                                                                              <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Based on Total Sale percentage</font></b><br></td>
                                                                                                              <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Profit</font></b><br></td>
                                                                                                              <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Based on Highest Profit percentage</font></b><br></td>
                                                                                                              <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Based on Total Profit percentage</font></b><br></td>

                                                                                                          </tr>
                                                                                                      </thead>
                                                                                                      <tbody>
                                                                                                       ''' % (
            from_date, to_date,)

        high_sale = 0
        high_profit = 0
        total_sale = 0
        total_profit_report = 0
        serial_no = 0

        query_picking = """select pt.name as product_name,pp.id as product_id, sum(sl.qty_delivered) as sale_qty, sum(sl.price_unit * sl.qty_delivered) as profit from sale_order_line sl
                                            inner join product_product pp on pp.id = sl.product_id
                                            inner join product_template pt on pt.id = pp.product_tmpl_id
                                            inner join sale_order so on so.id = sl.order_id
                                            where
                                            so.confirmation_date::date between '""" + str(
            from_date) + """' and '""" + str(
            to_date) + """'
                                            group by pt.name, pp.id"""

        self.env.cr.execute(query_picking)
        results = self.env.cr.dictfetchall()

        for result in results:
            if result['sale_qty'] > high_sale:
                high_sale = result['sale_qty']
            total_sale += result['sale_qty']

            if result['profit'] > high_profit:
                high_profit = result['profit']
            total_profit_report += result['profit']

        for product_dict in results:
            serial_no += 1
            sale_percentage = 0
            total_sale_percentage = 0
            profit_percentage = 0
            total_profit_percentage = 0
            if high_sale:
                sale_percentage = round((product_dict.get("sale_qty") * 100) / high_sale, 2)
            if total_sale:
                total_sale_percentage = round((product_dict.get("sale_qty") * 100) / total_sale, 2)
            if total_profit_report:
                total_profit_percentage = round((product_dict.get("profit") * 100) / total_profit_report, 2)

            if high_profit:
                profit_percentage = round((product_dict.get("profit") * 100) / high_profit, 2)

            table += '''
                                                                                                            <tr>
                                                                                                                <td style="text-align: center;"><font style="color: #000000;">''' + str(
                serial_no) + '''</font><br></td>
                
                <td>  <img src = "${''' + web_base_url + '''}/banners?record=${''' + str(
                product_dict.get("product_id")) + '''}"/>
                    </td>

                                                                                                                <td style="text-align: center;"><font style="color: #000000;">''' + str(
                product_dict.get("product_name")) + '''</font><br></td>
                                                                            <td style="text-align: center;"><font style="color: #000000;">''' + str(
                product_dict.get("sale_qty")) + '''</font><br></td>
                                                                                                                <td style="text-align: center;"><font style="color: #000000;">''' + str(
                sale_percentage) + '''</font><br></td>
                          <td style="text-align: center;"><font style="color: #000000;">''' + str(
                total_sale_percentage) + '''</font><br></td>
                                                                                                                <td style="text-align: center;"><font style="color: #000000;">''' + str(
                product_dict.get("profit")) + '''</font><br></td>
                                                                                                                <td style="text-align: center;"><font style="color: #000000;">''' + str(
                profit_percentage) + '''</font><br></td>
                                                                            <td style="text-align: center;"><font style="color: #000000;">''' + str(
                total_profit_percentage) + '''</font><br></td>
                                                                                                            </tr>

        '''

        compose = self.env['mail.mail'].create({
            'subject': 'Delivered Qty',
            'body_html': '%s' % table,
            'email_to': self.env.user.partner_id.email,
        })
        compose.send()

        table = '''<p style="font-size: 16px;line-height: 20px;">
                                                                                                       Dear  ,<br>
                                                                                                          &#160;&#160;&#160;&#160; Invoiced Qty <br>
                                                                                                          &#160;&#160;&#160;&#160; %s to %s
                                                                                                                  </p>
                                                                                                                   <table  border="1" width=60%% style="border-collapse:collapse;font-size: 16px;" >
                                                                                                              <thead>
                                                                                                                  <tr style="background-color:#0077b3;">
                                                                                                                      <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Serial No</font></b><br></td>
                                                                                                                      <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Image</font></b><br></td>
                                                                                                                      <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Name</font></b><br></td>
                                                                                                                      <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Sale Qty</font></b><br></td>
                                                                                                                      <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Based on Highest Sale percentage</font></b><br></td>
                                                                                                                      <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Based on Total Sale percentage</font></b><br></td>
                                                                                                                      <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Profit</font></b><br></td>
                                                                                                                      <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Based on Highest Profit percentage</font></b><br></td>
                                                                                                                      <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Based on Total Profit percentage</font></b><br></td>

                                                                                                                  </tr>
                                                                                                              </thead>
                                                                                                              <tbody>
                                                                                                               ''' % (
            from_date, to_date,)

        high_sale = 0
        high_profit = 0
        total_sale = 0
        total_profit_report = 0
        serial_no = 0

        query_picking = """select pt.name as product_name,pp.id as product_id ,sum(sl.qty_invoiced) as sale_qty, sum(sl.price_unit * sl.qty_invoiced) as profit from sale_order_line sl
                                                        inner join product_product pp on pp.id = sl.product_id
                                                        inner join product_template pt on pt.id = pp.product_tmpl_id
                                                        inner join sale_order so on so.id = sl.order_id
                                                        where
                                                        so.confirmation_date::date between '""" + \
                        str(from_date) + """' and '""" + str(to_date) + """'  group by pt.name, pp.id"""

        self.env.cr.execute(query_picking)
        results = self.env.cr.dictfetchall()

        for result in results:
            if result['sale_qty'] > high_sale:
                high_sale = result['sale_qty']
            total_sale += result['sale_qty']

            if result['profit'] > high_profit:
                high_profit = result['profit']
            total_profit_report += result['profit']

        for product_dict in results:
            serial_no += 1
            sale_percentage = 0
            total_sale_percentage = 0
            profit_percentage = 0
            total_profit_percentage = 0
            if high_sale:
                sale_percentage = round((product_dict.get("sale_qty") * 100) / high_sale, 2)
            if total_sale:
                total_sale_percentage = round((product_dict.get("sale_qty") * 100) / total_sale, 2)
            if total_profit_report:
                total_profit_percentage = round((product_dict.get("profit") * 100) / total_profit_report, 2)

            if high_profit:
                profit_percentage = round((product_dict.get("profit") * 100) / high_profit, 2)

            table += '''
                                                                                                                    <tr>
                                                                                                                        <td style="text-align: center;"><font style="color: #000000;">''' + str(
                serial_no) + '''</font><br></td>
                
                <td>  <img src = "${''' + web_base_url + '''}/banners?record=${''' + str(
                product_dict.get("product_id")) + '''}"/>
                    </td>

                                                                                                                        <td style="text-align: center;"><font style="color: #000000;">''' + str(
                product_dict.get("product_name")) + '''</font><br></td>
                                                                                    <td style="text-align: center;"><font style="color: #000000;">''' + str(
                product_dict.get("sale_qty")) + '''</font><br></td>
                                                                                                                        <td style="text-align: center;"><font style="color: #000000;">''' + str(
                sale_percentage) + '''</font><br></td>
                                  <td style="text-align: center;"><font style="color: #000000;">''' + str(
                total_sale_percentage) + '''</font><br></td>
                                                                                                                        <td style="text-align: center;"><font style="color: #000000;">''' + str(
                product_dict.get("profit")) + '''</font><br></td>
                                                                                                                        <td style="text-align: center;"><font style="color: #000000;">''' + str(
                profit_percentage) + '''</font><br></td>
                                                                                    <td style="text-align: center;"><font style="color: #000000;">''' + str(
                total_profit_percentage) + '''</font><br></td>
                                                                                                                    </tr>


                                                                                                                        '''

        compose = self.env['mail.mail'].create({
            'subject': 'Invoiced Qty',
            'body_html': '%s' % table,
            'email_to': self.env.user.partner_id.email,
        })
        compose.send()

        record = self.env['stock.warehouse'].search([])

        wizard = self.env['non.moving.product.wizard.ept'].create({
            'warehouse_ids': [(6, 0, record.ids)],
            'from_date': date.today() - timedelta(days=7),
            'to_date': date.today()})
        from_date = wizard.from_date
        to_date = wizard.to_date
        serial_no = 0

        today = datetime.now().strftime("%Y-%m-%d")

        warehouse_ids = wizard.warehouse_ids.ids

        data_dict = wizard.prepare_data(today, warehouse_ids, from_date, to_date)

        table = '''<p style="font-size: 16px;line-height: 20px;">
                                                                                                         Dear  ,<br>
                                                                                                                  &#160;&#160;&#160;&#160; Non Moving Products Report <br>
                                                                                                                  &#160;&#160;&#160;&#160; %s to %s
                                                                                                                          </p>
                                                                                                                           <table  border="1" width=60%% style="border-collapse:collapse;font-size: 16px;" >
                                                                                                                      <thead>
                                                                                                                          <tr style="background-color:#0077b3;">
                                                                                                                              <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Serial No</font></b><br></td>
                                                                                                                              <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Image</font></b><br></td>
                                                                                                                                 <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Product ID</font></b><br></td>
                                                                                                                              <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Product Code</font></b><br></td>
                                                                                                                              <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Product Name</font></b><br></td>
                                                                                                                              <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Available Qty</font></b><br></td>
                                                                                                                              <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Rack Location</font></b><br></td>
                                                                                                                              <td style="text-align: center;"><b><font style="color: 	#FFFFFF;">Last Sale Date</font></b><br></td>
                                                                                                                              <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Duration from Last sale\n(In days)</font></b><br></td>
                                                                                                                              <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Last Purchase Date</font></b><br></td>
                                                                                                                              <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Unit Cost</font></b><br></td>
                                                                                                                              <td width=10%% style="text-align: center;"><b><font style="color: 	#FFFFFF;">Total Cost</font></b><br></td>


                                                                                                                          </tr>
                                                                                                                      </thead>
                                                                                                                      <tbody>
                                                                                                                        ''' % (
            from_date, to_date,)

        if data_dict:
            for warehouse_id, data_details in data_dict.items():
                for product_data in data_details:
                    serial_no += 1
                    table += '''
                                                                                                                            <tr>
                                                                                                                                <td style="text-align: center;"><font style="color: #000000;">''' + str(
                        serial_no) + '''</font><br></td>
                        
                        <td>  <img src = "${''' + web_base_url + '''}/banners?record=${''' + str(
                        product_data.get('product_id')) + '''}"/>
                    </td>

                                                                                                                                <td style="text-align: center;"><font style="color: #000000;">''' + str(
                        product_data.get('product_id')) + '''</font><br></td>
                                                                                            <td style="text-align: center;"><font style="color: #000000;">''' + str(
                        product_data.get('default_code') or '-') + '''</font><br></td>
                                                                                                                                <td style="text-align: center;"><font style="color: #000000;">''' + str(
                        product_data.get('name')) + '''</font><br></td>
                                          <td style="text-align: center;"><font style="color: #000000;">''' + str(
                        product_data.get('qty_available')) + '''</font><br></td>
                                                                                                                                <td style="text-align: center;"><font style="color: #000000;">''' + str(
                        product_data.get('rack_location')) + '''</font><br></td>
                                                                                                                                <td style="text-align: center;"><font style="color: #000000;">''' + str(
                        product_data.get('last_sale_date')) + '''</font><br></td>
                                                                                            <td style="text-align: center;"><font style="color: #000000;">''' + str(
                        product_data.get(
                            'last_day_oldest')) + '''</font><br></td>                                                         <td style="text-align: center;"><font style="color: #000000;">''' + str(
                        product_data.get('last_purchase_date')) + '''</font><br></td>
                                                                                                                                <td style="text-align: center;"><font style="color: #000000;">''' + str(
                        product_data.get('cost_of_product')) + '''</font><br></td>
                                                                                            <td style="text-align: center;"><font style="color: #000000;">''' + str(
                        product_data.get('total_cost')) + '''</font><br></td>
                                                                                                                            </tr>


                                                                                                                                '''
        compose = self.env['mail.mail'].create({
            'subject': 'Non Moving Products Report',
            'body_html': '%s' % table,
            'email_to': self.env.user.partner_id.email,
        })
        compose.send()
