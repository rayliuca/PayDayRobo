# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 12:24:18 2021

@author: admin
"""
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from qtrade import Questrade
from twilio.rest import Client 
from pyeasyga import pyeasyga   # Genetic algorithms
import numpy as np
import random
import collections
import json

with open('keys.json') as f:
    setting_keys = json.load(f)


try:
    qtrade = Questrade(access_code = setting_keys['access_code'])
except:
    qtrade = Questrade(token_yaml='./access_token.yml')
    qtrade.refresh_access_token(from_yaml=True)

portfolio_target = {
    'XEC.TO':0.05, 
    'XEF.TO':0.175, 
    'ZAG.TO':0.10,
    'ZLB.TO':0.25, 
    'ZSP.TO':0.275, 
    'XMU.TO':0.15}

yearly_withdrawal = 0.05 # 5 pecent


def send_email (html_content, setting_keys = setting_keys):
    message = Mail(
        from_email=setting_keys['from_email'],
        to_emails=setting_keys['to_email'],
        subject='Sending with Twilio SendGrid is Fun',
        html_content=html_content)
    try:
        sg = SendGridAPIClient(setting_keys['SENDGRID_API_KEY'])
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

def send_sms (message, setting_keys = setting_keys):
    account_sid = setting_keys['account_sid']
    auth_token = setting_keys['auth_token']
    client = Client(account_sid, auth_token) 
     
    message = client.messages.create(  
                                  messaging_service_sid = setting_keys['messaging_service_sid'], 
                                  body = message,      
                                  to = setting_keys['reciver_phone']
                              ) 

    print(message.sid) 

def simulate_protfolio (portfolio_pos):
    ticket_prices = { key:portfolio_pos[key]['currentMarketValue']/portfolio_pos[key]['openQuantity'] for key in portfolio_pos.keys()}
    
    for key in portfolio_pos:
        portfolio_pos[key]['openQuantity'] = portfolio_pos[key]['openQuantity'] * (135 + random.uniform(-0, 0))
        portfolio_pos[key]['currentMarketValue'] = portfolio_pos[key]['openQuantity'] * ticket_prices[key]
        
    return portfolio_pos

def get_current_portfolio (qtrade):
    portfolio_pos = {}
    accounts = qtrade.get_account_id()
    for account in accounts:
        acc_pos = qtrade.get_account_positions(account)
        # acc_pos is an array of objects, containing the data of each position

        for obj in acc_pos:
            sym = obj['symbol']
            if sym in portfolio_pos:
                portfolio_pos[sym]['openQuantity'] = portfolio_pos[sym]['openQuantity'] + obj['openQuantity']
                portfolio_pos[sym]['currentMarketValue'] = portfolio_pos[sym]['currentMarketValue'] + obj['currentMarketValue']
            elif sym in portfolio_target:
                portfolio_pos[sym]={}
                portfolio_pos[sym]['openQuantity'] = obj['openQuantity']
                portfolio_pos[sym]['currentMarketValue'] = obj['currentMarketValue']

    return portfolio_pos

def gen_fees(individual):
    fees = individual*0.01+4.95
    return fees

def create_individual(data):
    num_tickets = data['num_tickets']
    individual = target_obj['base_individual'].copy()
    for i in range(num_tickets):
        individual[i] = individual[i] + random.uniform(-int(individual[i]*0.5), int(individual[i]*0.5))
    # individual = individual / individual.sum()
    # individual = list(individual)
    
    return individual

def crossover(parent_1, parent_2):
    """ Crossover two parents to produce two children
        Performs a weighted arithmetic recombination
    """
    ratio = random.uniform(-1, 1)  # Generate a number from -1 to 1
    size = len(parent_1)
    crossIndices = np.random.choice([0,1], size=(size,))
    child_1 = parent_1
    child_2 = parent_2
    for i in range(len(crossIndices)):
        if (crossIndices[i] == 1):
            child_1[i] = child_1[i] + ratio * child_2[i]  # Perform weighted sum
            child_2[i] = child_2[i] + ratio * child_1[i]
            
    # normalize the children
    # child_1 = child_1 / sum(child_1)
    # child_2 = child_2 / sum(child_2)
    
    child_1 = list(np.array(child_1).astype(int))
    child_2 = list(np.array(child_2).astype(int))
    
    return child_1, child_2

def mutate(individual):
    """ Mutate an individual to introduce new genetic information to the population
        Adds a random number from 0 to 9 to each allele in the individual (up to two decimal places)
    """
    individual = np.array(individual).astype(float)
    mutateIndices = np.random.choice([0, 1], size=(4,), p=[0.8, 0.2])
    for index in range(len(mutateIndices)):
        if(mutateIndices[index] == 1):
            individual += random.randint(1, 9) * (10**(index - 3))
    # individual = individual/individual.sum()
            
    individual = list(np.array(individual).astype(int))
    individual = list(individual)


def fitness(individual, target_obj):
    """ Calculate fitness of a candidate solution representation
        target_obj = {'portfolio_pos' : portfolio_pos,
                      'portfolio_target' : portfolio_target,
                      'yearly_withdrawal' : yearly_withdrawal,
                      'num_tickets' : num_tickets}
    """
    individual = np.array(individual)
    
    if len(individual[individual<0]) !=0:
        return 10**5
    
    portfolio_pos = target_obj['portfolio_pos']
    portfolio_target = target_obj['portfolio_target']
    yearly_withdrawal = target_obj['yearly_withdrawal']
    # monthly_withdrawal = yearly_withdrawal/12
    monthly_withdrawal = target_obj['monthly_withdrawal']
    
    # target_mix = np.array(list(portfolio_target.values()))
    target_mix = target_obj['target_mix']
    
    # currentMarketValues = [target_obj['portfolio_pos'][key]['currentMarketValue'] for key in target_obj['portfolio_pos'].keys()]
    # currentMarketValues = np.array(currentMarketValues)
    currentMarketValues = target_obj['currentMarketValues']
    
    # openQuantity = [target_obj['portfolio_pos'][key]['openQuantity'] for key in target_obj['portfolio_pos'].keys()]
    # openQuantity = np.array(openQuantity)
    openQuantity = target_obj['openQuantity']
    
    # total_market_val = sum(currentMarketValues)
    # target_withdrawal = monthly_withdrawal * total_market_val
    total_market_val = target_obj['total_market_val']
    target_withdrawal = target_obj['target_withdrawal']
    
    ticket_prices = target_obj['ticket_prices']
    
    # withdrawal_dollars = individual * target_withdrawal
    # withdrawal_shares = (withdrawal_dollars / ticket_prices).astype(int)
    withdrawal_shares = individual
    
    fees = gen_fees(withdrawal_shares).sum()
    target_obj['fees'] = fees
    
    withdrawal_share_val = (withdrawal_shares * ticket_prices).sum() - fees
    target_obj['withdrawal_share_val'] = withdrawal_share_val
    
    residue_portfolio = openQuantity - withdrawal_shares
    residue_portfolio_vals = residue_portfolio * ticket_prices
    residue_portfolio_alloc = residue_portfolio_vals / residue_portfolio_vals.sum()
    
    val_error = (withdrawal_share_val / target_withdrawal -1) ** 2
    portfolio_error = ((residue_portfolio_alloc - target_mix)**2).sum()*10

    
    fit = val_error + portfolio_error + fees/300
    
    return fit

def pre_process(target_obj):
    portfolio_pos = target_obj['portfolio_pos']
    portfolio_target = target_obj['portfolio_target']
    yearly_withdrawal = target_obj['yearly_withdrawal']
    
    monthly_withdrawal = yearly_withdrawal/12
    target_obj['monthly_withdrawal'] = monthly_withdrawal
    
    target_mix = np.array(list(portfolio_target.values()))
    target_obj['target_mix'] = target_mix
    currentMarketValues = [target_obj['portfolio_pos'][key]['currentMarketValue'] for key in target_obj['portfolio_pos'].keys()]
    currentMarketValues = np.array(currentMarketValues)
    target_obj['currentMarketValues'] = currentMarketValues
    
    openQuantity = [target_obj['portfolio_pos'][key]['openQuantity'] for key in target_obj['portfolio_pos'].keys()]
    openQuantity = np.array(openQuantity)
    target_obj['openQuantity'] = openQuantity
    
    total_market_val = sum(currentMarketValues)
    target_obj['total_market_val'] = total_market_val
    
    target_withdrawal = monthly_withdrawal * total_market_val
    target_obj['target_withdrawal'] = target_withdrawal
    
    ticket_prices = currentMarketValues / openQuantity
    target_obj['ticket_prices'] = ticket_prices
    
    # base_individual = np.zeros((target_obj['num_tickets'],))
    base_individual = target_withdrawal * target_mix/ ticket_prices
    target_obj['base_individual'] = base_individual.astype(int)
    
    return target_obj

portfolio_target = collections.OrderedDict(sorted(portfolio_target.items()))
num_tickets = len(portfolio_target)

portfolio_pos = get_current_portfolio (qtrade)
portfolio_pos = simulate_protfolio(portfolio_pos)
portfolio_pos = collections.OrderedDict(sorted(portfolio_pos.items()))

target_obj = {'portfolio_pos' : portfolio_pos,
              'portfolio_target' : portfolio_target,
              'yearly_withdrawal' : yearly_withdrawal,
              'num_tickets' : num_tickets}
target_obj = pre_process(target_obj)
# ind = create_individual(target_obj)
# fitness(ind, target_obj)

ga1 = pyeasyga.GeneticAlgorithm(target_obj,  # Input data
                               population_size = 50,
                               generations = 75,
                               crossover_probability = 0.8,
                               mutation_probability = 0.01,
                               maximise_fitness = False
                               )
ga1.create_individual = create_individual
ga1.crossover_function = crossover
ga1.mutate_function = mutate
ga1.selection_function = ga1.tournament_selection # pyeasyga’s implemented selection function
ga1.fitness_function = fitness

ga1.run()
bestSoln = ga1.best_individual()
print("Fitness = ", bestSoln[0])
print("Solution = ", bestSoln[1])

tickets = list(portfolio_target.keys())
shares_to_buy = {tickets[i] : bestSoln[1][i] for i in range(target_obj['num_tickets'])}

print(shares_to_buy)

def gen_text (shares_to_buy, target_obj = target_obj):
    message = "It is that time of the month! This month, lets sell\n"
    for key in shares_to_buy:
        message += f"{key}: {shares_to_buy[key]}\n"
    expected_fees = target_obj    
    
    message += f"for a total of {target_obj['withdrawal_share_val']:.2f} CAD."
    
    return message


# send_sms(gen_text (shares_to_buy, target_obj = target_obj))
send_email (gen_text (shares_to_buy, target_obj = target_obj), setting_keys = setting_keys)




