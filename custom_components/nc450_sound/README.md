# TPLink NC450 Sound

Can be used to get the sound levels from a TPLink NC450 camera.

To configure add

```
- platform: nc450_sound
  ip_address: 192.168.100.11
  password: !secret tplink
  name: hall_camera
```

to your sensor config. 

If the camera is turned off a sound level of 0 is returned and the attribute `sound` is set to `false`
