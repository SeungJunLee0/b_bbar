#!/bin/bash

source /cvmfs/grid.desy.de/etc/profile.d/grid-ui-env.sh

# Dump all code into 'MC_Generation_Script_0.sh'
cat <<'EndOfMCGenerationFile' > MC_Generation_Script_0.sh
#!/bin/bash

### Job configuration ###
echo "Processing job number 0 ... "
export X509_USER_PROXY=/afs/cern.ch/user/s/seungjun/private/b_bbar/run/.voms_proxy
export HOME=/afs/cern.ch/user/s/seungjun/private
CWD=`pwd -P`
mkdir -p /tmp/job_0
cd /tmp/job_0

### GEN-SIM step ###
export SCRAM_ARCH=slc6_amd64_gcc481
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_7_1_43/src ] ; then
  echo release CMSSW_7_1_43 already exists
else
  scram p CMSSW CMSSW_7_1_43
fi
cd CMSSW_7_1_43/src
eval `scram runtime -sh`
[ ! -d Configuration/GenProduction/python ] && mkdir -p Configuration/GenProduction/python
cp /afs/cern.ch/user/s/seungjun/private/b_bbar/run/fragments/tLepWLepZinvLO-madgraph-mcatnlo-pythia8.py Configuration/GenProduction/python/PY8_fragment.py
scram b
cd ../..
cmsDriver.py Configuration/GenProduction/python/PY8_fragment.py --python_filename GEN-SIM_cfg.py \
             --eventcontent RAWSIM,LHE --customise SLHCUpgradeSimulations/Configuration/postLS1Customs.customisePostLS1,Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM,LHE \
             --fileout file:GEN-SIM.root \
             --conditions MCRUN2_71_V1::All --beamspot Realistic50ns13TeVCollision \
             --customise_commands process.source.numberEventsInLuminosityBlock="cms.untracked.uint32(100)"\\nprocess.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(56650)"\\nprocess.RandomNumberGeneratorService.generator.initialSeed="int(16226)"\\nprocess.RandomNumberGeneratorService.VtxSmeared.initialSeed="int(58729)"\\nprocess.RandomNumberGeneratorService.LHCTransport.initialSeed="int(75790)"\\nprocess.RandomNumberGeneratorService.hiSignalLHCTransport.initialSeed="int(94715)"\\nprocess.RandomNumberGeneratorService.g4SimHits.initialSeed="int(39310)"\\nprocess.RandomNumberGeneratorService.mix.initialSeed="int(69601)"\\nprocess.RandomNumberGeneratorService.mixData.initialSeed="int(62569)"\\nprocess.RandomNumberGeneratorService.simSiStripDigiSimLink.initialSeed="int(40552)"\\nprocess.RandomNumberGeneratorService.simMuonDTDigis.initialSeed="int(88597)"\\nprocess.RandomNumberGeneratorService.simMuonCSCDigis.initialSeed="int(39094)"\\nprocess.RandomNumberGeneratorService.simMuonRPCDigis.initialSeed="int(75453)"\\n \
             --step LHE,GEN,SIM --magField 38T_PostLS1 --no_exec --mc -n 100000 || exit $? ;
cmsRun GEN-SIM_cfg.py || exit $? ;

### PREMIX step ###
export SCRAM_ARCH=slc6_amd64_gcc530
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_8_0_31/src ] ; then
  echo release CMSSW_8_0_31 already exists
else
  scram p CMSSW CMSSW_8_0_31
fi
cd CMSSW_8_0_31/src
eval `scram runtime -sh`
scram b
cd ../..
cmsDriver.py --python_filename PREMIX_cfg.py \
             --eventcontent PREMIXRAW --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM-RAW \
             --filein file:GEN-SIM.root --fileout file:PREMIX.root \
             --pileup_input "dbs:/Neutrino_E-10_gun/RunIISpring15PrePremix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v2-v2/GEN-SIM-DIGI-RAW" \
             --conditions 80X_mcRun2_asymptotic_2016_TrancheIV_v6 \
             --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(3998)"\\nprocess.RandomNumberGeneratorService.generator.initialSeed="int(86489)"\\nprocess.RandomNumberGeneratorService.VtxSmeared.initialSeed="int(95925)"\\nprocess.RandomNumberGeneratorService.LHCTransport.initialSeed="int(10215)"\\nprocess.RandomNumberGeneratorService.hiSignalLHCTransport.initialSeed="int(374)"\\nprocess.RandomNumberGeneratorService.g4SimHits.initialSeed="int(74181)"\\nprocess.RandomNumberGeneratorService.mix.initialSeed="int(68357)"\\nprocess.RandomNumberGeneratorService.mixData.initialSeed="int(86711)"\\nprocess.RandomNumberGeneratorService.simSiStripDigiSimLink.initialSeed="int(5807)"\\nprocess.RandomNumberGeneratorService.simMuonDTDigis.initialSeed="int(60939)"\\nprocess.RandomNumberGeneratorService.simMuonCSCDigis.initialSeed="int(95313)"\\nprocess.RandomNumberGeneratorService.simMuonRPCDigis.initialSeed="int(37423)"\\n \
             --step DIGIPREMIX_S2,DATAMIX,L1,DIGI2RAW,HLT:@frozen2016 --datamix PreMix --era Run2_2016 --no_exec --mc -n 100000 || exit $? ;
cmsRun PREMIX_cfg.py || exit $? ;

### AOD step ###
cmsDriver.py --python_filename AOD_cfg.py \
             --eventcontent AODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier AODSIM \
             --filein file:PREMIX.root --fileout file:AOD.root \
             --conditions 80X_mcRun2_asymptotic_2016_TrancheIV_v6 \
             --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(73112)"\\nprocess.RandomNumberGeneratorService.generator.initialSeed="int(24555)"\\nprocess.RandomNumberGeneratorService.VtxSmeared.initialSeed="int(33775)"\\nprocess.RandomNumberGeneratorService.LHCTransport.initialSeed="int(29455)"\\nprocess.RandomNumberGeneratorService.hiSignalLHCTransport.initialSeed="int(95931)"\\nprocess.RandomNumberGeneratorService.g4SimHits.initialSeed="int(74028)"\\nprocess.RandomNumberGeneratorService.mix.initialSeed="int(97558)"\\nprocess.RandomNumberGeneratorService.mixData.initialSeed="int(88160)"\\nprocess.RandomNumberGeneratorService.simSiStripDigiSimLink.initialSeed="int(8510)"\\nprocess.RandomNumberGeneratorService.simMuonDTDigis.initialSeed="int(75365)"\\nprocess.RandomNumberGeneratorService.simMuonCSCDigis.initialSeed="int(66622)"\\nprocess.RandomNumberGeneratorService.simMuonRPCDigis.initialSeed="int(68371)"\\n \
             --step RAW2DIGI,RECO,EI --era Run2_2016 --runUnscheduled --no_exec --mc -n 100000 || exit $? ;
cmsRun AOD_cfg.py || exit $? ;

### MINIAOD step ####
export SCRAM_ARCH=slc6_amd64_gcc630
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_9_4_9/src ] ; then
  echo release CMSSW_9_4_9 already exists
else
  scram p CMSSW CMSSW_9_4_9
fi
cd CMSSW_9_4_9/src
eval `scram runtime -sh`
scram b
cd ../..
cmsDriver.py --python_filename MINIAOD_cfg.py \
             --eventcontent MINIAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier MINIAODSIM \
             --filein file:AOD.root --fileout file:MINIAOD.root \
             --conditions 94X_mcRun2_asymptotic_v3 \
             --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(94313)"\\nprocess.RandomNumberGeneratorService.generator.initialSeed="int(36386)"\\nprocess.RandomNumberGeneratorService.VtxSmeared.initialSeed="int(39874)"\\nprocess.RandomNumberGeneratorService.LHCTransport.initialSeed="int(75697)"\\nprocess.RandomNumberGeneratorService.hiSignalLHCTransport.initialSeed="int(59216)"\\nprocess.RandomNumberGeneratorService.g4SimHits.initialSeed="int(15037)"\\nprocess.RandomNumberGeneratorService.mix.initialSeed="int(75461)"\\nprocess.RandomNumberGeneratorService.mixData.initialSeed="int(53839)"\\nprocess.RandomNumberGeneratorService.simSiStripDigiSimLink.initialSeed="int(53599)"\\nprocess.RandomNumberGeneratorService.simMuonDTDigis.initialSeed="int(25363)"\\nprocess.RandomNumberGeneratorService.simMuonCSCDigis.initialSeed="int(74539)"\\nprocess.RandomNumberGeneratorService.simMuonRPCDigis.initialSeed="int(40604)"\\n \
             --step PAT --era Run2_2016,run2_miniAOD_80XLegacy --runUnscheduled --no_exec --mc -n 100000 || exit $? ;
cmsRun MINIAOD_cfg.py || exit $? ;

### NANOAOD step ###
export SCRAM_ARCH=slc6_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_2_22/src ] ; then
  echo release CMSSW_10_2_22 already exists
else
  scram p CMSSW CMSSW_10_2_22
fi
cd CMSSW_10_2_22/src
eval `scram runtime -sh`
scram b
cd ../..
cmsDriver.py --python_filename NANOAOD_cfg.py \
             --eventcontent NANOAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM \
             --filein file:MINIAOD.root --fileout file:NANOAOD.root \
             --conditions 102X_mcRun2_asymptotic_v8 \
             --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(52193)"\\nprocess.RandomNumberGeneratorService.generator.initialSeed="int(8356)"\\nprocess.RandomNumberGeneratorService.VtxSmeared.initialSeed="int(47593)"\\nprocess.RandomNumberGeneratorService.LHCTransport.initialSeed="int(59803)"\\nprocess.RandomNumberGeneratorService.hiSignalLHCTransport.initialSeed="int(75852)"\\nprocess.RandomNumberGeneratorService.g4SimHits.initialSeed="int(13405)"\\nprocess.RandomNumberGeneratorService.mix.initialSeed="int(36599)"\\nprocess.RandomNumberGeneratorService.mixData.initialSeed="int(37022)"\\nprocess.RandomNumberGeneratorService.simSiStripDigiSimLink.initialSeed="int(2315)"\\nprocess.RandomNumberGeneratorService.simMuonDTDigis.initialSeed="int(69333)"\\nprocess.RandomNumberGeneratorService.simMuonCSCDigis.initialSeed="int(32252)"\\nprocess.RandomNumberGeneratorService.simMuonRPCDigis.initialSeed="int(30994)"\\n \
             --step NANO --era Run2_2016,run2_nanoAOD_94X2016 --no_exec --mc -n 100000 || exit $? ;
cmsRun NANOAOD_cfg.py || exit $? ;

### Saving NANOAOD files ###
[ ! -d /afs/cern.ch/user/s/seungjun/private/b_bbar/out/tLepWLepZinvLO-madgraph-mcatnlo-pythia8 ] && mkdir -p /afs/cern.ch/user/s/seungjun/private/b_bbar/out/tLepWLepZinvLO-madgraph-mcatnlo-pythia8
mv NANOAOD.root /afs/cern.ch/user/s/seungjun/private/b_bbar/out/tLepWLepZinvLO-madgraph-mcatnlo-pythia8/NANOAOD_0.root

### Cleaning ###
cd $CWD
rm -rf /tmp/job_0
echo "shell script has finished"

# End of MC_Generation_Script_0.sh
EndOfMCGenerationFile

# Make file executable
chmod +x MC_Generation_Script_0.sh

# Run in SLC6 container
export SINGULARITY_CACHEDIR="/tmp/$(whoami)/singularity"
singularity run -B /afs -B /nfs -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:amd64 $(echo $(pwd)/MC_Generation_Script_0.sh)
