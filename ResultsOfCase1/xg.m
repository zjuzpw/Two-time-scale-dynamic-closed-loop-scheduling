sys = tf([1/60],[1,0.015]);
[STP,t]=step(sys);

volume = -STP(1:2:196);

volume = volume * 1500+ 7000;
plot(volume)