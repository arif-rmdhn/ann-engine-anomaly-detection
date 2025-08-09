clc;
clear;

%% Load Data Training NN
     data = xlsread('data.xlsx',1);
% Normalisasi Input dan Output
   Input = data(:,1:3)';
   Output = data(:,4:6)'; 
      err = 1e-5;                       % error awal sebagai constraint 
error_max = 1e-5;                       % batasan error sebagai target trainning
   modmse = 2e2;
   
%% hidden layer (HL) dan Output (O)
%      HL1    HL2    O
 la = [10     3     3];  
 
%% Membentuk jaringan DL
    net=newff(minmax(Input), la, {'tansig','tansig','purelin'},'trainlm')
    %Define parameters
    net.trainParam.show = 10;
    net.trainParam.lr = 0.77;
    net.trainParam.epochs =9000;
    net.trainParam.goal = error_max;
    
% Menampilkan jumlah neuron
    disp(['Unit Layer      =    '  num2str(la)]);
    
% Train network
    struktur = train(net, Input, Output);
    
% Simulate result
   yNN = sim(struktur,Input);
   mIW = struktur.IW{1,1};            % Bobot Layer Input  (IW)
  mLW1 = struktur.LW{2,1};            % Bobot Layer 1      (LW1)
  mLW2 = struktur.LW{3,2};            % Bobot Layer 2      (LW2)
   mBi = struktur.b{1,1};             % Bobot Bias Input   (Bi)
  mBL1 = struktur.b{2,1};             % Bobot Bias Layer 1 (BL1)
  mBL2 = struktur.b{3,1};             % Bobot Bias Layer 2 (BL2)

%% Save into mat ext   
   save bobot3