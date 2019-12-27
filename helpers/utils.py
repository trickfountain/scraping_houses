def monthly_payments(price, interest_rate=3.79, amortization=20):
           
    # Interest rate monthly
    mrate=interest_rate/100/12
    nper=amortization*12
    monthly_payment = (price*(mrate*(1+mrate)**nper)/(((1+mrate)**nper)-1))
    
    return monthly_payment