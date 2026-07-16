from pprint import pprint
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
# baseline buffer probability 
# its not 0 as it would mean no session ever buffers no noise
# 0.12 = 12% of time any given session is briefly buffering, which is normal
BASE_P_BUFFER = 0.12

OUTAGE = {
    "region": REGIONS[0],
    "start": 100,  #tick in which outage starts 
    "ends": 120,   #tick at which outage ends
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

    def advance(self,tick):
        """
        Decides the session NEXT state for this tick 
        read self.state -> roll probability _> write self.state
        """
        p = BASE_P_BUFFER

        if ( self.region == OUTAGE.get("region") and
             OUTAGE["start"]<=tick < OUTAGE["ends"]
             ):
            #p = probability of buffering
            p = BASE_P_BUFFER * OUTAGE["severity"] #increases the probability of changing state
        
        # change state
        roll = random.random() 
        if roll < p:
            self.state = PlaybackState.BUFFERING 
        else:
            self.state = PlaybackState.PLAYING 
    
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
    total_counts  = {r: 0 for r in REGIONS}
    for tick in range(N_TICKS):
        for s in sessions:
            s.advance(tick)
            records = s.emit(tick,base_time)

            total_counts[records["region"]]+=1 

            if records["state"] == PlaybackState.BUFFERING:
                buffer_counts[records["region"]] +=1 
    
    for r in REGIONS:
        total = total_counts[r] 
        if total == 0:
            ratio = 0 
        else:
            ratio = buffer_counts[r]/total 
        print(f"{r}:{ratio:.2f}")
            
if __name__ == "__main__":
    main()



    
            
            