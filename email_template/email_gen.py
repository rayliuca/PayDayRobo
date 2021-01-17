# -*- coding: utf-8 -*-
"""
Created on Sun Jan 17 00:36:08 2021

@author: admin
"""
from datetime import date

def html_gen(shares_to_buy, target_obj):
    f_main = open("template.html", "rt")
    f_line_item = open("line_items.html", "rt")
    f_subtotal = open("subtotal.html", "rt")
    f_fees = open("fees.html", "rt")
    
    main = f_main.read()
    line_item = f_line_item.read()
    subtotal = f_subtotal.read()
    fees = f_fees.read()
    
    f_main.close()
    f_line_item.close()
    f_subtotal.close()
    f_fees.close()
    
    ticket_names = list(shares_to_buy.keys())
    line_item_combos=""
    subtotal_val = 0
    for i in range(target_obj['num_tickets']):
        ticket_name = ticket_names[i]
        q_to_buy = shares_to_buy[ticket_name]
        market_val = q_to_buy * target_obj['ticket_prices'][i]
        line_item_temp = line_item.replace('replace_with_line_item_name', ticket_name)
        line_item_temp = line_item_temp.replace('replace_with_line_item_quantity',  f"{q_to_buy:d}")
        line_item_temp = line_item_temp.replace('replace_with_line_item_val', f"{market_val:.2f}")
        line_item_combos = line_item_combos + ' \n ' + line_item_temp
        
        subtotal_val += market_val
        
    subtotal = subtotal.replace('replace_with_subtotal_val', f"{subtotal_val:.2f}")
    fees = fees.replace('replace_with_fee_val', f"{-target_obj['fees']:.2f}")
    
    total_val = subtotal_val - target_obj['fees']
    
    main = main.replace('replace_with_date', str(date.today()))
    main = main.replace('replace_with_line_items', line_item_combos )
    main = main.replace('replace_with_subtotal', subtotal )
    main = main.replace('replace_with_fees', fees)
    main = main.replace('replace_with_total_val', f"{total_val:.2f}" )
    
    return main

f_out = open("test.html", "w")
f_out.write(html_gen(shares_to_buy, target_obj))
f_out.close()