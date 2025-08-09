clear all;
clc;

% Load bobot dan data dari Excel
load bobot3.mat;
Data = xlsread('data.xlsx', 1);

% Pilih data ke-n untuk pelatihan (datake bisa divariasikan)
datake = 1;
input1 = Data(datake, 1);
input2 = Data(datake, 2);
input3 = Data(datake, 3);
target1 = Data(datake, 4);
target2 = Data(datake, 5);
target3 = Data(datake, 6);

% Gabungkan input dan output
Input = [input1; input2; input3];  % Input data
Output = [target1; target2; target3]; % Target data

% Variasi jumlah neuron hidden layer
for hl = 1:10
    % Membuat jaringan dengan struktur [10, 3, 3]
    net = newff(minmax(Input), [10, 3, 3], {'tansig', 'tansig', 'purelin'}, 'trainlm');
    
    % Parameter pelatihan
    net.trainParam.epochs = 1000;   % Jumlah epoch
    net.trainParam.goal = 1e-5;     % Target error
    
    % Pelatihan jaringan
    [net, tr] = train(net, Input, Output);
    
    % Simulasi hasil
    yNN = sim(net, Input);
    
    % Menghitung Mean Squared Error (MSE)
    mseError = perform(net, Output, yNN);
    
    % Menampilkan hasil
    fprintf('Jumlah Neuron HL1: 10, HL2: 3, Output: 3, MSE: %f\n', mseError);
end
