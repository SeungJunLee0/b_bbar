#!/bin/sh

#  @1  -->  "resubmit" for resubmition

find /afs/cern.ch/user/s/seungjun/private/b_bbar/out/tLepWLepZinvLO-madgraph-mcatnlo-pythia8 -name "*.root" > find_tmp

array=()
n_miss_job=0
for j in {0..0}
do
if ! grep -q "_"${j}".root" find_tmp
then
    array+=(${j})
    let n_miss_job++
fi
done

echo ""
echo "The number of missing files is: "${n_miss_job}
echo ""
echo "The jobs failed are: ${array[@]}"
echo ""


if [ "${1}" = "resubmit" ]
then
    [ -d resubmit ] && rm -rf resubmit
    mkdir resubmit
    n_sub_job=0
    for j in ${array[@]}
    do
        cp mc_generation_job_${j}.sh resubmit/mc_generation_job_${n_sub_job}.sh
        let n_sub_job++
    done
    cd resubmit
    cp ../mc_generation_jobs.submit .
    sed -i 's|HTCondor_run|HTCondor_run/resubmit|g' mc_generation_jobs.submit
    sed -i 's|1|'${n_sub_job}'|g' mc_generation_jobs.submit
    cd ../


    echo "Jobs ready to be re-submitted in 'resubmit' directory ... "
fi

echo ""

rm find_tmp

echo "done."

echo ""
