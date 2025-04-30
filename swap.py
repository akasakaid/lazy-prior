import os
import sys
import time
import requests
from web3 import Web3, Account, HTTPProvider
from datetime import datetime, timezone
from colorama import Fore, Style

red = Fore.LIGHTRED_EX
green = Fore.LIGHTGREEN_EX
yellow = Fore.LIGHTYELLOW_EX
reset = Style.RESET_ALL
white = Fore.LIGHTWHITE_EX
black = Fore.LIGHTBLACK_EX
blue = Fore.LIGHTBLUE_EX

RPC = "https://sepolia.base.org"
ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "priorAmount", "type": "uint256"}
        ],
        "name": "calculatePriorToUsdc",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "usdcAmount", "type": "uint256"}
        ],
        "name": "calculateUsdcToPrior",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getTokenABalance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getTokenBBalance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "priorAmount", "type": "uint256"}
        ],
        "name": "swapPriorToUsdc",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "usdcAmount", "type": "uint256"}
        ],
        "name": "swapUsdcToPrior",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "amount", "type": "uint256"},
        ],
        "name": "Transfer",
        "type": "event",
    },
    {
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]
PRIOR_CONTRACT = Web3.to_checksum_address("0xefc91c5a51e8533282486fa2601dffe0a0b16edb")
USDC_CONTRACT = Web3.to_checksum_address("0xdB07b0b4E88D9D5A79A08E91fEE20Bb41f9989a2")
ROUTER_ADDRESS = Web3.to_checksum_address("0x8957e1988905311EE249e679a29fc9deCEd4D910")
FAUCET_ADDRESS = Web3.to_checksum_address("0xa206dC56F1A56a03aEa0fCBB7c7A62b5bE1Fe419")
MAX_SWAP_PERDAY = 5
HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Content-Length": "186",
    "Content-Type": "application/json",
    "Host": "priortestnet.xyz",
    "Origin": "https://priortestnet.xyz",
    "Referer": "https://priortestnet.xyz/swap",
    "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
}


def log(msg):
    now = datetime.now().isoformat(" ").split(".")[0]
    print(f"{black}[{now}] {reset}{msg}{reset}")


def submit(address, amount, _from, _to, tx_hash):
    try:
        ses = requests.Session()
        submit_data = {
            "address": address,
            "amount": str(amount),
            "tokenFrom": _from,
            "tokenTo": _to,
            "txHash": tx_hash,
        }
        ses.headers.update(HEADERS)
        res = ses.post("https://priortestnet.xyz/api/swap", json=submit_data)
        success = res.json().get("success")
        if success:
            daily_swap = res.json().get("user", {}).get("dailySwaps")
            log(f"{green}success {white}submit swap data !")
            return daily_swap
        else:
            log(f"{red}failed {white}submit swap data !")
            return False
    except:
        log(f"{red}failed {white}submit swap data !")


def claim_faucet(wallet):
    log(f"{yellow}try to claim faucet !")
    ABI_FAUCET = [
        {
            "inputs": [],
            "name": "claim",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function",
        },
        {
            "inputs": [{"internalType": "address", "name": "", "type": "address"}],
            "name": "lastClaim",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function",
        },
    ]
    try:
        w3 = Web3(HTTPProvider(RPC))
        contract = w3.eth.contract(address=FAUCET_ADDRESS, abi=ABI_FAUCET)
        gas_est = contract.functions.claim().estimate_gas({"from": wallet.address})
        tx = contract.functions.claim().build_transaction({
            "from": wallet.address,
            "gas": gas_est + 20000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(wallet.address, "pending"),
        })
        sign = Account.sign_transaction(tx, wallet.key)
        tx_hash = w3.eth.send_raw_transaction(sign.raw_transaction)
        log(f"{green}tx hash : {white}{tx_hash.to_0x_hex()}")
        ses = requests.Session()
        ses.headers.update(HEADERS)
        res = ses.post(
            "https://priortestnet.xyz/api/faucet/claim",
            json={"address": wallet.address},
        )
        success = res.json().get("success")
        if success:
            log(f"{green}success {white}claim faucet !")
            return True
        else:
            log(f"{red}failed {white}claim faucet !")
            return False
    except KeyboardInterrupt:
        sys.exit()
    except:
        log(f"{red}failed {white}claim faucet !")


def swap(privatekey):
    try:
        ses = requests.Session()
        ses.headers.update(HEADERS)
        w3 = Web3(HTTPProvider(RPC))
        wallet = Account.from_key(privatekey)
        address = wallet.address
        log(f"{green}addr : {white}{address}")
        res = ses.post("https://priortestnet.xyz/api/auth", json={"address": address})
        daily_swap = res.json().get("dailySwaps")
        ts_last_claim_faucet = res.json().get("lastFaucetClaim")
        ts_now = datetime.now(tz=timezone.utc).timestamp()
        if ts_last_claim_faucet is not None:
            ts_last_claim_faucet = datetime.fromisoformat(
                ts_last_claim_faucet.replace("Z", "")
            ).timestamp()
            if (ts_now - ts_last_claim_faucet) > (24 * 3600):
                claim_faucet(wallet)
        if ts_last_claim_faucet is None:
            claim_faucet(wallet)
        while True:
            log(f"{white}total swap today : {green}{daily_swap}")
            if daily_swap >= MAX_SWAP_PERDAY:  # pyright: ignore[reportOptionalOperand]
                log(f"{white}daily swap {yellow}limit reached")
                return
            _eth_balance = w3.eth.get_balance(address)
            balance = Web3.from_wei(_eth_balance, unit="ether")
            log(f"{green}eth balance :{white} {balance}")
            contract = w3.eth.contract(address=USDC_CONTRACT, abi=ABI)
            _usdc_balance = contract.functions.balanceOf(address).call()
            _usdc_decimals = contract.functions.decimals().call()
            usdc_balance = _usdc_balance / (10**_usdc_decimals)
            log(f"{green}usdc balance :{white} {usdc_balance}")
            contract = w3.eth.contract(address=PRIOR_CONTRACT, abi=ABI)
            _prior_balance = contract.functions.balanceOf(address).call()
            _prior_decimals = contract.functions.decimals().call()
            prior_balance = _prior_balance / (10**_prior_decimals)
            log(f"{green}prior balance :{white} {prior_balance}")
            usdc_contract = w3.eth.contract(address=USDC_CONTRACT, abi=ABI)
            usdc_allowance = usdc_contract.functions.allowance(
                address, ROUTER_ADDRESS
            ).call()
            prior_contract = w3.eth.contract(address=PRIOR_CONTRACT, abi=ABI)
            prior_allowance = prior_contract.functions.allowance(
                address, ROUTER_ADDRESS
            ).call()
            if usdc_allowance <= 1000:
                log(f"{yellow}approving {white}usdc contract !")
                gas_est = usdc_contract.functions.approve(
                    ROUTER_ADDRESS, 2**256 - 1
                ).estimate_gas({"from": address})
                tx = usdc_contract.functions.approve(
                    ROUTER_ADDRESS, 2**256 - 1
                ).build_transaction({
                    "from": address,
                    "nonce": w3.eth.get_transaction_count(address, "pending"),
                    "gas": gas_est + 20000,
                    "gasPrice": w3.eth.gas_price,
                })
                sign = Account.sign_transaction(tx, wallet.key)
                # print(sign)
                tx_hash = w3.eth.send_raw_transaction(sign.raw_transaction)
                log(f"{green}tx hash : {white}{tx_hash.to_0x_hex()}")
                time.sleep(5)

            if prior_allowance <= 1000:
                log(f"{yellow}approving {white}prior contract !")
                gas_est = prior_contract.functions.approve(
                    ROUTER_ADDRESS, 2**256 - 1
                ).estimate_gas({"from": address})
                tx = prior_contract.functions.approve(
                    ROUTER_ADDRESS, 2**256 - 1
                ).build_transaction({
                    "from": address,
                    "nonce": w3.eth.get_transaction_count(address, "pending"),
                    "gas": gas_est + 20000,
                    "gasPrice": w3.eth.gas_price,
                })
                sign = Account.sign_transaction(tx, wallet.key)
                tx_hash = w3.eth.send_raw_transaction(sign.raw_transaction)
                log(f"{green}tx hash : {white}{tx_hash.to_0x_hex()}")
                time.sleep(5)
            router = w3.eth.contract(ROUTER_ADDRESS, abi=ABI)
            if prior_balance > 0:
                try:
                    result = router.functions.calculatePriorToUsdc(_prior_balance).call()
                    usdc_ = result / (10**_usdc_decimals)
                    log(f"{green}swap {white}{prior_balance} {blue}PRIOR {green}to {white}{usdc_} {blue}USDC")
                    gas_est = router.functions.swapPriorToUsdc(_prior_balance).estimate_gas({
                        "from": address
                    })
                    tx = router.functions.swapPriorToUsdc(_prior_balance).build_transaction({
                        "from": address,
                        "nonce": w3.eth.get_transaction_count(address, "pending"),
                        "gas": gas_est + 20000,
                        "gasPrice": w3.eth.gas_price,
                    })
                    sign = Account.sign_transaction(tx, wallet.key)
                    tx_hash = w3.eth.send_raw_transaction(sign.raw_transaction)
                    log(f"{green}tx hash : {white}{tx_hash.to_0x_hex()}")
                    result = submit(
                        address=address,
                        amount=prior_balance,
                        _from="PRIOR",
                        _to="USDC",
                        tx_hash=tx_hash.to_0x_hex(),
                    )
                    if result is False:
                        continue
                    daily_swap = result
                    time.sleep(5)
                    continue
                except Exception as e:
                    log(f"{red}error : {white}{e}")
            if usdc_balance > 0:
                try:
                    result = router.functions.calculateUsdcToPrior(_usdc_balance).call()
                    prior_ = result / (10**_prior_decimals)
                    log(f"{green}swap {white}{usdc_balance} {blue}USDC {green}to {white}{prior_} {blue}PRIOR")
                    gas_est = router.functions.swapUsdcToPrior(_usdc_balance).estimate_gas({
                        "from": address
                    })
                    tx = router.functions.swapUsdcToPrior(_usdc_balance).build_transaction({
                        "from": address,
                        "nonce": w3.eth.get_transaction_count(address, "pending"),
                        "gas": gas_est + 20000,
                        "gasPrice": w3.eth.gas_price,
                    })
                    sign = Account.sign_transaction(tx, wallet.key)
                    tx_hash = w3.eth.send_raw_transaction(sign.raw_transaction)
                    log(f"{green}tx hash : {white}{tx_hash.to_0x_hex()}")
                    result = submit(
                        address=address,
                        amount=usdc_balance,
                        _from="USDC",
                        _to="PRIOR",
                        tx_hash=tx_hash.to_0x_hex(),
                    )
                    if result is False:
                        continue
                    daily_swap = result
                    time.sleep(5)
                    continue
                except Exception as e:
                    log(f"{red}error : {white}{e}")
                    continue
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        log(f"{red}error : {white}{e}")


def main():
    os.system("cls" if os.name == "nt" else "clear")
    print(f"""{white}
>
> lazy-prior
> auto swap for prior testnet
> join t.me/sdsproject
> dwyor !
>
        """)
    privatekeys = open("privatekeys.txt").read().splitlines()
    print(f"{green}total privatekey : {white}{len(privatekeys)}")
    print()
    for n, privatekey in enumerate(privatekeys):
        print(f"{white}~" * 50)
        if len(privatekey) < 66:
            log(f"{white}privatekey line : {red}{n + 1} is invalid !")
            continue
        swap(privatekey=privatekey)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
