import time 
import random
from enum import Enum
from uuid import uuid4


# cdn regions
REGIONS = [ "iad-01",   # US East
    "lhr-01",   # Europe West
    "fra-01",   # Europe Central
    "sin-01",   # Asia Pacific
    "bom-01",   # India
] 
P_TO_B_BUFFER = 0.12 # PLAYING->BUFFERING chance (outage probability) base outage buffer,#entry rate
B_TO_P_BUFFER = 0.30 # BUFFERING->PLAYING chance #drain rate
B_TO_S_BUFFER = 0.05 # BUFFERING -> STALL chance
S_TO_B_BUFFER = 0.20 # STALL -> BUFFERING chance


OUTAGE = {
    "region": REGIONS[0],
    "start": 0,  #tick in which outage starts 
    "ends": 200,   #tick at which outage ends
    "severity": 5 #multiplier on the baseline buffer
}
N_SESSIONS = 20 # no of concurrent viewers 
N_TICKS =  360 # 360 ticks * 1s = 6min of simulated time 


class PlaybackState(Enum):
    PLAYING = "playing"
    BUFFERING = "buffering"
    STALL = "stall"

class Session:
    def __init__(self,
                 session_id:str,
                 region:str):
        
        self.session_id:str = session_id 
        self.region:str = region
        self.state:PlaybackState = PlaybackState.PLAYING

    def state_transition(self,buffering:float):
        """
        transition rules based on probability defined 
        P_TO_B = chances of buffering 
        B_TO_S = chance of stalling 
        S_TO_B = chance of un-stalling
        B_TO_P = chance of recovery
        """
        roll = random.random() 
        p_to_b_buffer = buffering
        if self.state == PlaybackState.PLAYING:
            # 2 states possible form playing
            if roll < p_to_b_buffer:
                self.state = PlaybackState.BUFFERING 
            else:
                self.state = PlaybackState.PLAYING 

        elif self.state == PlaybackState.BUFFERING:
            #all 3 states possible 
            if roll < B_TO_S_BUFFER:
                self.state = PlaybackState.STALL 
            elif roll < B_TO_S_BUFFER + B_TO_P_BUFFER:
                self.state = PlaybackState.PLAYING 
            else:
                self.state = PlaybackState.BUFFERING 

        elif self.state == PlaybackState.STALL:
            # can only go to buffering 
            if roll < S_TO_B_BUFFER:
                self.state = PlaybackState.BUFFERING 
            else:
                self.state = PlaybackState.STALL

    def advance(self,tick):
        """
        Decides the session NEXT state for this tick 
        read self.state -> roll probability _> write self.state
        """
        p_to_b_buffer = P_TO_B_BUFFER

        if ( self.region == OUTAGE.get("region") and
             OUTAGE["start"]<=tick < OUTAGE["ends"]
             ):
            #p = probability of buffering
            p_to_b_buffer = P_TO_B_BUFFER * OUTAGE["severity"] #increases the probability of changing state
        # change state
        self.state_transition(p_to_b_buffer)
            
    def emit(self,tick,base_time):
        """
        return a dict of records e.g 
        {
            session_id,
            region,
            timestamp,
            state
        }
        """
        return_dict = {
            "session_id":self.session_id,
            "region": self.region,
            "timestamp": base_time + tick*1_000, #each tick = 1000ms or 1s
            "state": self.state
        }
        return return_dict 
    

def main():

    base_time = int(time.time() * 1_000) # 1000ms makes the tick per sec instead of just a unit

    sessions =  [Session(session_id=str(uuid4()),region=random.choice(REGIONS)) 
                 for _ in range(N_SESSIONS)]

    buffer_counts = {r: 0 for r in REGIONS}
    stall_counts  = {r: 0 for r in REGIONS}
    total_counts  = {r: 0 for r in REGIONS}
    for tick in range(N_TICKS):
        for s in sessions:
            s.advance(tick)
            records = s.emit(tick,base_time)

            total_counts[records["region"]]+=1 

            if records["state"] == PlaybackState.BUFFERING:
                buffer_counts[records["region"]] +=1 
            elif records["state"] == PlaybackState.STALL:
                stall_counts[records["region"]] +=1 
    
    for r in REGIONS:
        total = total_counts[r] 
        buf_ratio = buffer_counts[r]/total if total else 0
        stall_ratio = stall_counts[r]/total if total else 0
        print(f"{r}:buffer={buf_ratio:.2f} stall={stall_ratio:.2f}")
            
if __name__ == "__main__":
    main()



    
            
            