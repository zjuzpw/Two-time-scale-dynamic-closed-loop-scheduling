clc;
time1 = 0;
time2 = 180;
span = linspace(time1,time2,37);
figure
plot(span,a1,'-r','linewidth',1)
hold on 
plot(span,a2,'-k','linewidth',1)
plot(span,2050000*ones(1,37),'--k','linewidth',1)
plot(span,2150000*ones(1,37),'--k','linewidth',1)
axis([time1,time2,1950000,2200000])
hold off
legend('Predicted pipline pressure','Actual pipeline pressure','Lower bound of pipeline pressure','Upper bound of pipeline pressure')
%title('Change of oxygen pipeline pressure with compensation')
xlabel('t(min)')
ylabel('Oxygen pipeline pressure(Pa)')