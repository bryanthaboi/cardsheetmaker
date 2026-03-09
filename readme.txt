Windows

python -m venv venv
./venv/Scripts/activate 
pip install -r requirements.txt
python sprite.py
deactivate


Mac

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install Pillow
python3 sprite.py
deactivate