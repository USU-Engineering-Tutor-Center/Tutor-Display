cd /home/tutorcenter/Tutor-Display 
git pull 
rclone sync Box:/General/Schedule.xlsx ./
rclone sync Box:'/General/Pictures For Display' ./Images
/home/tutorcenter/Tutor-Display/venv/bin/python src/main.py
echo -e '\nThe system crashed'
while true; do
	sleep 1
done
