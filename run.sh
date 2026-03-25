cd /home/tutorcenter/Tutor-Display 
git pull 
rclone sync Box:/Engineering Tutoring Center/Schedule.xlsx ./data
rclone sync Box:'/Engineering Tutoring Center/Pictures For Display' ./Images
/home/tutorcenter/Tutor-Display/venv/bin/python src/main.py > ERRORLOG.txt
echo -e '\nThe system crashed'
while true; do
	sleep 1
done
