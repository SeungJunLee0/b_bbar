import os, glob

width_title = ["0_80em","0_90em","1_00em","1_10em","1_20em","1_30em", "1_32em", "1_40em", "1_50em","1_60em","1_70em","1_80em"]
#                 0        1        2         3       4       5         6        7         8         9       10        11
width  = width_title[1]



all_folder = glob.glob('/u/user/seungjun/SE_UserHome/root/'+width+'/*.root')
all_file = [x for x in all_folder if os.path.isfile(x)]

int_num = []

for file_name in all_file:
    file_new = file_name[-8:-5].replace(" ","")
    int_num.append(int(file_new))
int_num.sort()
#print(int_num)


int_no = []
for i in range(1,161):
    if i not in int_num:
        int_no.append(i)
        #print(i)
print(int_no)



for i in int_no:
    num = str(i)
    command_line = "rm -rf /u/user/seungjun/scratch/b_bbar/run/HTCondor_run/mc_generation_job_"+num+".sh"
    #print(command_line)
    os.system(command_line)

