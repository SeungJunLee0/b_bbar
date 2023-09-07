import os, glob

width_title = ["0_80em","0_90em","1_00em","1_10em","1_20em","1_30em", "1_32em", "1_40em", "1_50em","1_60em","1_70em","1_80em"]
#                 0        1        2         3       4       5         6        7         8         9       10        11
width  = width_title[1]

print(width)
print(width)
print(width)



all_folder = glob.glob('/u/user/seungjun/SE_UserHome/root/'+width+'/*.root')
all_file = [x for x in all_folder if os.path.isfile(x)]

int_num = []

for file_name in all_file:
    file_new = file_name[-8:-5].replace(" ","")
    int_num.append(int(file_new))
int_num.sort()
#print(int_num)


int_no = []
for i in range(0,161):
    if i not in int_num:
        int_no.append(i)
        #print(i)
print(int_no)



for i in int_no:
    num = str(i)
    command_line = "rm -rf /u/user/seungjun/scratch/b_bbar/run/HTCondor_run/mc_generation_job_"+num+".sh"
    #print(command_line)
    os.system(command_line)


all_folder = glob.glob('/u/user/seungjun/scratch/b_bbar/run/HTCondor_run/mc*.sh')
all_file = [x for x in all_folder if os.path.isfile(x)]
for i in all_file:
    file_new = i.replace(" ","")
    file_new1 = "."+file_new
    os.chdir("/u/user/seungjun/scratch/b_bbar/run/HTCondor_run/")
    #print(file_new1[50:])
    run_name = "./"+file_new1[50:]
    os.system(run_name)

all_folder = glob.glob('/u/user/seungjun/scratch/b_bbar/run/HTCondor_run/MC*.sh')
all_file = [x for x in all_folder if os.path.isfile(x)]
for i in all_file:
    file_new = i.replace(" ","")
    os.chdir("/u/user/seungjun/scratch/b_bbar/run/HTCondor_run/")
    #print(file_new1[50:])
    print(file_new[70:-3])
    int_num = int(file_new[70:-3])
    if int_num<10:
        command_line = "mv "+ i + " MC_Generation_Script_00" + str(int_num)+".sh"
        print(command_line)
        os.system(command_line)
    if int_num>=10 and int_num <100:
        command_line = "mv "+ i + " MC_Generation_Script_0" + str(int_num)+".sh"
        print(command_line)
        os.system(command_line)
    #os.system(run_name)

os.chdir("/u/user/seungjun/scratch/b_bbar/run/HTCondor_run/")
all_folder = glob.glob('MC*.sh')
all_file = [x for x in all_folder if os.path.isfile(x)]
for i,n in enumerate(all_file):
   new_name = "MC_Generation_Script_"+str(i)+".sh" 
   command_line = "mv " + n + " " + new_name
   #print(command_line)
   os.system(command_line)
print(len(all_file))
