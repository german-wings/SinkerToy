import filecmp
import os


import os
import shutil
from threading import local


sink_from = r"C:\Users\GermanWings\OneDrive\Exports"
sink_from = os.path.normpath(sink_from)
sink_to = os.path.join(os.getcwd(),"dds-master")

def copy_master():
    for root , directory , files in os.walk(sink_from):
        for file in files:
            target_remote_file_path = os.path.join(root , file)
            stripped_remote_path = target_remote_file_path.split(sink_from+"\\")[1]
            possible_local_path = os.path.join(sink_to , stripped_remote_path)
            if(not os.path.exists(possible_local_path)):
                copy_to_dirname = os.path.dirname(possible_local_path)
                if(os.path.isdir(copy_to_dirname) == False):
                    os.makedirs(os.path.normpath(copy_to_dirname))
                shutil.copy2(target_remote_file_path , copy_to_dirname)
                print(f"Copyying...{os.path.basename(target_remote_file_path)} to {os.path.dirname(possible_local_path)}")
            elif(os.path.exists(possible_local_path)):
                #compare two files
                print(f"Comparing .. {os.path.basename(possible_local_path)} Remote {os.path.basename(target_remote_file_path)}")
                filecmp.clear_cache()
                if(filecmp.cmp(possible_local_path , target_remote_file_path)==False):
                    print("Downloading again...."+os.path.basename(possible_local_path))
                    shutil.copy2(target_remote_file_path , possible_local_path)


def delete_master():
    for root , dirs , files in os.walk(sink_to):
        for file in files:
            local_path = os.path.join(root , file)
            stripped_local_path = local_path.split(sink_to+"\\")[1]
            possible_global_path = os.path.join(sink_from , stripped_local_path)
            if(not os.path.exists(possible_global_path)):
                os.remove(local_path)
        
        for dir in dirs:
            possible_empty_dir = os.listdir(os.path.join(root,dir))
            if(len(possible_empty_dir) == 0):
                os.rmdir(os.path.join(root , dir))

delete_master()
copy_master()