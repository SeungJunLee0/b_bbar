#!/usr/bin/env python3

import os
import sys
import time
import glob
import json
import random
from argparse import ArgumentParser

work_dir = f"/afs/cern.ch/user/s/seungjun/private/b_bbar/run"
run_dir = f"{work_dir}/HTCondor_run"
output_dir = f"/afs/cern.ch/user/s/seungjun/private/b_bbar/out"

####################################################################################
def get_fragment(gridpack_path):
####################################################################################
    
    fragment=''
    fragment+=f'''import FWCore.ParameterSet.Config as cms
externalLHEProducer = cms.EDProducer("ExternalLHEProducer",
    args = cms.vstring('/cvmfs/cms.cern.ch/phys_generator/gridpacks/2017/13TeV/powheg/V2/TT_hvq/TT_hdamp_NNPDF31_NNLO_dilepton.tgz'),
    nEvents = cms.untracked.uint32(5000),
    numberOfParameters = cms.uint32(1),
    outputFile = cms.string('cmsgrid_final.lhe'),
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
)
process=cms.Process("TEST")
process.source = cms.Source("LHESource",
    fileNames = cms.untracked.vstring('file:/afs/cern.ch/user/s/seungjun/private/lhe_product/pwgevents-0001.lhe')
)

from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *
from Configuration.Generator.Pythia8PowhegEmissionVetoSettings_cfi import *
#from Configuration.Generator.Pythia8aMCatNLOSettings_cfi import *
from Configuration.Generator.PSweightsPythia.PythiaPSweightsSettings_cfi import *

generator = cms.EDFilter("Pythia8HadronizerFilter",
                         maxEventsToPrint = cms.untracked.int32(1),
                         pythiaPylistVerbosity = cms.untracked.int32(1),
                         filterEfficiency = cms.untracked.double(1.0),
                         pythiaHepMCVerbosity = cms.untracked.bool(False),
                         comEnergy = cms.double(13000.),
                         PythiaParameters = cms.PSet(
                              pythia8CommonSettingsBlock,
                              pythia8CP5SettingsBlock,
                              pythia8PowhegEmissionVetoSettingsBlock,
                              pythia8PSweightsSettingsBlock,
                              processParameters = cms.vstring(
                                          'POWHEG:nFinal = 2', ## Number of final state particles
                                          ## (BEFORE THE DECAYS) in the LHE
                                          ## other than emitted extra parton
                                          'TimeShower:mMaxGamma = 1.0',#cutting off lepton-pair production
                                          ##in the electromagnetic shower
                                          ##to not overlap with ttZ/gamma* samples
                                          '6:m0 = 172.5',    # top mass'
                                                  ),
                              parameterSets = cms.vstring('pythia8CommonSettings',
                                          'pythia8CP5Settings',
                                          'pythia8PowhegEmissionVetoSettings',
                                          'pythia8PSweightsSettings',
                                          'processParameters'
                                          )


                         )
)
ProductionFilterSequence = cms.Sequence(generator)'''

    return fragment

####################################################################################
def get_shell_script(dataset_name, nEvents, fragment_path, job_id):
####################################################################################
    
    script=''
    script+=f'''#!/bin/bash

#source /cvmfs/grid.desy.de/etc/profile.d/grid-ui-env.sh

# Dump all code into 'MC_Generation_Script_{job_id}.sh'
cat <<'EndOfMCGenerationFile' > MC_Generation_Script_{job_id}.sh
#!/bin/bash

### Job configuration ###
echo "Processing job number {job_id} ... "
export X509_USER_PROXY={work_dir}/.voms_proxy
export HOME=/afs/cern.ch/user/s/seungjun/private
CWD=`pwd -P`
mkdir -p /tmp/seungjun/job_{job_id}
cd /tmp/seungjun/job_{job_id}

### GEN-SIM step ###

export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_6_17_patch1/src ] ; then
  echo release CMSSW_10_6_17_patch1 already exists
else
  scram p CMSSW CMSSW_10_6_17_patch1
fi
cd CMSSW_10_6_17_patch1/src
eval 'cmsenv'
eval `scram runtime -sh`

[ ! -d Configuration/GenProduction/python ] && mkdir -p Configuration/GenProduction/python
cp {fragment_path} Configuration/GenProduction/python/PY8_fragment.py
scram b
cd ../..

cmsDriver.py Configuration/GenProduction/python/PY8_fragment.py --python_filename GEN-SIM_cfg.py \\
             --eventcontent RAWSIM,LHE --customise SLHCUpgradeSimulations/Configuration/postLS1Customs.customisePostLS1,Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM,LHE \\
             --fileout file:GEN-SIM.root \\
             --conditions   106X_upgrade2018_realistic_v11_L1v1 --beamspot Realistic25ns13TeVEarly2018Collision \\
             --customise_commands process.source.numberEventsInLuminosityBlock="cms.untracked.uint32(100)"\\\\n\
#process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.generator.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.VtxSmeared.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.LHCTransport.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.hiSignalLHCTransport.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.g4SimHits.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.mix.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.mixData.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simSiStripDigiSimLink.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simMuonDTDigis.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simMuonCSCDigis.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simMuonRPCDigis.initialSeed="int({int(random.random()*100000)})"\\\\n \\
             --step LHE,GEN,SIM --no_exec --mc -n {nEvents} || exit $? ;
cmsRun GEN-SIM_cfg.py || exit $? ;

### PREMIX step ###
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_6_17_patch1/src ] ; then
  echo release CMSSW_10_6_17_patch1 already exists
else
  scram p CMSSW CMSSW_10_6_17_patch1
fi
cd CMSSW_10_6_17_patch1/src
eval `scram runtime -sh`

scram b
cd ../..
cmsDriver.py --python_filename PREMIX_cfg.py \\
             --eventcontent PREMIXRAW --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM-RAW \\
             --filein file:GEN-SIM.root --fileout file:PREMIX.root \\
             --pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer20ULPrePremix-UL18_106X_upgrade2018_realistic_v11_L1v1-v2/PREMIX"
             --conditions 106X_upgrade2018_realistic_v11_L1v1
             --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.generator.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.VtxSmeared.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.LHCTransport.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.hiSignalLHCTransport.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.g4SimHits.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.mix.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.mixData.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simSiStripDigiSimLink.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simMuonDTDigis.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simMuonCSCDigis.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simMuonRPCDigis.initialSeed="int({int(random.random()*100000)})"\\\\n \\
             --step DIGIPREMIX_S2,DATAMIX,L1,DIGI2RAW,HLT:@frozen2016 --datamix PreMix --era Run2_2018 --no_exec --mc -n {nEvents} || exit $? ;
cmsRun PREMIX_cfg.py || exit $? ;

### AOD step ###
cmsDriver.py --python_filename AOD_cfg.py \\
             --eventcontent AODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier AODSIM \\
             --filein file:PREMIX.root --fileout file:AOD.root \\
             --conditions 106X_upgrade2018_realistic_v11_L1v1 \\
             --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.generator.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.VtxSmeared.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.LHCTransport.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.hiSignalLHCTransport.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.g4SimHits.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.mix.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.mixData.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simSiStripDigiSimLink.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simMuonDTDigis.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simMuonCSCDigis.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simMuonRPCDigis.initialSeed="int({int(random.random()*100000)})"\\\\n \\
             --step RAW2DIGI,RECO,EI --era Run2_2018 --runUnscheduled --no_exec --mc -n {nEvents} || exit $? ;
cmsRun AOD_cfg.py || exit $? ;

### MINIAOD step ####
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_6_20/src ] ; then
  echo release CMSSW_10_6_20 already exists
else
  scram p CMSSW CMSSW_10_6_20
fi
cd CMSSW_10_6_20/src
eval `scram runtime -sh`

scram b
cd ../..

cmsDriver.py --python_filename MINIAOD_cfg.py \\
             --eventcontent MINIAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier MINIAODSIM \\
             --filein file:AOD.root --fileout file:MINIAOD.root \\
             --conditions 106X_upgrade2018_realistic_v16_L1v1 
             --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.generator.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.VtxSmeared.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.LHCTransport.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.hiSignalLHCTransport.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.g4SimHits.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.mix.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.mixData.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simSiStripDigiSimLink.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simMuonDTDigis.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simMuonCSCDigis.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simMuonRPCDigis.initialSeed="int({int(random.random()*100000)})"\\\\n \\
             --step PAT --era Run2_2018,run2_miniAOD_106XLegacy --runUnscheduled --no_exec --mc -n {nEvents} || exit $? ;
cmsRun MINIAOD_cfg.py || exit $? ;

### NANOAOD step ###
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_6_26/src ] ; then
  echo release CMSSW_10_6_26 already exists
else
  scram p CMSSW CMSSW_10_6_26
fi
cd CMSSW_10_6_26/src
eval `scram runtime -sh`

scram b
cd ../..

cmsDriver.py --python_filename NANOAOD_cfg.py \\
             --eventcontent NANOAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM \\
             --filein file:MINIAOD.root --fileout file:NANOAOD.root \\
             --conditions 106X_upgrade2018_realistic_v16_L1v1 
             --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.generator.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.VtxSmeared.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.LHCTransport.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.hiSignalLHCTransport.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.g4SimHits.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.mix.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.mixData.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simSiStripDigiSimLink.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simMuonDTDigis.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simMuonCSCDigis.initialSeed="int({int(random.random()*100000)})"\\\\n\
process.RandomNumberGeneratorService.simMuonRPCDigis.initialSeed="int({int(random.random()*100000)})"\\\\n \\
             --step NANO --era Run2_2018,run2_nanoAOD_106Xv2 --no_exec --mc -n {nEvents} || exit $? ;
cmsRun NANOAOD_cfg.py || exit $? ;

### Saving NANOAOD files ###
[ ! -d {output_dir}/{dataset_name} ] && mkdir -p {output_dir}/{dataset_name}
mv NANOAOD.root {output_dir}/{dataset_name}/NANOAOD_{job_id}.root

### Cleaning ###
cd $CWD
rm -rf /tmp/seungjun/job_{job_id}
echo "shell script has finished"

# End of MC_Generation_Script_{job_id}.sh
EndOfMCGenerationFile

# Make file executable
chmod +x MC_Generation_Script_{job_id}.sh

# Run in SLC6 container
export SINGULARITY_CACHEDIR="/tmp/$(whoami)/singularity"
singularity run -B /afs -B /nfs -B /cvmfs -B /etc/grid-security --home $PWD:$PWD /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/slc6:amd64 $(echo $(pwd)/MC_Generation_Script_{job_id}.sh)
'''
    
    return script

####################################################################################
def get_condor_submit_file(run_dir, nJobs):
####################################################################################
    
    script_name = run_dir + "/mc_generation_job"
    
    file=''
    file+=f'+RequestRuntime       = 85000\n'
    file+=f'RequestMemory         = 2000\n'
    file+=f'universe              = vanilla\n'
    file+=f'executable            = {script_name}_$(ProcId).sh\n'
    file+=f'output                = {script_name}_$(ProcId).out\n'
    file+=f'error                 = {script_name}_$(ProcId).err\n'
    file+=f'log                   = {script_name}_$(ProcId).log\n'
    file+=f'transfer_executable   = True\n'
    file+=f'queue {nJobs}\n'
    
    return file

####################################################################################
def get_find_script(output_dir, subdir_list, nJobs):
####################################################################################
    
    dirs_to_look = ''
    for d in subdir_list:
        dirs_to_look+=f'{output_dir}/{d} '
    
    file=''
    file+='#!/bin/sh\n\n'
    file+='#  @1  -->  "resubmit" for resubmition\n\n'
    file+='find '+dirs_to_look+'-name "*.root" > find_tmp\n\n'
    file+='array=()\n'
    file+='n_miss_job=0\n'
    file+='for j in {0..'+str(nJobs-1)+'}\n'
    file+='do\n'
    file+='if ! grep -q "_"${j}".root" find_tmp\n'
    file+='then\n'
    file+='    array+=(${j})\n'
    file+='    let n_miss_job++\n'
    file+='fi\n'
    file+='done\n\n'
    file+='echo ""\n'
    file+='echo "The number of missing files is: "${n_miss_job}\n'
    file+='echo ""\n'
    file+='echo "The jobs failed are: ${array[@]}"\n'
    file+='echo ""\n\n\n'
    file+='if [ "${1}" = "resubmit" ]\n'
    file+='then\n'
    file+='    [ -d resubmit ] && rm -rf resubmit\n'
    file+='    mkdir resubmit\n'
    file+='    n_sub_job=0\n'
    file+='    for j in ${array[@]}\n'
    file+='    do\n'
    file+='        cp mc_generation_job_${j}.sh resubmit/mc_generation_job_${n_sub_job}.sh\n'
    file+='        let n_sub_job++\n'
    file+='    done\n'
    file+='    cd resubmit\n'
    file+='    cp ../mc_generation_jobs.submit .\n'
    file+="    sed -i 's|HTCondor_run|HTCondor_run/resubmit|g' mc_generation_jobs.submit\n"
    file+="    sed -i 's|"+str(nJobs)+"|'${n_sub_job}'|g' mc_generation_jobs.submit\n"
    file+='    cd ../\n\n\n'
    file+='    echo "Jobs ready to be re-submitted in '+"'resubmit'"+' directory ... "\n'
    file+='fi\n\n'
    file+='echo ""\n\n'
    file+='rm find_tmp\n\n'
    file+='echo "done."\n\n'
    file+='echo ""\n'

    return file

####################################################################################
def main():
####################################################################################
    
    parser = ArgumentParser(description="Generate MC Events")
    parser.add_argument("--nJob", type=int, required=True, help="number of jobs per dataset")
    parser.add_argument("--nEvent", type=int, required=True, help="number of events per job (nTot_dataset = nEvent x nJob)")
    args = parser.parse_args()
    
    os.system(f"voms-proxy-init --voms cms -valid 192:00 --out {work_dir}/.voms_proxy")
    
    if(not os.path.exists(run_dir)):
        os.system(f"mkdir {run_dir}")
    else:
        os.system(f"rm -rf {run_dir}/*")
    
    fragment_dir = f'{work_dir}/fragments'
    if(not os.path.exists(fragment_dir)):
        os.system(f"mkdir {fragment_dir}")
    else:
        os.system(f"rm -rf {fragment_dir}/*")
    
    gridpack_dict = {
    'tLepWLepZinvLO-madgraph-mcatnlo-pythia8':'/afs/cern.ch/user/s/seungjun/private/lhe_product/pwgevents-0001.lhe',
    #'tLepWLepZinvLO-madgraph-mcatnlo-pythia8':'/nfs/dust/cms/user/stafford/tWZ_gen/slc6_gen_prod/genproductions/bin/MadGraph5_aMCatNLO/tLepWLepZinvLO_slc6_amd64_gcc700_CMSSW_10_2_24_patch1_tarball.tar.xz',
    }
    job_id=0
    for dataset in gridpack_dict.keys():
        
        with open(f'{fragment_dir}/{dataset}.py','w') as fragment_file:
            fragment_file.write(get_fragment(gridpack_dict[dataset]))
            
        for iJob in range(args.nJob):
            
            with open(f'{run_dir}/mc_generation_job_{str(job_id)}.sh','w') as bash_file:
                bash_file.write(get_shell_script(dataset, args.nEvent , f'{fragment_dir}/{dataset}.py', job_id))
            
            job_id+=1
    
    
    with open(f'{run_dir}/mc_generation_jobs.submit','w') as file_out:
        file_out.write(get_condor_submit_file(run_dir, job_id))

    with open(f'{run_dir}/find.sh','w') as file_out:
        file_out.write(get_find_script(output_dir, list(gridpack_dict.keys()), job_id))

    os.system(f'chmod u+x {run_dir}/*.sh')

    print(f'\nGeneration is ready to be submitted comprising {len(list(gridpack_dict.keys()))} sample(s) with {args.nJob*args.nEvent} event(s) each, total number of jobs is {job_id} ...\n')

if __name__ == "__main__":
    main()
## how am i 
