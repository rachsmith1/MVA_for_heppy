from MVA_tools import *

sigTreeList = [
			'pp_Zprime_10TeV_ttbar',
]

bkgTreeList = [
                        'pp_tt_M_5000_10000',
			'pp_tt_M_10000_15000',
]

discriList  = [
			'numberOfFatJets',
	                'Jet3_pt',
        	        'Jet4_pt',
                	'rapiditySeparation',
	                'transverseMomentumAsymmetry',
]

analysisType = 'FCChhAnalyses.Zprime_tt'
heppyTreePath = '/eos/user/r/rasmith/fcc_v01/Zprime_tt/allHadronic'
cut = 'Jet1_pt > 2800. && Jet2_pt > 2800. && abs(Jet1_eta) < 3. && abs(Jet2_eta) < 3.'
events = 300000
num = 4000
MVAmethod = 'BDT' 

name = 'ttbar'
heppyFolder = '/afs/cern.ch/user/r/rasmith/fcc/heppy/FCChhAnalyses/Zprime_tt'

trainMVA(sigTreeList, bkgTreeList, discriList, heppyTreePath, analysisType, num, events, cut, MVAmethod, name)
heppyMVA(name, heppyFolder)
