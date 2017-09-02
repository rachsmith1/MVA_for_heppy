from __future__ import division
import ROOT
from ROOT import *
from array import array
import subprocess, glob, optparse, json, ast, os, sys, collections
import os.path
import math

def trainMVA(sigTreeList, bkgTreeList, discriList, heppyTreePath, analysisType, num, events, cut, MVAmethod, name):
	
	MVA_fileName = "MVA_{}.root".format(name)
	file_MVA = TFile(MVA_fileName,"recreate")
	print "Will write MVA info in ", MVA_fileName

	factory = TMVA.Factory(MVAmethod, file_MVA)
	dataloader = TMVA.DataLoader()

	for discriVar in discriList :
	        dataloader.AddVariable(discriVar)	

	for sigTree in sigTreeList:
		sig_file = TFile("{}/{}/heppy.{}.TreeProducer.TreeProducer_1/tree.root".format(heppyTreePath, sigTree, analysisType))
		sig_tree = sig_file.Get("events")
		
		sig_slimname = "{}_{}".format(events, sigTree)
		my_file = "slim_files/slim_{}.root".format(sig_slimname)
        	if not(os.path.exists(my_file)):
                	print "slim_{}.root does not exist!".format(sig_slimname)
                	sig_save = TFile("slim_files/slim_{}.root".format(sig_slimname),"recreate")
			sig_save.cd()
			sig_slim = sig_tree.CloneTree(0)
				
			nentries = 0
			if sig_tree.GetEntries() < events: 
				nentries = sig_tree.GetEntries()
			else: 
				nentries = events
			for entry in xrange(nentries) :
				if entry%1000==0: print "... {}: {}/{} ...".format(sigTree, entry, nentries)
				sig_tree.GetEntry(entry)
				sig_slim.Fill()
			sig_slim.SetName("sig")
			sig_save.Write()
			sig_save.Close()

		sig_chain = TChain()
        	sig_chain.Add("slim_files/slim_{}.root/sig".format(sig_slimname))
	        dataloader.AddSignalTree(sig_chain, 1)

	for bkgTree in bkgTreeList:
                bkg_file = TFile("{}/{}/heppy.{}.TreeProducer.TreeProducer_1/tree.root".format(heppyTreePath, bkgTree, analysisType))
                bkg_tree = bkg_file.Get("events")

                bkg_slimname = "{}_{}".format(events, bkgTree)
                my_file = "slim_files/slim_{}.root".format(bkg_slimname)
                if not(os.path.exists(my_file)):
                        print "slim_{}.root does not exist!".format(bkg_slimname)
                        bkg_save = TFile("slim_files/slim_{}.root".format(bkg_slimname),"recreate")
                        bkg_save.cd()
                        bkg_slim = bkg_tree.CloneTree(0)

                        nentries = 0
                        if bkg_tree.GetEntries() < events:
                                nentries = bkg_tree.GetEntries()
                        else:
                                nentries = events
                        for entry in xrange(nentries) :
                                if entry%1000==0: print "... {}: {}/{} ...".format(bkgTree, entry, nentries)
                                bkg_tree.GetEntry(entry)
                                bkg_slim.Fill()
                        bkg_slim.SetName("bkg")
                        bkg_save.Write()
                        bkg_save.Close()

                bkg_chain = TChain()
                bkg_chain.Add("slim_files/slim_{}.root/bkg".format(bkg_slimname))
                dataloader.AddBackgroundTree(bkg_chain, 1)		

	sigcut = cut
	for discri in discriList:
        	sigcut += " && {} >= 0".format(discri)
    	bkgcut = sigcut

	dataloader.PrepareTrainingAndTestTree( TCut( sigcut ), TCut( bkgcut ),
                                            ":".join([ "nTrain_Signal={}".format(num),     # Number of signal events used, 0 = ALL
                                                       "nTrain_Background={}".format(num), # Number of background events, 0 = ALL
                                                       "nTest_Signal={}".format(num),      # Number of signal events used, 0 = ALL
                                                       "nTest_Background={}".format(num),  # Number of background events, 0 = ALL
                                                       "SplitMode=Random",    # How are events chosen to be used for either training or testing
                                                       "NormMode=NumEvents",  # Integral of datasets is given by number of events
                                                                              #   (could e.g. also be sum of weights or simply defined to be 1)
                                                       "!V"                   # Don't print everything (i.e. not verbose)
                                                       ]))

	if MVAmethod == "BDT":
        	method = factory.BookMethod(dataloader, TMVA.Types.kBDT, name,"!H:!V:NTrees=2000:MinNodeSize=0.05:MaxDepth=6:BoostType=AdaBoost:AdaBoostBeta=0.5:UseBaggedBoost:BaggedSampleFraction=0.5:SeparationType=GiniIndex:nCuts=20")

	factory.TrainAllMethods()
	factory.TestAllMethods()
	factory.EvaluateAllMethods()
	file_MVA.Close()

	os.system('mv default {}'.format(name))
			
		

def heppyMVA(name, heppyFolder):
	
	os.system('cp {}/weights/BDT_{}.class.C {}'.format(name, name, heppyFolder))
	cwd = os.getcwd()
	os.chdir('{}'.format(heppyFolder))

	print os.getcwd()

	fpyname = 'compile.py'
	fpy = open(fpyname, 'w')
        fpy.write('import ROOT as r\n')
	fpy.write('r.gROOT.ProcessLine(".L {}/BDT_{}.class.C+")\n'.format(heppyFolder,name))

	subprocess.Popen("python compile.py", shell=True)
	
	os.chdir('{}'.format(cwd))

	print 'Add the following line to the beginning of TreeProducer:'
	print 'ROOT.gROOT.ProcessLine(".L {}/BDT_{}.class.C+")'.format(heppyFolder,name)
	print 'and'
	print 'mva = ROOT.Read{}(inputs)'.format(name)
	
	
