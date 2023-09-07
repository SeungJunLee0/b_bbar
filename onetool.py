import os, glob

width_title = ["0_80em","0_90em","1_00em","1_10em","1_20em","1_30em", "1_32em", "1_40em", "1_50em","1_60em","1_70em","1_80em"]
#                 0        1        2         3       4       5         6        7         8         9       10        11
width  = width_title[1]



all_folder = glob.glob('/u/user/seungjun/SE_UserHome/lhe/'+width+'/*.lhe')
all_file = [x for x in all_folder if os.path.isfile(x)]
for file_name in all_file:
    file_new = file_name[-7:-4].replace(" ","")
    output = " /u/user/seungjun/SE_UserHome/root/0_90em/lhe_"+file_new+".root "
    command_line="cmsRun lhe_to_edm.py "+file_name+" /u/user/seungjun/SE_UserHome/root/0_90em/lhe_"+file_new+".root "
    print(command_line)
    os.system(command_line)
