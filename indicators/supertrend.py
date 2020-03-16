import backtrader as bt


class SuperTrend(bt.Indicator):
    """
    SuperTrend Algorithm :
    
        BASIC UPPERBAND = (high + low) / 2 + Multiplier * ATR
        BASIC lowERBAND = (high + low) / 2 - Multiplier * ATR
        
        FINAL UPPERBAND = IF( (Current BASICUPPERBAND < Previous FINAL UPPERBAND) or (Previous close > Previous FINAL UPPERBAND))
                            THEN (Current BASIC UPPERBAND) ELSE Previous FINALUPPERBAND)
        FINAL lowERBAND = IF( (Current BASIC lowERBAND > Previous FINAL lowERBAND) or (Previous close < Previous FINAL lowERBAND)) 
                            THEN (Current BASIC lowERBAND) ELSE Previous FINAL lowERBAND)
        SUPERTREND = IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current close <= Current FINAL UPPERBAND)) THEN
                        Current FINAL UPPERBAND
                    ELSE
                        IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current close > Current FINAL UPPERBAND)) THEN
                            Current FINAL lowERBAND
                        ELSE
                            IF((Previous SUPERTREND = Previous FINAL lowERBAND) and (Current close >= Current FINAL lowERBAND)) THEN
                                Current FINAL lowERBAND
                            ELSE
                                IF((Previous SUPERTREND = Previous FINAL lowERBAND) and (Current close < Current FINAL lowERBAND)) THEN
                                    Current FINAL UPPERBAND
        
    """
        
    lines = ('super_trend',)
    params = (('period', 7),
              ('multiplier', 3),
             )
    plotlines = dict(
                    super_trend=dict(
                    _name='ST',
                    color='blue',
                    alpha=1
                    ))
                    
    plotinfo = dict(subplot=False)
    
    def __init__(self):
        self.st = [0]
        self.finalupband = [0]
        self.finallowband = [0]
        self.addminperiod(self.p.period)
        atr = bt.ind.ATR(self.data, period=self.p.period)
        self.upperband = (self.data.high + self.data.low)/2 + self.p.multiplier * atr
        self.lowerband = (self.data.high + self.data.low)/2 - self.p.multiplier * atr
        
 
    def next(self):
        
        pre_upband=self.finalupband[0]
        pre_lowband=self.finallowband[0]
        
        if self.upperband[0] < self.finalupband[-1] or self.data.close[-1] > self.finalupband[-1]:
            self.finalupband[0] = self.upperband[0]
            
        else:
            self.finalupband[0] = self.finalupband[-1]
            
        if self.lowerband[0] > self.finallowband[-1] or self.data.close[-1] < self.finallowband[-1]:
            
            self.finallowband[0] = self.lowerband[0]
            
        else:
            self.finallowband[0] = self.finallowband[-1]
          
        if  self.data.close[0] <= self.finalupband[0] and ( (self.st[-1] == pre_upband)):
             
            self.st[0] = self.finalupband[0]
            self.lines.super_trend[0] = self.finalupband[0]
            
        elif (self.st[-1] == pre_upband) and (self.data.close[0] > self.finalupband[0]) :
            
            self.st[0] = self.finallowband[0]
            self.lines.super_trend[0] = self.finallowband[0]
            
        elif (self.st[-1] == pre_lowband) and ( self.data.close[0] >= self.finallowband[0]) :
                
            self.st[0] = self.finallowband[0]
            self.lines.super_trend[0] = self.finallowband[0]
                   
        elif (self.st[-1] == pre_lowband) and ( self.data.close[0] < self.finallowband[0]): 
            
            self.st[0] = self.finalupband[0]
            self.lines.super_trend[0] = self.st[0]
