import random
from enum import Enum
import time
from uuid import uuid4

TICK_SECONDS = 0.1
# cdn regions
REGIONS = [
    "iad-01",  # US East
    "lhr-01",  # Europe West
    "fra-01",  # Europe Central
    "sin-01",  # Asia Pacific
    "bom-01",  # India
]
P_TO_B_BUFFER = 0.12  # PLAYING->BUFFERING chance (outage probability) base outage buffer,#entry rate
B_TO_P_BUFFER = 0.30  # BUFFERING->PLAYING chance #drain rate
B_TO_S_BUFFER = 0.05  # BUFFERING -> STALL chance
S_TO_B_BUFFER = 0.20  # STALL -> BUFFERING chance

OUTAGE_CHANCE = 0.01      # per-tick chance an outage starts

N_SESSION = 10

class PlaybackState(Enum):
    PLAYING = "playing"
    BUFFERING = "buffering"
    STALL = "stall"


class Session:
    def __init__(self, session_id: str, region: str):

        self.session_id: str = session_id
        self.region: str = region
        self.state: PlaybackState = PlaybackState.PLAYING

    def state_transition(self, buffering: float):
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
            # all 3 states possible
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

    def advance(self, outage_region,outage_severity):
        """
        Decides the session NEXT state for this tick
        read self.state -> roll probability _> write self.state
        """
        p_to_b_buffer = P_TO_B_BUFFER
        if self.region == outage_region:
           p_to_b_buffer = P_TO_B_BUFFER * outage_severity # increases the probability of buffering for this region
        # change state
        self.state_transition(p_to_b_buffer)

    def emit(self):
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
            "session_id": self.session_id,
            "region": self.region,
            "timestamp": int(time.time() * 1_000),  # time elapsed since 1 Jan 1970 in ms
            "state": self.state.value, 
        }
        return return_dict


def main():
 

    sessions = [
        Session(session_id=str(uuid4()), region=random.choice(REGIONS))
        for _ in range(N_SESSION)
    ]
    tick = 0
    outage_region = None 
    outage_ticks_left = 0 
    outage_severity = 1
    try:
        while True:
            #if experiencing current outage 
            if outage_ticks_left > 0:
                outage_ticks_left-=1
                if outage_ticks_left == 0:
                    outage_region = None

            #if no outage roll the dice to start one 
            elif random.random() < OUTAGE_CHANCE:
                outage_region = random.choice(REGIONS)
                outage_ticks_left = random.randint(60,120) # duration of outage
                outage_severity = random.randint(2,5)
 
            for s in sessions:
                s.advance(outage_region,outage_severity)
                records = s.emit()
                # producer goes here later
                print(records)
            tick += 1
            time.sleep(TICK_SECONDS)
    except KeyboardInterrupt:
        print("*" * 6 + "---INTERRUPTED---" + "*" * 6)

if __name__ == "__main__":
    main()
