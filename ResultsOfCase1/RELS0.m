function [y,err]=RELS0(n,m,lambda,s,N,M,L,y_real)
%%
%n,m是y和e的阶次
clf;
%y_real=xlsread('unmeasured demand.xlsx','Sheet2')';
% y_real=xlsread('差分1-35.xlsx','Sheet2')';
% b=xlsread('积分白噪声1-36.xlsx','Sheet1');
%y_real=1:1000;
%y_real=y_real(1:36);
%b=b(1:35);
y_pred=zeros(1,L);
e_pre=zeros(size(y_pred));%估计误差e_pre
PHI=[];
err_pre=e_pre; %一步预测误差err_pre

P=1*eye(n+m);%n和m是阶次
THE=[];the=[-0.9708;0.1518];%zeros(n+m,1);%;
THE=[THE the];

phi=[-y_real(n:-1:1) e_pre(m:-1:1)];
y_pred(n+1)=phi*the;
% e_pre(n+1)=y_real(n+1)-y_pred(n+1);
% P=zeros(n+m);
% for i=T-20:T-1
%     phi=[-y_real(i-1:-1:i-n) e(i-1:-1:i-m)];
%     P=P+phi'*phi;
%     PHI=[PHI;phi];
% end
% P=inv(P);
% THE=[];
% the=pinv(PHI)*y_real(T-20:T-1)';
% THE=[THE the];
% phi=[-y_real(T-1:-1:T-n) e(T-1:-1:T-m)];
% y_pred(T)=phi*the;

for t=n+1:13 %s是迭代的阶数
    err_pre(t)=y_real(t)-phi*the;
     
    c=1/(lambda+phi*P*phi');
    P=(P-P*(phi'*phi)*P*c)/lambda;
    K=P*phi';
    the=the+K*err_pre(t);
    
    e_pre(t)=y_real(t)-phi*the;  
    THE=[THE the];
    phi=[-y_real(t:-1:t-n+1) e_pre(t:-1:t-m+1)];
    y_pred(t+1)=phi*the;  
    
end
figure(1);
plot(y_pred(1:s));
hold on;
plot(y_real);

y_pred(1:s)=y_real(1:s);
for t=s:N:L-M  
    for tt=t+1:t+M
        phi=[-y_pred(tt-1:-1:tt-n) e_pre(tt-1:-1:tt-m)];
        y_pred(tt)=phi*the;
        if(tt<=length(y_real))
            err_pre(tt)=y_real(tt)-y_pred(tt);
        else
            err_pre(tt)=0;
        end
    end
    plot(t+1:t+M,y_pred(t+1:t+M));
    y1=y_pred(t+1:t+M);
    for i=2:length(y1)
        y1(i)=y1(i)+y1(i-1);
    end
   % b=b(1:10:991);
   % y1=y1+b(s);
    delete('y_pred.xlsx');
    xlswrite('y_pred.xlsx',y_pred','Sheet1');  
    xlswrite('y_pred.xlsx',y1','Sheet2'); 
    figure(2);
%     plot(b);
    hold on;
    plot(s+1:s+length(y1),y1);
    y = y_pred
    err = the
end