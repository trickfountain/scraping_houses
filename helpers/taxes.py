import pandas as pd
import numpy as np

def amount_in_interval(val, low, high):
    if val < low:
        return 0
    if val >= high:
        return high-low
    if low <= val <= high:
        return val-low
    else:
        Exception("Error in comparison between value and interval (low,high)")

def tax_calculator(df, tax_brackets, id_col='centris_id', price_col='price', Debug=False):
    """Helper function to calculate total tax based on tax brackets
    uses amount_in_interval()
    tax brackets should be in the form of {'bracket_name': (low, high, tax_rate)}
    
    Returns a dataframe with columns id_col, price_col, taxes"""
    
    taxes = df.loc[:, [id_col, price_col]]
    
    # Add a column per tax bracket and make total at the end
    for bracket, (low, high, rate) in tax_brackets.items():
        taxes[f'{bracket}'] = taxes[f'{price_col}'].apply(lambda x: amount_in_interval(x, low, high)) * rate
    
    # Compute total of all brackets
    taxes['total'] = taxes.iloc[:,2:].sum(axis=1)
    
    if Debug == True:
        return taxes
    else:
        return taxes.iloc[:,[0,1,-1]]

class TaxBrackets(object):
    welcome_tax = {
        'Montreal' : {
        '0$-50,900$': (0, 50900, 0.005),
        '50,900$-254,400$': (50900, 254400, 0.01),
        '254,400$-508,700$ ': (254400, 508700, 0.015),
        '508,700$, 1,017,400$' :(508700, 1017400, 0.02),
        '1,017,400$ +' : (1017400, np.inf, 0.025)
    }}
    
    school_tax = {
        'Montreal': {
            'School tax: Fixed rate': (0, np.inf, 0.0015035)
        }
    }
    
    # Base sur: http://ville.montreal.qc.ca/pls/portal/docs/PAGE/SERVICE_FIN_FR/MEDIA/DOCUMENTS/2019_PLATEAU_FR.PDF
    
    property_tax = {
        'Montreal': {
            'Fonciere generale': (0, np.inf, 0.006519),
            "Taxe speciale de l'eau": (0, np.inf, 0.001083),
            "ARTM": (0, np.inf, 0.000025),
            "Voirie": (0, np.inf, 0.000036),
            "Arrondissement - Services": (0, np.inf, 0.000591),
            "Arrondissement - Investissements": (0, np.inf, 0.000315),
        }
    }
