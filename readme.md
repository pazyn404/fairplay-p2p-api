# About project

The main idea of the project was to implement p2p system that assure
provable actions so that all parties(in my case system, host, player)
were protected from being misled by other parties which achieved by digital signatures.
The games theme was chosen because of different games can have different
rules so it was interesting for me to implement a flexible architecture to support any of them
via a common interface. But there is still one flaw if invalid signature was achieved
for example by host from system host can't prove that system is malformed cause http traffic is not public
but anyway previous actions history remains valid. To solve previously described problem 
blockchain as message broker can be used since it's publicly available it also implies that you don't need a public ip
since you just need to send message and crawl blockchain for the response.
Possible blockchain for this purpose is Constellation(DAG) 
as far as I understand it allows fast transactions, support messages and has
DAG structure that allows to crawl messages much easier and faster(should be tested in practice).

# How to run

* ## Windows
* Init
```
git clone https://github.com/pazyn404/fairplay-p2p-api.git
cd fairplay-p2p-api
mkdir system\keys
mkdir host\keys
mkdir player\keys
python -m venv venv
.\venv\Scripts\activate
python -m pip install -r requirements.txt
cd tools
python init.py
cd ..
```
* Run system
```
cd system
docker compose --env-file .\dev\.env up
```
* Run host
```
cd host
docker compose --env-file .\dev\.env up
```
* ## Linux, MacOS
* Init
```
git clone https://github.com/pazyn404/fairplay-p2p-api.git
cd fairplay-p2p-api
mkdir system/keys host/keys player/keys
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
cd tools
python3 init.py
cd ..
```
* Run system
```
cd system
docker compose --env-file ./dev/.env up
```
* Run host
```
cd host
docker compose --env-file ./dev/.env up
```

# How to format payload

* To format payload tools/payload_formatter.py should be used like:
* python payload_formatter.py who(host_user, player) id next_action_number
* python payload_formatter.py host_user 1 2
* python payload_formatter.py player 2 0
