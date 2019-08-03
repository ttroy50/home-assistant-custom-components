# Virgin Media

Monitors the downstream signal of the Virgin Media Hub 3 to check for bad signal to noise ratio and power level

To configure add

```
- platform: virgin_hub
  ip_addr: 192.168.100.1
  rxmer_threshold: 30 # Will report status as BRX if below this
  postrs_threshold: 10000 # Will report status as PRS if above this
```

to your sensor config. 

States are:

  * OK - all ok
  * NC - Could not contact model
  * BRX - We  have a channel below the rxmer threshold
  * PRS - We have a channel above the PostRS threshold (but not below rxmer threshold)
