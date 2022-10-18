% 此代码对1，2数据进行预处理
% 读取原始数据
x = readmatrix('C:\Users\cug-auto-zp\Desktop\2021华为PCIC：Causal Discovery\phase2\datasets_phase2\data phase2\1\Alarm.csv')
% 对数据进行排列
x = sortrows(x,[1,2])
n = max(x(:,1:2))
m=length(x);
a=1;c=3;b=c;
% 数据剔除，剔除只出现两次及以下的报警数据
for i=1:m-1
    if (x(i+1,1)==x(i,1) && x(i+1,2)==x(i,2))
        a=a+1;
    else
        b=a;
        a=1;
    end
    if(x(m,2) ~= x(m-1,2))
        x(m,:)=0;
    end
    if b<c
       for j=1:b
           x(i-j+1,:)=0;
       end
       b=c;
    end
end    

x = sortrows(x,[1,3]);
x = sortrows(x,[1,2])

for i=length(x):-1:1
    if x(i,:)==0
        x(i,:)=[];
    end
end

% 保存数据
writematrix(x,'C:\Users\cug-auto-zp\Desktop\2021华为PCIC：Causal Discovery\数据预处理\Alarm1_1.csv')

