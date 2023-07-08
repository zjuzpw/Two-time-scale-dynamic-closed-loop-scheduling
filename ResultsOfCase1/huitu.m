clc;clear all
close all
time1 = 0;
time2 = 180;
span = linspace(time1,time2,37);
value = [85000 * ones(1,12),85000 * ones(1,12),85000 * ones(1,13)];
figure
stairs(span,value,'-+','linewidth',2.5)
axis([time1 time2 78000 96000])
title('氧气需求时间序列')
xlabel('时间[min]')
ylabel('需求值[Nm^3/h]')
%%
data1
figure
subplot(221)
plot(span,scheduling(:,1),'k','linewidth',1)
title('ASU1')
axis([time1 time2 18000,22000])
xlabel('t(min)')
ylabel('Load(Nm^3/h)')
subplot(222)
plot(span,scheduling(:,2),'k','linewidth',1)
title('ASU2')
axis([time1 time2 15000,22000])
xlabel('t(min)')
ylabel('Load(Nm^3/h)')
subplot(223)
plot(span,scheduling(:,3),'k','linewidth',1)
title('ASU3')
axis([time1 time2 18000,22000])
xlabel('t(min)')
ylabel('Load(Nm^3/h)')
subplot(224)
plot(span,scheduling(:,4),'k','linewidth',1)
title('ASU4')
axis([time1 time2 26000,34000])
xlabel('t(min)')
ylabel('Load(Nm^3/h)')
%%
xg

D(1) = 30000;
P(1) = 2100000;
D(2) = 30000;
P(2) = 2100000;
for i = 3:37
    D(i)  =  D(i-1) + (scheduling(i,1) + scheduling(i,2) + scheduling(i,3) + scheduling(i,4) - value(i) - Vent(i))*0.083;
    P(i) = P(i-1)+(D(i)-D(i-1))/(volume(i) * 22.4 * 0.001/(8.314 * 273.15)); 
end

figure
plot(span,P0,'-k','linewidth',1)
hold on 
plot(span,P,'-r','linewidth',1)
plot(span,2050000*ones(1,37),'--k','linewidth',1)
plot(span,2150000*ones(1,37),'--k','linewidth',1)
axis([time1,time2,2020000,2170000])
hold off
legend('Predicted pipeline pressure change','Actual pipeline pressure change','Lower bound of pipeline pressure','Upper bound of pipeline pressure')
title('Change of oxygen pipeline pressure')
xlabel('t(min)')
ylabel('Pressure of medium pressure oxygen pipeline(Pa)')

%% disturbance calculate
clear d
const1 =  9.6555 * 0.083;
% P0为预估值 P为实际值
for i = 2:36
    d2(i) = (P0(i+1) - P(i+1) - P0(i) + P(i))/const1;
end
for i = 2:12
    d(i) = (P0(i+1) - P(i+1) - P0(i) + P(i))/const1;
end
d(13) = d(12);
[y,err] = RELS0(1,1,0.995,12,1,13,48,d);
subplot(121)
plot(d2)
subplot(122)
plot(y)
%% 预测是否准确
P_pre(1) = 2100000;
for i = 2:37
    P_pre(i) = P0(i) - P0(i-1) + P_pre(i-1) - y(i-1) * const1; 
end

figure
plot(span,P_pre,'-r','linewidth',1)
hold on 
plot(span,P,'-k','linewidth',1)
plot(span,2050000*ones(1,37),'--k','linewidth',1)
plot(span,2150000*ones(1,37),'--k','linewidth',1)
axis([time1,time2,1950000,2200000])
hold off
legend('Predicted pipline pressure changes after compensation','Actual pipeline pressure change')
title('Change of oxygen pipeline pressure with compensation')
xlabel('t(min)')
ylabel('Pressure of medium pressure oxygen pipeline(Pa)')