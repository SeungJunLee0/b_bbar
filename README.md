# b_bbar
For test the private LHE files

cmsRun lhe_to_edm.py pwgevents-0001.lhe lhe_0.root

#Run over lhe_{jobid}.root
python3 submit_bbar_2018.py --nJob 1 #--nEvent 10 (default nEvent is set to -1)
cd run/HTCondor_run
./mc_generation_job_0.sh

#Dont forget to run voms-proxy-init for local run, unless cmssw will not find premix samples
