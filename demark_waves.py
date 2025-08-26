import math
import pandas as pd

import math

class State:
    _state_machine:any
    waveLow:float
    waveHigh:float
    waveNumber:int
   
    def __init__(self, state_machine=None, wave_number = 0, test_value=None):
        self._state_machine = state_machine
        self.waveLow = float('inf')
        self.waveHigh = -float('inf')
        self.waveNumber = wave_number
        if (test_value is not None):
            self.updateHighsLows(test_value)        

    def updateHighsLows(self, test_value):
        self.waveLow = min(self.waveLow, test_value['Open'], test_value['Close'], test_value['Low'])
        self.waveHigh = max(self.waveHigh, test_value['Open'], test_value['Close'], test_value['High'])

    def step_machine(self, test_value):
        self.updateHighsLows(test_value)
        return False
    
    def is_initial(self):
        return False
    
    def is_final(self):
        return False
    
    def get_str(self):
        pass

    def _is_valid_operand(self, other):
        return hasattr(other, 'waveNumber')
    
    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.waveNumber == other.waveNumber
    
    def __ne__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.waveNumber != other.waveNumber
    
    def __lt__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.waveNumber < other.waveNumber
    
    def __le__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.waveNumber <= other.waveNumber
    
    def __gt__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.waveNumber > other.waveNumber
    
    def __ge__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.waveNumber >= other.waveNumber        

class Trading_Waves:
    _state:State
    _stateHistory:dict
    _stateCount:dict
    waveCounter:int
    def __init__(self):
        self._state = State_Zero_Wave(self)
        self._stateHistory = dict()
        self._stateCount = dict()
        self.waveCounter = 0

    def step_machine(self, test_value, low_thresholds, high_thresholds):
        return self._state.step_machine(test_value, low_thresholds, high_thresholds)
        
    def change_state(self, state):
        self._stateHistory[type(self._state)] = self._state
        self._stateHistory[type(state)] = state

        if type(state) in self._stateCount:
            self._stateCount[type(state)] += 1
        else:
            self._stateCount[type(state)] = 1

        if (not state.is_initial()) & (state < self._state):
            for x in self.waveGenerator(state.waveNumber, self._state.waveNumber):
                state.waveLow = min(state.waveLow, self._stateHistory[type(x)].waveLow)
                state.waveHigh = max(state.waveHigh, self._stateHistory[type(x)].waveHigh)
        elif state.is_initial():
            self._stateHistory = dict()

        if state.is_initial() & self._state.is_final():
            self.waveCounter += 1

        self._state = state    

        return True    

    def get_state_str(self):
         return self._state.get_str()    

    def waveGenerator(self, startWave = 0, endWave=0):
        n = min(max(startWave,0),9)
        while n < max(min(endWave,9), 0):
            if n == 0:
                yield State_Zero_Wave()
            elif n == 1:
                yield State_Possible_Wave1()
            elif n == 2:
                yield State_Confirmed_Wave1()
            elif n == 3:
                yield State_Wave2()
            elif n == 4:
                yield State_Wave3()
            elif n == 5:
                yield State_Wave4()
            elif n == 6:
                yield State_Wave5()
            elif n == 7:
                yield State_WaveA()
            elif n == 8:
                yield State_WaveB()
            elif n == 9:
                yield State_WaveC()
            n += 1

class State_Zero_Wave(State):    

    def __init__(self, state_machine=None, test_value=None):
        super().__init__(state_machine=state_machine, wave_number=0, test_value=test_value)

    def step_machine(self, test_value, low_thresholds, high_thresholds):        
        if min(test_value['Low'], test_value['Close']) <= low_thresholds['C'] :
            return self._state_machine.change_state(State_Possible_Wave1(self._state_machine, test_value))                   
        else :
            return super().step_machine(test_value)
            
    def is_initial(self):
        return True
    
    def get_str(self):
        return '0'

class State_Possible_Wave1(State):
    def __init__(self, state_machine=None, test_value=None):
        super().__init__(state_machine, wave_number=1, test_value=test_value)
        
    def step_machine(self, test_value, low_thresholds, high_thresholds):        
        if max(test_value['High'], test_value['Close']) >= high_thresholds['B'] :
            return self._state_machine.change_state(State_Confirmed_Wave1(self._state_machine, test_value))
        elif min(test_value['Low'], test_value['Close']) <= low_thresholds['A'] :
            return self._state_machine.change_state(State_Zero_Wave(self._state_machine))
        else :
            return super().step_machine(test_value)
    
    def get_str(self):
        return 'P1'

class State_Confirmed_Wave1(State):
    def __init__(self, state_machine=None, test_value=None):
        super().__init__(state_machine, wave_number=2, test_value=test_value)        

    def step_machine(self, test_value, low_thresholds, high_thresholds):        
        if min(test_value['Low'], test_value['Close'])  <= low_thresholds['A'] :
            return self._state_machine.change_state(State_Wave2(self._state_machine, test_value))                    
        else :
            return super().step_machine(test_value)

    def get_str(self):
        return 'C1'

class State_Wave2(State):
    def __init__(self, state_machine=None, test_value=None):
        super().__init__(state_machine, wave_number=3, test_value=test_value)

    def step_machine(self, test_value, low_thresholds, high_thresholds):        
        if (self._state_machine._stateHistory[type(self)].waveHigh > self._state_machine._stateHistory[type(State_Confirmed_Wave1())].waveHigh) & (self._state_machine._stateHistory[type(self)].waveHigh > self._state_machine._stateHistory[type(State_Possible_Wave1())].waveHigh) :
            return self._state_machine.change_state(State_Confirmed_Wave1(self._state_machine, test_value))              
        elif max(test_value['High'], test_value['Close'])  >= high_thresholds['C'] :
            return self._state_machine.change_state(State_Wave3(self._state_machine, test_value))              
        else :
            return super().step_machine(test_value)
            
    def get_str(self):
        return '2'

class State_Wave3(State):
    def __init__(self, state_machine=None, test_value=None):
        super().__init__(state_machine, wave_number=4, test_value=test_value)
        
    def step_machine(self, test_value, low_thresholds, high_thresholds):        
        if min(test_value['Low'], test_value['Close'])  <= low_thresholds['B'] :
            if (self._state_machine._stateHistory[type(self)].waveHigh > self._state_machine._stateHistory[type(State_Confirmed_Wave1())].waveHigh) & (self._state_machine._stateHistory[type(self)].waveHigh > self._state_machine._stateHistory[type(State_Possible_Wave1())].waveHigh) :
                return self._state_machine.change_state(State_Wave4(self._state_machine, test_value))              
            else : 
                return self._state_machine.change_state(State_Zero_Wave(self._state_machine, test_value))             
        else :
            return super().step_machine(test_value)

    def get_str(self):
        return '3'

class State_Wave4(State):
    def __init__(self, state_machine=None, test_value=None):
        super().__init__(state_machine, wave_number=5, test_value=test_value)

    def step_machine(self, test_value, low_thresholds, high_thresholds):        
        if min(test_value['Low'], test_value['Close']) < self._state_machine._stateHistory[type(State_Wave2())].waveLow :
            return self._state_machine.change_state(State_Wave2(self._state_machine, test_value))
        elif max(test_value['High'], test_value['Close']) >= high_thresholds['D'] :
            return self._state_machine.change_state(State_Wave5(self._state_machine, test_value))
        else :
            return super().step_machine(test_value)

    def get_str(self):
        return '4'

class State_Wave5(State):
    def __init__(self, state_machine=None, test_value=None):
        super().__init__(state_machine, wave_number=6, test_value=test_value)

    def step_machine(self, test_value, low_thresholds, high_thresholds):
        if min(test_value['Low'], test_value['Close']) <= low_thresholds['B'] :
            if (self._state_machine._stateHistory[type(self)].waveHigh > self._state_machine._stateHistory[type(State_Wave3())].waveHigh) :
                return self._state_machine.change_state(State_WaveA(self._state_machine, test_value))              
            else : 
                return self._state_machine.change_state(State_Wave3(self._state_machine, test_value))             
        else :
            return super().step_machine(test_value)

    def get_str(self):
        return '5'

class State_WaveA(State):
    def __init__(self, state_machine=None, test_value=None):
        super().__init__(state_machine, wave_number=7, test_value=test_value)

    def step_machine(self, test_value, low_thresholds, high_thresholds):        
        if max(test_value['High'], test_value['Close']) >= high_thresholds['A'] :
            return self._state_machine.change_state(State_WaveB(self._state_machine, test_value))  
        else :
            return super().step_machine(test_value)

    def get_str(self):
        return 'A'

class State_WaveB(State):
    def __init__(self, state_machine=None, test_value=None):
        super().__init__(state_machine, wave_number=8, test_value=test_value)

    def step_machine(self, test_value, low_thresholds, high_thresholds):        
        if min(test_value['Low'], test_value['Close']) <= low_thresholds['C'] :
            return self._state_machine.change_state(State_WaveC(self._state_machine, test_value)) 
        elif (self._state_machine._stateHistory[type(self)].waveHigh > self._state_machine._stateHistory[type(State_Wave5())].waveHigh) :
            return self._state_machine.change_state(State_Wave5(self._state_machine, test_value)) 
        else :
            return super().step_machine(test_value)

    def get_str(self):
        return 'B'

class State_WaveC(State):
    def __init__(self, state_machine=None, test_value=None):
        super().__init__(state_machine, wave_number=9, test_value=test_value)

    def step_machine(self, test_value, low_thresholds, high_thresholds):        
        if min(test_value['Low'], test_value['Close']) <= self._state_machine._stateHistory[type(State_WaveA())].waveLow :
            return self._state_machine.change_state(State_Zero_Wave(self._state_machine)) 
        elif min(test_value['Low'], test_value['Close']) <= low_thresholds['C'] :
            return self._state_machine.change_state(State_Possible_Wave1(self._state_machine, test_value))
        else :
            return super().step_machine(test_value)
    
    def is_final(self):
        return True
    
    def get_str(self):
        return 'C'    
    
def createWaves(inputData, A = 8, B = 13, C = 21, D = 34):
    
    df = inputData.copy()    
    
    df['dayHighA'] = df['Close'].rolling(A).max()
    df['dayLowA'] = df['Close'].rolling(A).min()
    
    df['dayHighB'] = df['Close'].rolling(B).max()
    df['dayLowB'] = df['Close'].rolling(B).min()

    df['dayHighC'] = df['Close'].rolling(C).max()
    df['dayLowC'] = df['Close'].rolling(C).min()

    df['dayHighD'] = df['Close'].rolling(D).max()
    df['dayLowD'] = df['Close'].rolling(D).min()

    df = df.dropna()

    demarkBull = Trading_Waves()
    demarkBear = Trading_Waves()
    testValue = dict()
    lowThresholds = dict()
    highThresholds = dict()

    df['BullWave'] = '0'
    df['BullWaveNumber'] = 0
    df['BearWave'] = '0'
    df['BearWaveNumber'] = 0

    for row in df.itertuples(index=True, name='Pandas'):
         testValue['Open'], testValue['High'], testValue['Low'], testValue['Close'] = row.Open, row.High, row.Low, row.Close
         lowThresholds['A'], lowThresholds['B'], lowThresholds['C'], lowThresholds['D'] = row.dayLowA, row.dayLowB, row.dayLowC, row.dayLowD
         highThresholds['A'], highThresholds['B'], highThresholds['C'], highThresholds['D'] = row.dayHighA, row.dayHighB, row.dayHighC, row.dayHighD
         demarkBull.step_machine(testValue, lowThresholds, highThresholds) 
         df.loc[row.Index, 'WaveBull'] = demarkBull.get_state_str()
         df.loc[row.Index, 'WaveBullNumber'] = demarkBull.waveCounter

         testValue['Open'], testValue['High'], testValue['Low'], testValue['Close'] = -row.Open, -row.Low, -row.High, -row.Close
         lowThresholds['A'], lowThresholds['B'], lowThresholds['C'], lowThresholds['D'] = -row.dayHighA, -row.dayHighB, -row.dayHighC, -row.dayHighD
         highThresholds['A'], highThresholds['B'], highThresholds['C'], highThresholds['D'] = -row.dayLowA, -row.dayLowB, -row.dayLowC, -row.dayLowD
         demarkBear.step_machine(testValue, lowThresholds, highThresholds) 
         df.loc[row.Index, 'WaveBear'] = demarkBear.get_state_str()
         df.loc[row.Index, 'WaveBearNumber'] = demarkBear.waveCounter

    return df