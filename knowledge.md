# Building a QoE outage detector 
> It sends alert's if there is a outage in a cdn region 

## Outage
--- 
- Per-session Degradation = THis is normal, one viewer bnuffering/stalling indiviual 
  bad connections happen constantly. The dector should just ignore it, its just noise.
- A Regional Outage = manny session in the same region degrading at the same time. One
  viewer stalling in `asia-mumbai` is nothing, but say 10% of users stalling in the same 
  window (say 30s) is an oputage 

> SO outage is not a property of one event, it a property of correlated clusterd of events
> sharing a region and a time window. 

== So the similator needs to be able to make whole region go down at once == 

## A tick 
> A tick i sone step of simulated time - one heartbeat on the simlation's clock 
The simulator doenst just run in continous,flowing time. It advances in discrete
jumps. If
``` 1 tick = 1 secound of simulated palyback ``` 
So tick 0 is 0 sec,tick1  is one sec ... tick 120 is 120 sec 

## WQhat happens each tick 
> At every tick the simulator sweeps thpooughs every active session and ask 
> "What's the sessions state now"? Now each session then emits one event 
>  describing its current state
So if i have 20 sessions and simulate for say 300 ticks then i have 
- Each tick produces 20 events 
- 300 ticks x 20 session = 6,000 events total  

# The parts of the simulator 
- **CONFIG** = how many session,how many regions, what are the transition odds 
               and the outage plan( whcih regions,which ticks and how severe)
- **SESSIONS** = a population of viewers. each one has 
    - its own identity (session_id,region,content)
    - == memory (its current state: playing/buffer/stall) ==
    each viewer knows how to advance itself one step 
- THE CLOCK ( the vent generator)
    for each tick in time:
        for each session:
            advance it one step = (update intenal memory. Decide what state I am in now
            prossibly cahnging to some other state)
            emit one vent = (report my current sate to the outrside)
    will produce a steam of event dict 
    ```json 
    {
        {
            session_id:
            region: value,
            timestamp: current_timestamp()
            state: playing/buffering/stalling 
        },
        
    }
    ```

```text
BASELINE NOISE          every session, every tick, a small
(Mechanism A)           independent chance of hiccuping on its own
                        → constant low-level buffering everywhere
                        → this is "normal," the thing to NOT alert on

INJECTED OUTAGE         one region, one window, degrade odds cranked up
(Mechanism B)           → a concentrated burst of buffering in one place
                        → this is the SIGNAL, the thing to catch
```

-> To dsetect the outage across a region we have to tally up 
the buffering-rate per region per time window, e.g 
```
window     region-A   region-B   region-C(doomed)
0–60         0.11       0.13        0.12
60–120       0.12       0.11        0.13
120–180      0.12       0.12        0.58   ← there it is
180–240      0.13       0.12        0.14
```
-> THat spike indicate region-C experianced an outage 

## What advance one step actaully means 
```
I am currently "playing"
   → roll: small chance I slip to "buffering", otherwise stay "playing"

I am currently "buffering"
   → roll: might recover to "playing", might worsen to "stall", might stay

I am currently "stalled"
   → roll: probably stay stuck (stalls are sticky), small chance I recover 

```