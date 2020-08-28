close all
clear all
clc
tic
fclose('all');
home=pwd;
% Above code cleans the screen and workspace, and starts your code fresh

% Set the filepath to be the folder where the data is kept
% filepath='/Users/ADN/Dropbox/GNI/histogram_final';
%filepath='/Users/ADN/Dropbox/GCCN_Observation_Paper_Data/histogram_final';
filepath='/Users/ADN/Dropbox/mini-GNI/ResultsFromJorgen/Batch2';

allfolders=dir(filepath);
allfolders=allfolders([allfolders.isdir]);
allfolders = allfolders(arrayfun(@(x) x.name(1),allfolders) ~= '.');

% Loops through all the folders
F=1;
for i=1:length(allfolders)
    cd(filepath);cd(allfolders(i).name);
    
    folder=dir;
    folder=folder([folder.isdir]);
    folder=folder(arrayfun(@(x) x.name(1),folder) ~= '.');
    
    % Loops through subfolders
    for j=1:length(folder)
        
        cd(folder(j).name);
        fname=dir;fname = fname(arrayfun(@(x) x.name(1),fname) ~= '.');
        gnifile=fopen(fname.name);
        fname.name
        % gnifile is the name of the file it is reading. The "fname.name
        % line prints the currently opened file on the command line
        
        if gnifile==-1
            fprintf('Failure to open: %s. Program terminated.',fname);
            return;
        end;
        
        % Loop through the first 13 lines, none of which contain
        % information that needs to be saved
        for k=1:13
            trash=fgetl(gnifile);
        end
        
        % Begin grabbing information from the text file lines...
        date=fgetl(gnifile);D(F)=str2num(date(45:52));
        num=fgetl(gnifile);N(F)=str2num(num(48:52));
        starttime=fgetl(gnifile);ST(F)=str2num(starttime(44:53));
        endtime=fgetl(gnifile);ET(F)=str2num(endtime(44:53));
        expo=fgetl(gnifile);X(F)=str2num(expo(48:53));
        vol=fgetl(gnifile);V(F)=str2num(vol(44:57));
        alt=fgetl(gnifile);Z(F)=str2num(alt(44:54));
        pres=fgetl(gnifile);P(F)=str2num(pres(44:54));
        temp=fgetl(gnifile);T(F)=str2num(temp(44:54));
        relhum=fgetl(gnifile);RH(F)=str2num(relhum(44:54));
        wind=fgetl(gnifile);U(F)=str2num(wind(44:54));
        long=fgetl(gnifile);L(F)=str2num(long(44:54));
        colleff=fgetl(gnifile);E(F)=str2num(colleff(44:54));
        
        % Skip a bunch more lines
        for k=1:43
            trash=fgetl(gnifile);
        end
        
        % Now grab the data from the table
        for k=1:100-4
            data=fgetl(gnifile);
            cols=sscanf(data,'%lg');
            B{F}(k)=cols(1);
            LBL{F}(k)=cols(2);
            MBL{F}(k)=cols(3);
            UBL{F}(k)=cols(4);
            Flag{F}(k)=cols(5);
            Conc{F}(k)=cols(6);
        end
        
        for k=1:5
            trash=fgetl(gnifile);
        end
        
        % And finally grab the info under the table
        particleloss=fgetl(gnifile);PL(F)=str2num(particleloss(53:58));
        
        trash=fgetl(gnifile);

        lognormdist=fgetl(gnifile);LND(F)=str2num(lognormdist(50:52));
        lognormN=fgetl(gnifile);LNN(F)=str2num(lognormN(48:57));
        lognormrad=fgetl(gnifile);LNR(F)=str2num(lognormrad(48:57));
        lognormstdev=fgetl(gnifile);LNSD(F)=str2num(lognormstdev(48:57));
        chisq=fgetl(gnifile);CHI(F)=str2num(chisq(53:57));
        
        trash=fgetl(gnifile);

        saltloading=fgetl(gnifile);NACL(F)=str2num(saltloading(51:57));
        
        F=F+1;
        cd ..
              
    end
    
end

%% Mid bin limit vs Concentration, all lines will plot
figure;hold on;
for n=1:length(Conc)
plot(MBL{n},Conc{n})
end
xlim([0 10])

%% Wind speed vs NaCl

figure;hold on;
scatter(U,NACL,'+k','linewidth',2)
xlim([0 20])
ylim([0 40])
set(gca,'fontsize',18)
xlabel('Wind speed during exposure (m s^{-1})','fontsize',18);
ylabel('Sea-salt mass loading (\mug  m^{-3})','fontsize',18)
box on;set(gca,'XMinorTick','on','YMinorTick','on')

x=U;
y=NACL;
[mb r]=polyfit(x,y,1);
plot(x,mb(1).*x+mb(2),'k','linewidth',2)
cc=corrcoef(x,y);CC=cc(1,2);
text(2,38,['Intercept = ',num2str(mb(2))],'fontsize',18)
text(2,35,['Slope = ',num2str(mb(1))],'fontsize',18)
text(2,32,['Corr Coef = ',num2str(CC)],'fontsize',18)
toc
