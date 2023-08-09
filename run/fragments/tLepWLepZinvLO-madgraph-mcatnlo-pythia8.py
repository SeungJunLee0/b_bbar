import FWCore.ParameterSet.Config as cms
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
ProductionFilterSequence = cms.Sequence(generator)