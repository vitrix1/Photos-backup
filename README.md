# Photos-backup
The script performs the backup feature photos of VK on Yandex disk, either on Google drive.  
## For the script to work, you will need:
- install the shutil, tqdm, json, requests, datetime, google-api-python-client libraries  
- to work with VK:  
1. get a token  
2. save it to a file named vk_token.txt to the folder with the script  
3. the number of copied photos is specified in count (line 15)  
4. you can specify from which album the profile, wall and saved photos will be copied (line 15)  
- when working with Yandex Disk:  
1. get a token  
2. save it to a file named ya_token.txt to the folder with the script  
After the script is running, a folder with the VK user id will be automatically created,
in which the saved photos will be  
- when working with Google Disc:  
1. сreate a service account  
2. get the key in json format  
3. specify the path to the file in self.SERVICE_ACCOUNT_FILE (line 77)  
4. create a folder for uploading photos from VK to Google Disk  
5. grant access to your created service account for it  
6. go to the folder and copy the folder id from the address bar  
7. specify the id in self.folder_id (line 78)  

## The script works according to the following algorithm:  
1. a temporary folder tmp_dir is created  
2. a request is made for the VK token and data about the photo is downloaded  
### If the algorithm uses Yandex:  
3. a remote folder is created with the name of the VK user ID and photos are uploaded there via the link  
4. to avoid duplicate names, a request is made for all files in the folder and a match is checked  
### If the algorithm uses Google:  
3. photos are downloaded to tmp_dir  
4. name matches in tmp_dir are checked, if there are none,  
the photo is uploaded to a remote folder without name changes,  
if vice versa, the date is added to the file name.  

**THAT IS, THE UNIQUENESS OF THE NAME IS CHECKED ONLY IN ONE SESSION OF UPLOADING PHOTOS TO DISK.**  

*The script is run with the arguments: <VK_person_id> <y/g>*  
At the end of the script, the result.json file will be created.  
