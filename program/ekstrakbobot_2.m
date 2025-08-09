clear all;
clc;

load bobot3.mat
Data = xlsread('data.xlsx',1);
datake = 3;

input1 = Data(datake,1)
input2 = Data(datake,2)
input3 = Data(datake,3)
target1 = Data(datake,4)
target2 = Data(datake,5)
target3 = Data(datake,6)

mIW  = struktur.IW{1,1};    % 10x3
mLW1 = struktur.LW{2,1};    % 3x10
mLW2 = struktur.LW{3,2};    % 3x3
mBi  = struktur.b{1,1};     % 10x1
mBL1 = struktur.b{2,1};     % 3x1
mBL2 = struktur.b{3,1};     % 3x1

%% Hidden Layer 1 (10 neuron)
nH1 = zeros(10,1);
aH1 = zeros(10,1);
for i = 1:10
    nH1(i) = input1*mIW(i,1) + input2*mIW(i,2) + input3*mIW(i,3) + mBi(i);
    aH1(i) = tansig(nH1(i));
end

%% Hidden Layer 2 (3 neuron)
nH2 = zeros(3,1);
aH2 = zeros(3,1);
for j = 1:3
    for i = 1:10
        nH2(j) = nH2(j) + aH1(i) * mLW1(j,i);
    end
    nH2(j) = nH2(j) + mBL1(j);
    aH2(j) = tansig(nH2(j));
end

%% Output Layer (3 neuron)
nOut = zeros(3,1);
y = zeros(3,1);
for k = 1:3
    for j = 1:3
        nOut(k) = nOut(k) + aH2(j) * mLW2(k,j);
    end
    nOut(k) = nOut(k) + mBL2(k);
    y(k) = round(nOut(k));  % hasil prediksi dibulatkan
end

%% Tampilkan hasil
disp('Hasil prediksi jaringan:');
disp(y);

disp('Target sebenarnya:');
disp([target1; target2; target3]);
