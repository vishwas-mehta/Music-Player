
if [ -d '.env' ];
then
    echo '___________.env already exist. lets run app___________'
    source .env/bin/activate
else
    echo '.env not exist. so lets install py env'
    python3 -m venv .env
    source .env/bin/activate
    pip3 install -r req.txt
fi


# rm instance/db.sqlite3
# python3 init.py

python3 main.py

deactivate
echo 'DEACTIVATED'